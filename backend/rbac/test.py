from check_permissions import ColumnScope, check_query_privilages, Role, RoleTablePrivileges
import unittest


class TestColumnSecurity(unittest.TestCase):

    def setUp(self):
        self.roles = [
            Role(
                "admin",
                "Administrator with full access",
                "db_admin",
            ),
            Role(
                "read_only_user",
                "User with read-only access",
                "db_read_only_user",
            ),
        ]
        self.table_privilages_map = {
            "employees": [
                RoleTablePrivileges(
                    "id1",
                    "admin",
                    "employees",
                    ["name", "salary", "department_id"],
                    [],
                )
            ],
            "departments": [
                RoleTablePrivileges("id2", "admin", "departments", ["name", "id"], []),
                RoleTablePrivileges(
                    "id2", "read_only_user", "departments", ["name"], []
                ),
            ],
        }

    def test_role_not_found(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "manager",
            "SELECT employees.name FROM employees",
        )
        self.assertFalse(result.query_allowed)

    def test_invalid_sql_query(self):
        result = check_query_privilages(
            self.table_privilages_map, self.roles, "admin", "INVALID SQL QUERY"
        )
        self.assertFalse(result.query_allowed)

    def test_table_not_in_privilages(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            "SELECT projects.name FROM projects",
        )
        self.assertFalse(result.query_allowed)

    def test_wildcard_star_not_allowed(self):
        result = check_query_privilages(
            self.table_privilages_map, self.roles, "admin", "SELECT * FROM employees"
        )
        self.assertFalse(result.query_allowed)

    def test_role_no_table_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            "SELECT employees.name FROM employees",
        )
        self.assertFalse(result.query_allowed)

    def test_role_no_column_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            "SELECT employees.salary FROM employees",
        )
        self.assertFalse(result.query_allowed)

    def test_query_allowed(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            "SELECT employees.name FROM employees",
        )
        self.assertTrue(result.query_allowed)

    def test_join_query(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            "SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id",
        )
        self.assertTrue(result.query_allowed)

    def test_join_query_no_table_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            "SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id",
        )
        self.assertFalse(result.query_allowed)

    def test_cte_query(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM employees e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT employee_departments.name, employee_departments.department FROM employee_departments
            """,
        )
        print(result)
        self.assertTrue(result.query_allowed)

    def test_cte_query_no_table_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM employees e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT employee_departments.name, employee_departments.department FROM employee_departments
            """,
        )
        self.assertFalse(result.query_allowed)

    def test_alias_query(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            "SELECT employees.name AS employee_name FROM employees",
        )
        self.assertTrue(result.query_allowed)

    def test_alias_query_no_column_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            "SELECT employees.salary AS employee_salary FROM employees",
        )
        self.assertFalse(result.query_allowed)

    def test_subquery_query(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            "SELECT e.name FROM (SELECT employees.name FROM employees) e",
        )
        self.assertTrue(result.query_allowed)

    def test_subquery_with_cte_join_no_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM employees e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT e.name FROM (SELECT employee_departments.name FROM employee_departments) e
            """,
        )
        self.assertFalse(result.query_allowed)

    def test_subquery_with_cte_join(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM employees e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT e.name FROM (SELECT employee_departments.name FROM employee_departments) e
            """,
        )
        self.assertTrue(result.query_allowed)

    def test_subquery_within_cte_with_join(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "admin",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM (
                    SELECT employees.name
                    FROM employees
                ) e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT e.name FROM (SELECT employee_departments.name FROM employee_departments) e
            """,
        )
        self.assertTrue(result.query_allowed)

    def test_subquery_within_cte_with_join_no_access(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "read_only_user",
            """
            WITH employee_departments AS (
                SELECT e.name, d.name as department
                FROM (
                    SELECT employees.name
                    FROM employees
                ) e
                JOIN departments d ON e.department_id = d.id
            )
            SELECT e.name FROM (SELECT employee_departments.name FROM employee_departments) e
            """,
        )
        self.assertFalse(result.query_allowed)


class TestRowSecurity(unittest.TestCase):

    def setUp(self):
        self.roles = [
            Role("project_manager", "Project Manager", "db_project_manager"),
            Role("department_manager", "Department Manager", "db_department_manager"),
        ]

        self.table_privilages_map = {
            "projects": [
                RoleTablePrivileges(
                    "1",
                    "project_manager",
                    "projects",
                    [
                        "id",
                        "name",
                        "description",
                        "start_date",
                        "end_date",
                    ],
                    ["id"],
                ),
                RoleTablePrivileges(
                    "2",
                    "department_manager",
                    "projects",
                    [
                        "id",
                        "name",
                        "description",
                        "department_id",
                    ],
                    ["department_id"],
                ),
            ],
            "departments": [
                RoleTablePrivileges(
                    "id2",
                    "department_manager",
                    "departments",
                    ["id", "name", "description"],
                    ["id"],
                )
            ],
        }

    def test_no_where_clause(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "project_manager",
            "SELECT p.id, p.name FROM projects as p",
            {
                "projects": [ColumnScope("projects", "id", "1")],
            },
        )
        self.assertFalse(result.query_allowed)

    def test_missing_scopes_for_role(self):
        try:
            _result = check_query_privilages(
                self.table_privilages_map,
                self.roles,
                "department_manager",
                "SELECT p.id, p.name FROM projects as p where p.department_id = 1",
            )
            self.fail("Expected exception due to missing scopes for role")
        except:
            pass

    def test_where_clause_not_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "project_manager",
            "SELECT p.id, p.name FROM projects as p WHERE p.id = 1",
            table_scopes={
                "projects": [ColumnScope("projects", "id", "2")],
            },
        )
        self.assertFalse(result.query_allowed)

    def test_where_clause_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "project_manager",
            "SELECT p.id, p.name FROM projects as p WHERE p.id = 1",
            table_scopes={
                "projects": [ColumnScope("projects", "id", "1")],
            },
        )
        print(result)
        self.assertTrue(result.query_allowed)

    def test_joined_table_scopes_not_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "department_manager",
            "SELECT p.id, p.name FROM projects as p JOIN departments as d ON p.department_id = d.id WHERE p.id = 1",
            table_scopes={
                "projects": [ColumnScope("projects", "department_id", "2")],
                "departments": [ColumnScope("departments", "id", "2")],
            },
        )
        self.assertFalse(result.query_allowed)

    def test_joined_table_scopes_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "department_manager",
            "SELECT p.id, p.name FROM projects as p JOIN departments as d ON p.department_id = d.id WHERE p.department_id = 1 and d.id = 1",
            table_scopes={
                "projects": [ColumnScope("projects", "department_id", "1")],
                "departments": [ColumnScope("departments", "id", "1")],
            },
        )
        self.assertTrue(result.query_allowed)

    def test_joined_table_scopes_partially_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "department_manager",
            "SELECT p.id, p.name, d.name FROM projects as p JOIN departments as d ON p.department_id = d.id WHERE p.department_id = 1",
            table_scopes={
                "projects": [ColumnScope("projects", "department_id", "1")],
                "departments": [ColumnScope("departments", "id", "1")],
            },
        )
        self.assertFalse(result.query_allowed)

    def test_subquery_scope_not_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "project_manager",
            "SELECT p.id, p.name FROM (SELECT q.id, q.name FROM projects q) p",
            table_scopes={
                "projects": [ColumnScope("projects", "id", "1")],
            },
        )
        self.assertFalse(result.query_allowed)

    def test_subquery_scope_satisfied(self):
        result = check_query_privilages(
            self.table_privilages_map,
            self.roles,
            "project_manager",
            "SELECT p.id, p.name FROM (SELECT q.id, q.name FROM projects q WHERE q.id = 1) p",
            table_scopes={
                "projects": [ColumnScope("projects", "id", "1")],
            },
        )
        self.assertTrue(result.query_allowed)


if __name__ == "__main__":
    unittest.main()
