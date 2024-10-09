from typing import Any, Dict, List, Literal, Optional, Tuple
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
    columns: List[str]
    columns_to_scope: List[str]

    def __init__(self, id, role_id, table, columns, columns_to_scope) -> None:
        self.id = id
        self.role_id = role_id
        self.table = table
        self.columns = columns
        self.columns_to_scope = columns_to_scope


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
        context: Optional[Dict[str, Any]] = None,
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
    table_privilages_map: dict[str, List[RoleTablePrivileges]],
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


def find_role_by_id(roles: List[Role], role_id: str) -> Optional[Role]:
    """
    This function finds a role by its id in a list of roles.
    """
    for role in roles:
        if role.id == role_id:
            return role
    return


def check_query_privilages(
    table_privilages_map: dict[str, List[RoleTablePrivileges]],
    roles: List[Role],
    role_id: str,
    query: str,
    allowed_aliases: List[str] = [],
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
    parsed_query = None
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

    alias_table_map: Dict[str, str] = {}
    table_privilages_for_role: Dict[str, RoleTablePrivileges] = {}

    # Check eash subquery in the CTEs
    # A cte is allowed if all the subqueries are allowed
    ctes = parsed_query.find_all(exp.CTE)
    valid_query_aliases = allowed_aliases
    for cte in ctes:
        cte_query = list(cte.find_all(exp.Select))[0]
        cte_result = check_query_privilages(
            table_privilages_map, roles, role_id, cte_query.sql()
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

        table_privilages, error = check_table_privilages_for_role(
            table, table_privilages_map, role_id, query
        )

        if error:
            return error

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
