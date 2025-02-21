from typing import Any, Literal, Optional, Tuple, Union
from enum import Enum
import sqlglot
from sqlglot import exp, errors as sqlglot_errors
from dataclasses import dataclass, field


@dataclass
class RoleTablePrivileges:
    """
    Defines the privilages that a role has for a table

    Attributes:
        id: Unique identifier for the privilage entry
        role_id: id of the role that owns the privilages
        table: name of the table which the privilages apply to
        columns: list of columns within the table that the role has access to
        scoped_columns: list of columns that define row level restrictions. The role can only access rows where the column satisfies the scoping restrictions
    """

    role_id: str
    table: str
    columns: list[str]
    scoped_columns: list[str]


ComparisionOperator = Literal[
    "=",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "IN",
    "NOT IN",
    "IS",
    "IS NOT",
    "LIKE",
    "NOT LIKE",
]


@dataclass
class ColumnScope:
    """
    Represents a scope for a column in a table.
    A scope is a restriction on the column that must be satisfied for a query to be allowed.

    Attributes:
        table: Name of the table
        column: Name of the column
        operator: The operator symbol to be used for the comparison. Can be one of "=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "IS", "IS NOT", "LIKE", "NOT LIKE"
        value: The value to be compared against
        value_type: The type of the value. Can be one of "string", "literal", "list", "string_array", "null"
    """

    table: str
    column: str
    value: Union[str, list[str], None] = field(default=None)
    operator: ComparisionOperator = field(default="=")
    value_type: Literal["string", "literal", "list", "string_array", "null"] = field(
        default="literal"
    )


class ErrorCode(Enum):
    """
    This Enum represents the various error codes that can be returned when checking for privileges.
    """

    INVALID_SQL_QUERY = "The provided SQL query is invalid."
    CTE_ERROR = "The provided CTE is either invalid, not supported or is not allowed for the role."
    SUBQUERY_ERROR = (
        "The subquery is either invalid, not supported or is not allowed for the role."
    )
    MISSING_TABLE_NAME_PREFIX = "The provided SQL query is not supported."
    TABLE_NOT_IN_PRIVILAGES = "The specified table is not found in the privileges map."
    ROLE_NO_TABLE_ACCESS = "The role does not have access to the specified table."
    ROLE_NO_COLUMN_ACCESS = "The role does not have access to the specified column."
    ROLE_NO_ROWS_ACCESS = "The query is trying to access rows which don't"
    WILDCARD_STAR_NOT_ALLOWED = "The wildcard star is not allowed."


@dataclass
class PrivilageCheckResult:
    """
    Represents the result of a privilage check for an SQL query

    Attributes:
        query_allowed: Weather or not a query is allowed for the role
        err_code: ErrorCode for when the query is not allowed
        context: Additional context about the check, and the reason for the check result
    """

    query_allowed: bool
    err_code: Optional[ErrorCode] = field(default=None)
    context: Optional[dict[str, Any]] = field(default=None)


def check_table_privilages_for_role(
    table: exp.Table,
    table_privilages_map: dict[str, list[RoleTablePrivileges]],
    role_id: str,
) -> Tuple[Optional[RoleTablePrivileges], Optional[PrivilageCheckResult]]:
    """
    Check if the table meets the user's privilages

    Args:
        table: The table expression that has to be checked for privilages
        table_privilages_map: List of privilages for the role
        role_id:

    Returns: A tuple of RoleTablePrivileges
    """
    if table.name not in table_privilages_map:
        return (
            None,
            PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.TABLE_NOT_IN_PRIVILAGES,
                context={"table": table.name, "role": role_id},
            ),
        )

    privilages_for_role = None
    table_privilages = table_privilages_map[table.name]
    for privilage in table_privilages:
        if privilage.role_id == role_id:
            privilages_for_role = privilage
            break

    if privilages_for_role is None:
        return (
            None,
            PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_TABLE_ACCESS,
                context={"table": table.name, "role": role_id},
            ),
        )

    return (privilages_for_role, None)


