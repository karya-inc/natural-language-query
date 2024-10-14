from typing import Any, Literal, Optional, Tuple, Union
from enum import Enum
import sqlglot
from sqlglot import exp, errors as sqlglot_errors


class Role:
    """
    This class represents a Role in the system. Each role has an id, a description, and a database role.
    """

    def __init__(
        self,
        id: str,
        description: str,
        db_role: str,
    ):
        self.id = id
        self.description = description
        self.db_role = db_role


class RoleTablePrivileges:
    """
    Access control list that defines the tables, columns and scopes a role can access
    """

    id: str
    role_id: str
    table: str
    columns: list[str]
    scoped_columns: list[str]

    def __init__(self, id, role_id, table, columns, scoped_columns) -> None:
        self.id = id
        self.role_id = role_id
        self.table = table
        self.columns = columns
        self.scoped_columns = scoped_columns


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


class ColumnScope:
    """
    This class represents the scopes for a table. It includes the table name and the scopes for the table.
    """

    def __init__(
        self,
        table: str,
        column: str,
        value: Union[str, list[str], None],
        operator: ComparisionOperator = "=",
        value_type: Literal[
            "string", "literal", "list", "string_array", "null"
        ] = "literal",
    ) -> None:
        self.table = table
        self.column = column
        self.operator = operator
        self.value = value
        self.value_type = value_type


class ErrorCode(Enum):
    """
    This Enum represents the various error codes that can be returned when checking for privileges.
    """

    ROLE_NOT_FOUND = "The specified role was not found."
    INVALID_SQL_QUERY = "The provided SQL query is invalid."
    CTE_ERROR = "The provided CTE is either invalid, not supported or is not allowed for the role."
    SUBQUERY_ERROR = (
        "The subquery is either invalid, not supported or is not allowed for the role."
    )
    UNSUPPORTED_SQL_QUERY = "The provided SQL query is not supported."
    TABLE_NOT_IN_PRIVILAGES = "The specified table is not found in the privileges map."
    ROLE_NO_TABLE_ACCESS = "The role does not have access to the specified table."
    ROLE_NO_COLUMN_ACCESS = "The role does not have access to the specified column."
    ROLE_NO_ROWS_ACCESS = "The query is trying to access rows which don't"
    WILDCARD_STAR_NOT_ALLOWED = "The wildcard star is not allowed."


class PrivilageCheckResult:
    """
    This class represents the result of a privilege check. It includes whether the query is allowed, the error code if
    the query is not allowed, and additional context about the check.
    """

    def __init__(
        self,
        query_allowed: bool,
        err_code: Optional[ErrorCode] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.query_allowed = query_allowed
        self.err_code = err_code
        self.context = context or {}

    def __eq__(self, other):
        if isinstance(other, PrivilageCheckResult):
            return (
                self.query_allowed == other.query_allowed
                and self.err_code == other.err_code
                and self.context == other.context
            )
        return False

    def __str__(self):
        return f"PrivilageCheckResult(query_allowed={self.query_allowed}, err_code={self.err_code}, context={self.context})"


def check_table_privilages_for_role(
    table: exp.Table,
    table_privilages_map: dict[str, list[RoleTablePrivileges]],
    role_id: str,
    query: str,
) -> Tuple[Optional[RoleTablePrivileges], Optional[PrivilageCheckResult]]:
    """
    This function checks the privileges for a role on a table. It returns the privileges the role has on the table and
    a PrivilageCheckResult which contains error information.
    """
    if table.name not in table_privilages_map:
        return (
            None,
            PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.TABLE_NOT_IN_PRIVILAGES,
                context={"table": table.name, "role": role_id, "query": query},
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
                context={"table": table.name, "role": role_id, "query": query},
            ),
        )

    return (privilages_for_role, None)


def find_role_by_id(roles: list[Role], role_id: str) -> Optional[Role]:
    """
    This function finds a role by its id in a list of roles.
    """
    for role in roles:
        if role.id == role_id:
            return role
    return


def match_operator_to_exp(operator: str) -> tuple[exp._Expression, bool]:
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
    mappings = {exp.GT: exp.LT, exp.LT: exp.GT, exp.LTE: exp.GTE, exp.GTE: exp.LTE}
    return mappings.get(comparator, comparator)