def match_operator_to_exp(operator: str) -> tuple[exp._Expression, bool]:
    """
    Match the operator symbol to the metaclass representing the operator in the AST

    Args:
        operator: symbol representing the operator

    Raises:
        ValueError: If the operator is invalid or not supported

    Returns:
        If the operator is valid, returns a tuple of the operator and a boolean representing if the operator is negated

    """
    match operator:
        case "=":
            return exp.EQ, False
        case "!=":
            return exp.NEQ, False
        case ">":
            return exp.GT, False
        case "<":
            return exp.LT, False
        case ">=":
            return exp.GTE, False
        case "<=":
            return exp.LTE, False
        case "IN":
            return exp.In, False
        case "NOT IN":
            return exp.In, True
        case "IS":
            return exp.Is, False
        case "IS NOT":
            return exp.Is, True
        case "LIKE":
            return exp.Like, False
        case "NOT LIKE":
            return exp.Like, True

    raise ValueError(f"Invalid / Unsupported operator - {operator}")


def invert_comparision_direction(comparator: exp._Expression) -> exp._Expression:
    """
    Inverts the direction of a comparision operator in the AST.

    Args:
        comparator: Metaclass representing the comparision operator in the AST

    Returns: The inverted comparision operator if it is invertible, else returns the same operator
    """
    mappings = {exp.GT: exp.LT, exp.LT: exp.GT, exp.LTE: exp.GTE, exp.GTE: exp.LTE}
    return mappings.get(comparator, comparator)


def check_expression_matches_scope(
    column_scope: ColumnScope, operator: exp.Expression
) -> bool:
    """
    Check if the operator rooted subtree matches the required column scope

    Args:
        column_scope: Scope that needs to be checked
        operator: The node representing the operator within the AST

    Returns:
        True if the column, operator, value and value_type of the scope match the operator expression
    """
    # Get the column and value from the operator expressions in the AST
    column: exp.Column
    value: exp.Expression
    is_comparision_negated = False
    comparision_operator: exp.Expression = operator

    # expected operator information extracted from the column scope
    expected_operator, expected_negation = match_operator_to_exp(column_scope.operator)

    # Handle queries with NOT operator
    if isinstance(operator, exp.Not):
        comparision_operator = operator.this
        is_comparision_negated = True

    # Extract the column and value from the AST node
    if isinstance(comparision_operator.this, exp.Column):
        column = comparision_operator.this
        value = comparision_operator.expression
    else:
        column = comparision_operator.expression
        value = comparision_operator.this
        expected_operator = invert_comparision_direction(expected_operator)

    # Check if the actual values for the operator match the values in the column scope
    is_comparision_value_matches = False
    if isinstance(comparision_operator, exp.In):
        assert column_scope.value_type == "list" and isinstance(
            column_scope.value, list
        ), "Value type must always be list for IN operators"

        expetced_values = set(column_scope.value)
        actual_values = set([val.this for val in comparision_operator.expressions])
        missing_values = expetced_values - actual_values

        is_comparision_value_matches = len(missing_values) == 0
    else:
        is_comparision_value_matches = column_scope.value == value.this

    is_column_matches = column_scope.column == column.name
    is_negation_matches = is_comparision_negated == expected_negation
    operator_type_matches = isinstance(comparision_operator, expected_operator)

    # Check if the value type matches the expected value type
    is_value_type_matches = False
    match column_scope.value_type:
        case "string":
            is_value_type_matches = value.is_string
        case "list":
            is_value_type_matches = len(comparision_operator.expressions) > 0
        case "string_array":
            if len(comparision_operator.expressions) > 0:
                is_string_array = all(
                    [val.is_string for val in comparision_operator.expressions]
                )
                is_value_type_matches = is_string_array
            else:
                is_value_type_matches = False
        case "literal":
            is_value_type_matches = value.is_string == False
        case "null":
            is_value_type_matches = isinstance(value, exp.Null)

    is_expression_matches_scope = (
        is_column_matches
        and is_negation_matches
        and operator_type_matches
        and is_comparision_value_matches
        and is_value_type_matches
    )

    return is_expression_matches_scope


def check_scope_privilages(
    reference_table: exp.Table,
    column_scopes: list[ColumnScope] = [],
    alias_table_map: dict[str, str] = {},
) -> PrivilageCheckResult:
    """
    This function checks if the scopes for a given table is satisfied.

    Args:
        reference_table: Table for which scope requirement need to be verified
        column_scopes: List of all the scopes that are applicable to the table
        alias_table_map: Dictionary containing the mappings between table aliases to actual table names

    Returns:
        PrivilageCheckResult representing weather or not the required scopes are present for the table
    """
    select_query = reference_table.find_ancestor(exp.Select)
    assert select_query is not None

    where_clauses = list(select_query.find_all(exp.Where))
    if len(where_clauses) == 0 and len(column_scopes) > 0:
        return PrivilageCheckResult(
            query_allowed=False,
            err_code=ErrorCode.ROLE_NO_ROWS_ACCESS,
            context={
                "reason": "No where clauses found for table in the query segment",
                "table": reference_table,
                "query_segment": select_query.sql(),
            },
        )

    scoping_expresssions_by_column: dict[str, list[exp.Expression]] = {}
    prune_or_subtrees = lambda node: node == exp.Or
    for where_clause in where_clauses:
        expressions = where_clause.dfs(prune_or_subtrees)

        # Identify potential expressions which can satisfy the scopes for the table
        for operator_symbol in expressions:
            is_not_operator = isinstance(operator_symbol, exp.Not)
            is_valid_comparision_predicate = isinstance(operator_symbol, exp.Predicate)
            if not is_not_operator and not is_valid_comparision_predicate:
                continue

            columns = list(operator_symbol.find_all(exp.Column))

            # Comparisions between two columns or two literals won't be considered for scope checks
            if len(columns) != 1:
                continue

            column = columns[0]

            is_valid_table_name_for_column = (
                column.table is not None and column.table != ""
            )
            if not is_valid_table_name_for_column:
                return PrivilageCheckResult(
                    query_allowed=False,
                    err_code=ErrorCode.MISSING_TABLE_NAME_PREFIX,
                    context={
                        "reason": "No table name for column in where clause",
                        "column": column.sql(),
                        "where_clause": where_clause.sql(),
                        "near": column.parent.sql() if column.parent else None,
                    },
                )

            # Get the unaliased table name
            table_name = alias_table_map.get(column.table, column.table)

            if table_name is not reference_table.name:
                continue

            # Initialize index for column in table
            scoping_expresssions_by_column[column.name] = (
                scoping_expresssions_by_column.get(column.name, [])
            )

            scoping_expresssions_by_column[column.name].append(operator_symbol)

    for column_scope in column_scopes:
        scoping_expressions = scoping_expresssions_by_column.get(column_scope.column)

        if scoping_expressions is None:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_ROWS_ACCESS,
                context={
                    "reason": "No where clauses found for column in the query segment",
                    "column": column_scope.column,
                    "query_segment": select_query.sql(),
                },
            )

        scope_matched = False
        for operator_expression in scoping_expressions:
            scope_matched = check_expression_matches_scope(
                column_scope, operator_expression
            )
            if scope_matched:
                break

        if not scope_matched:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_ROWS_ACCESS,
                context={
                    "reason": "Column scope is not fulfilled for one of the selects",
                    "scope": column_scope,
                },
            )

    return PrivilageCheckResult(query_allowed=True)