def check_expression_matches_scope(
    column_scope: ColumnScope, operator: exp.Expression
) -> bool:
    column: exp.Column
    value: exp.Expression

    expected_operator, expected_negation = match_operator_to_exp(column_scope.operator)

    is_comparision_negated = False
    comparision_operator: exp.Expression = operator
    if isinstance(operator, exp.Not):
        comparision_operator = operator.this
        is_comparision_negated = True

    if isinstance(comparision_operator.this, exp.Column):
        column = comparision_operator.this
        value = comparision_operator.expression
    else:
        column = comparision_operator.expression
        value = comparision_operator.this
        expected_operator = invert_comparision_direction(expected_operator)

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
                    err_code=ErrorCode.UNSUPPORTED_SQL_QUERY,
                    context={
                        "reason": "No table name for column in where clause",
                        "column": column.sql(),
                        "where_clause": where_clause.sql(),
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
    roles: list[Role],
    role_id: str,
    query: str,
    table_scopes: dict[str, list[ColumnScope]] = {},
    allowed_aliases: list[str] = [],
) -> PrivilageCheckResult:
    """
    Given a query and a role, this function checks if the role has access to the tables and columns in the query

    A query is allowed if:
        - The role has access to the table in the query
        - The role has access to the columns in the query

    The following kinds of queries are not not supported:
        - Queries with wildcard stars. Eg:
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
    active_role = find_role_by_id(roles, role_id)

    if active_role is None:
        return PrivilageCheckResult(
            query_allowed=False,
            err_code=ErrorCode.ROLE_NOT_FOUND,
            context={"role": role_id, "query": query},
        )

    # Try to parse the query
    parsed_query: exp.Expression
    try:
        parsed_query = sqlglot.parse_one(query)
    except sqlglot_errors.ParseError as e:
        return PrivilageCheckResult(
            query_allowed=False,
            err_code=ErrorCode.INVALID_SQL_QUERY,
            context={"error": str(e), "role": role_id, "query": query},
        )

    # Check if the query contains a wildcard star
    # Such queries are not allowed
    wildcard_exists = parsed_query.find(exp.Star)
    if wildcard_exists:
        return PrivilageCheckResult(
            query_allowed=False,
            err_code=ErrorCode.WILDCARD_STAR_NOT_ALLOWED,
            context={"role": role_id, "query": query},
        )

    alias_table_map: dict[str, str] = {}
    table_privilages_for_role: dict[str, RoleTablePrivileges] = {}

    # Check eash subquery in the CTEs
    # A cte is allowed if all the subqueries are allowed
    ctes = parsed_query.find_all(exp.CTE)
    valid_query_aliases = allowed_aliases
    for cte in ctes:
        cte_query = list(cte.find_all(exp.Select))[0]
        cte_result = check_query_privilages(
            table_privilages_map, roles, role_id, cte_query.sql(), table_scopes
        )
        if not cte_result.query_allowed:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.CTE_ERROR,
                context={
                    "role": role_id,
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
        select = list(subquery.find_all(exp.Select))[0]
        subquery_result = check_query_privilages(
            table_privilages_map,
            roles,
            role_id,
            select.sql(),
            table_scopes,
            valid_query_aliases,
        )

        if not subquery_result.query_allowed:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.SUBQUERY_ERROR,
                context={
                    "role": role_id,
                    "query": query,
                    "subquery": subquery.sql(),
                    "subquery_result": str(subquery_result),
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
            table, table_privilages_map, role_id, query
        )

        if table_check_result and not table_check_result.query_allowed:
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
        ), f"Missing scopes: {missing_scopes} for role '{role_id}' on table '{table.name}'"

        scope_check_result = check_scope_privilages(
            table, scopes_for_table, alias_table_map
        )

        if not scope_check_result.query_allowed:
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
                err_code=ErrorCode.UNSUPPORTED_SQL_QUERY,
                context={
                    "role": role_id,
                    "query": query,
                    "reason": "No table name for column",
                },
            )

        # Get the unaliased table name
        table_name = alias_table_map.get(column.table, column.table)
        if table_name in valid_query_aliases:
            continue

        if table_name not in table_privilages_for_role:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_TABLE_ACCESS,
                context={"table": table_name, "role": role_id, "query": query},
            )

        table_privilages = table_privilages_for_role[table_name]
        if column.name not in table_privilages.columns:
            return PrivilageCheckResult(
                query_allowed=False,
                err_code=ErrorCode.ROLE_NO_COLUMN_ACCESS,
                context={"column": column.name, "role": role_id, "query": query},
            )

    return PrivilageCheckResult(
        query_allowed=True, context={"role": role_id, "query": query}
    )