def check_query_privilages(
    table_privilages_map: dict[str, list[RoleTablePrivileges]],
    active_role: str,
    query: str,
    table_scopes: dict[str, list[ColumnScope]] = {},
    allowed_aliases: list[str] = [],
) -> PrivilageCheckResult:
    """
    Given a query and a role, this function checks if the role has access to the tables and columns in the query

    Args:
        table_privilages_map: Dictionary mapping table names to a list of privilages for the table
        roles: List of available roles
        role_id: Id of the current role
        query: SQL query to be checked for privilages
        table_scopes: Dictionary mapping table names to list of ColumnScopes
        allowed_aliases: List of allowed_aliases for CTEs and Subqueries. No checks are performed on columns in these aliases

    Returns: PrivilageCheckResult representing weather or not the query is allowed

    A query is allowed if:
        - The role has access to the table in the query
        - The role has access to the columns in the query

    The following kinds of queries are not not supported:
        - Queries with wildcard stars.
        - Queries that don't have a table name for a column.
        - Invalid SQL Queries

    ```python
    # Queries with wildcard stars are not allowed
    SELECT * FROM employees

    # Queries that don't have a table name for a column are not allowed
    SELECT name FROM employees # This query is rejected
    SELECT employees.name FROM employees # This query is accepted
    ```

    """
    # Try to parse the query
    parsed_query: exp.Expression
    try:
        parsed_query = sqlglot.parse_one(query)
    except sqlglot_errors.ParseError as e:
        return PrivilageCheckResult(
            query_allowed=False,
            err_code=ErrorCode.INVALID_SQL_QUERY,
            context={"error": str(e), "role": active_role, "query": query},
        )

    alias_table_map: dict[str, str] = {}
    table_privilages_for_role: dict[str, RoleTablePrivileges] = {}

    # Check select queries for select all stars
    select_queries = parsed_query.find_all(exp.Select)
    for select_query in select_queries:
        is_wildcard_present = next(
            True if isinstance(expression, exp.Star) else False
            for expression in select_query.expressions
        )

        if is_wildcard_present:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.WILDCARD_STAR_NOT_ALLOWED,
                context={"role": active_role, "query": query},
            )

    # Check eash subquery in the CTEs
    # A cte is allowed if all the subqueries are allowed
    ctes = parsed_query.find_all(exp.CTE)
    valid_query_aliases = allowed_aliases
    for cte in ctes:
        cte_query = next(cte.find_all(exp.Select))
        cte_result = check_query_privilages(
            table_privilages_map, active_role, cte_query.sql(), table_scopes
        )
        if not cte_result.query_allowed:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.CTE_ERROR,
                context={
                    "role": active_role,
                    "query": query,
                    "cte": cte,
                    "cte_result": str(cte_result),
                },
            )

        valid_query_aliases.append(cte.alias)
        alias_table_map[cte.alias] = cte.alias

    # Check each subquery in the subqueries
    subqueries = parsed_query.find_all(exp.Subquery)
    for subquery in subqueries:
        select = next(subquery.find_all(exp.Select))
        subquery_result = check_query_privilages(
            table_privilages_map,
            active_role,
            select.sql(),
            table_scopes,
            valid_query_aliases,
        )

        if not subquery_result.query_allowed:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.SUBQUERY_ERROR,
                context={
                    "role": active_role,
                    "query": query,
                    "subquery": subquery.sql(),
                    "subquery_result": str(subquery_result),
                    "near": subquery.parent.sql() if subquery.parent else None,
                },
            )

        valid_query_aliases.append(subquery.alias)
        alias_table_map[subquery.alias] = subquery.alias

    # Check table privilages for each table in the query
    # This check also checks tables referenced within CTEs
    tables = parsed_query.find_all(exp.Table)
    for table in tables:
        if table.alias:
            alias_table_map[table.alias] = table.name
        else:
            alias_table_map[table.name] = table.name

        if table.name in valid_query_aliases:
            continue

        table_privilages, table_check_result = check_table_privilages_for_role(
            table, table_privilages_map, active_role
        )

        if table_check_result and not table_check_result.query_allowed:
            assert table_check_result.context is not None
            table_check_result.context["query"] = query
            return table_check_result

        assert table_privilages is not None

        # Ensure all hte required scopes are available
        scopes_for_table = table_scopes.get(table.name, [])
        column_scopes_available: set[str] = set()
        for column_scope in scopes_for_table:
            column_scopes_available.add(column_scope.column)

        required_scopes = set(table_privilages.scoped_columns)
        missing_scopes = required_scopes - column_scopes_available
        assert (
            len(missing_scopes) == 0
        ), f"Missing scopes: {missing_scopes} for role '{active_role}' on table '{table.name}'"

        scope_check_result = check_scope_privilages(
            table, scopes_for_table, alias_table_map
        )

        if not scope_check_result.query_allowed:
            assert scope_check_result.context is not None
            scope_check_result.context["table"] = table.name
            scope_check_result.context["query"] = query
            return scope_check_result

        if table_privilages:
            table_privilages_for_role[table.name] = table_privilages

    # Check column privilages for each column in the query
    # This check also checks columns referenced within CTEs
    columns = parsed_query.find_all(exp.Column)
    for column in columns:
        if column.table is None or column.table == "":
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.MISSING_TABLE_NAME_PREFIX,
                context={
                    "role": active_role,
                    "query": query,
                    "reason": "No table name for column",
                    "column": column.sql(),
                    "near": column.parent.sql() if column.parent else None,
                },
            )

        # Get the unaliased table name
        table_name = alias_table_map.get(column.table, column.table)
        if table_name in valid_query_aliases:
            continue

        if table_name not in table_privilages_for_role or active_role == "EXTERNAL_COORDINATOR":
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_TABLE_ACCESS,
                context={"table": table_name, "role": active_role, "query": query},
            )

        table_privilages = table_privilages_for_role[table_name]
        if column.name not in table_privilages.columns:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_COLUMN_ACCESS,
                context={"column": column.name, "role": active_role, "query": query},
            )

    return PrivilageCheckResult(
        query_allowed=True, context={"role": active_role, "query": query}
    )
