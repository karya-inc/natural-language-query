from abc import ABC, abstractmethod
import json
from typing import Any, List, Literal, cast
from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy.orm import context

from executor.errors import UnRecoverableError
from executor.models import AggregatedQuery, HealedQuery, QueryType, RelevantCatalog, GeneratedQueryList, RelevantTables, NLQIntent
from executor.state import AgentState, QueryResults
from executor.catalog import Catalog
from utils.query_pipeline import QueryExecutionResult


class AgentTools(ABC):

    @abstractmethod
    async def invoke_llm[
        T
    ](
        self,
        response_type: type[T],
        messages: list[ChatCompletionMessageParam],
        temperature=0.0,
    ) -> T:
        raise NotImplementedError

    async def analaze_nlq_intent(self, nlq: str) -> str:
        """
        Analyze the natural language query (NLQ) and return the intent of the query.
        """
        system_prompt = """
        You are a SQL and Technology Expert tasked with understanding user queries and generating informative responses.
        Your role is to carefully analyze the user's input, which will be in natural language, to identify the underlying intent and provide a detailed response that addresses their needs.
        Requirements for your response:
        1. Intent Analysis: Accurately determine what the user is asking for or trying to achieve.
        2. Comprehensive Explanation: Deliver a clear and thorough natural language explanation that elaborates on the user's query, including any necessary context or background information.
        3. Insightful Guidance: If applicable, offer additional insights, best practices, or recommendations related to SQL or technology to enhance user understanding.
        4. Clarity and Relevance: Ensure your response is easy to understand and directly relevant to the user's intent.
        """
        response = await self.invoke_llm(
            NLQIntent,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nlq},
            ],
        )
        return response.intent

    async def analyze_query_type(
        self, nlq: str
    ) -> Literal["QUESTION_ANSWERING", "REPORT_GENERATION"]:
        """
        Analyze the natural language query (NLQ) and return the type of query.
        Type can be Question Answering, or Report Generation
        """
        system_prompt = """
        Your role is to analyze natural language queries and categorize them into specific buckets based on their context. The primary categories are:
        1. Question Answering: This includes queries where the user is asking for explanations or insights related to data or information that has already been generated or discussed.
        2. Report Generation: This encompasses queries where the user is requesting new data compilations, reports, or detailed data summaries that have not been previously generated.
        Evaluate the user's input and correctly assign it to one of the defined buckets: Question Answering or Report Generation.
        """
        llm_response = await self.invoke_llm(
            QueryType,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nlq},
            ],
        )
        return llm_response.query_type

    async def get_relevant_catalog(self, nlq: str, catalogs: List[Catalog]) -> str:
        """
        Get the subset of database catalogs that might be relevant to the given natural language query (NLQ).
        """
        database_info: list[dict] = []

        for catalog in catalogs:
            table_map = map(
                lambda table_kv: {
                    "name": table_kv[0],
                    "description": table_kv[1]["description"],
                },
                catalog.schema.items(),
            )
            table_info = list(table_map)

            catalog_info = {
                "name": catalog.name,
                "description": catalog.description,
                "tables": table_info,
            }

            database_info.append(catalog_info)

        database_info_json = json.dumps(database_info)

        system_prompt = """
        You are a highly experienced SQL Expert with over 10 years of expertise. You are provided with a catalog containing metadata about various databases, including descriptions, table names, and column names. Your task is to analyze user queries to understand their intent and determine whether the required data can be retrieved from a single database or if multiple databases are needed.
        Response Requirements:
        1. Intent Analysis: Carefully assess the user's query and cross-reference it with the catalog metadata to identify the database or databases involved.
        2. Categorization:
            If the data can be fetched from a single database, return True and include the name of the database.
            If the data must be retrieved from multiple databases, return False.
        3. Output Format:
            For single-database queries: True, Database Name
            For multi-database queries: False
        Ensure that your analysis is thorough, leveraging your extensive experience to provide precise and contextually accurate responses.
        """
        nlq_database_info = (
            f"User asked query: {nlq}, ## Database Catalogs: {database_info_json}"
        )

        llm_resp = await self.invoke_llm(
            RelevantCatalog,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nlq_database_info},
            ],
        )
        if llm_resp.requires_multiple_catalogs:
            raise UnRecoverableError("Multiple catalogs/databases are required")
        return llm_resp.database_name

    async def get_relevant_tables(self, nlq: str, catalog: Catalog) -> List[str]:
        tables_info = []
        for tablename, tableinfo in catalog.schema.items():
            curr_table_info = {
                "table": tablename,
                "description": tableinfo["description"],
                "columns": tableinfo["columns"],
            }
            tables_info.append(curr_table_info)

        tables_info_json = json.dumps(tables_info)

        system_prompt = """
        You are a seasoned SQL Expert with over 10 years of experience.
        Your role is to analyze user queries and identify all the relevant tables in a database catalog that might be related or can provide the required data.
        The catalog contains metadata about databases, including descriptions, table names, and column names.
        """
        nlq_tables_info = (
            f"User asked query: {nlq}, ## Database Catalog: {tables_info_json}"
        )

        llm_response = await self.invoke_llm(
            RelevantTables,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nlq_tables_info},
            ],
        )

        return llm_response.tables

    async def generate_queries(
        self, nlq: str, relevant_tables: dict[str, Any], provider: str
    ) -> List[str]:
        """
        Generate a list of queries as simple as possible for the given natural language query (NLQ) and catalogs
        """

        system_prompt = f"""
        You are a seasoned SQL Expert with over 10 years of experience with {provider} dialect.
        Your task is to create SQL queries based on the given user intent, using metadata from a provided database catalog.
        The catalog includes database descriptions, table names, column names, and other relevant metadata to guide your query generation.

        User Permissions: A query is allowed if:
            - The role has access to the table in the query
            - The role has access to the columns in the query
            - The row level restrictions are satisfied for the query with where clauses on the required column scopes

        The following kinds of queries are not not supported:
            - Queries with wildcard stars.
            - Queries that don't have a table name for a column. All occurances of columns SHOULD be prefixed with table name to avoid ambiguity. Even columns in where clauses, functions, joins, withs, subqueries, group by and order by clauses follow this requirement
            - Invalid SQL Queries

        ```sql
            <!-- Queries with wildcard stars are not allowed -->
        SELECT * FROM employees

        select employees.name from employees where employees.salary > 1000 <!--This Query is allowed -->
        select employees.name from employees where salary > 1000 <!--This Query is not allowed -->
        select name from employees where employees.salary > 1000 <!--This Query is not allowed -->
        select name from employees where salary > 1000 <!--This Query is not allowed -->
        ```

        Guidelines:
        1. Leverage the Catalog: Use the metadata to align your queries with the correct database, tables, and columns.
        2. Output: Create multiple simple queries to address the user intent comprehensively and efficiently.
        3. Column Prefixing: Ensure that all columns are prefixed with the table name to avoid ambiguity.
        Ensure that your generated queries are precise, efficient, and easy to understand, showcasing your extensive experience.
        """
        nlq_relevant_tables = f"{nlq} Relevant Tables: {relevant_tables}"
        llm_response = await self.invoke_llm(
            GeneratedQueryList,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": nlq_relevant_tables},
            ],
        )
        return llm_response.queries

    async def generate_aggregate_query(
        self,
        intermediate_results: dict[str, QueryResults],
        relevant_tables: dict[str, Any],
    ) -> str:
        """
        Generate an aggregate query by looking at the queries used to generate results
        in the ephimeral storage. Use subqueries and CTES (with clause) to generate the aggregate query.
        """
        system_prompt = """
            You are a SQL Expert with over 10 years of experience. Your task is to consolidate multiple provided queries into an optimal single SQL query or the minimum number of queries needed to achieve the desired result. You will be provided with a json containing queries and sample responses from them.

            Task Requirements:
            1. Analyze Provided Queries: Carefully review the given individual queries to understand the data they retrieve and their intended outcomes.
            2. Aggregate Query Construction: Combine and refactor the individual queries into one comprehensive SQL query that can deliver the same result set. You can convert these provided queries in CTEs (With clasuses), subqueries or joings to achieve this.
            3. Ensure that the final query is optimized for performance and adheres to SQL best practices.

            Guidelines:
            1. Efficiency and Performance: Design the aggregated query to minimize computation time and resource usage.
            2. Simplicity and Clarity: Strive for clear and maintainable SQL code, even when aggregating complex logic.
            3. Output Format: Return the complete aggregated query and, if necessary, include brief comments explaining non-standard operations or logic.
            Ensure that the final result is accurate, optimized, and reflects your expertise in SQL.
            """

        user_prompt = f"Intermediate Results: {intermediate_results}, Relevant Tables: {relevant_tables}"

        llm_response = await self.invoke_llm(
            AggregatedQuery,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return llm_response.query

    async def is_result_relevant(self, results: QueryResults, nlq: str) -> bool:
        """
        Check if the aggregated result is relevant to the original natural language query (NLQ).
        """
        raise NotImplementedError

    async def heal_fix_query(
        self, query: str, state: AgentState, errors: QueryExecutionResult
    ) -> str:
        """
        Fix the query by looking at the error message and the query itself.
        """

        catalog = cast(Catalog, state.relevant_catalog)
        system_prompt = f"""
        You are a SQL Expert with over 10 years of experience in {catalog.provider} dialect. Your task is to troubleshoot and fix SQL queries that are incorrect or have improper permissions. You will be provided with the original SQL query, the relevant information related to the query and the query execution result which includes any errors or unexpected results.

        The following kinds of queries are not not supported:
            - Queries with wildcard stars.
            - Queries that don't have a table name for a column.
            - Invalid SQL Queries

        User Permissions: A query is allowed if:
            - The role has access to the table in the query
            - The role has access to the columns in the query
            - The row level restrictions are satisfied for the query with where clauses on the required column scopes


        ```sql
            <!-- Queries with wildcard stars are not allowed -->
        SELECT * FROM employees

        select employees.name from employees where employees.salary > 1000 <!--This Query is allowed -->
        select employees.name from employees where salary > 1000 <!--This Query is not allowed -->
        select name from employees where employees.salary > 1000 <!--This Query is not allowed -->
        select name from employees where salary > 1000 <!--This Query is not allowed -->
        ```

        Task Requirements:
        1. Analyze the Problem: Carefully review the provided SQL query and the context, including the error message or details about the unexpected outcome.
        2. Diagnose and Fix:
            Identify the root cause of the issue in the query.
            Correct the SQL query to ensure it performs as expected and meets the desired requirements.
        3. Generate the Solution: Provide the fixed SQL query and, if necessary, a brief explanation of the changes made and why they resolve the issue.

        Your expertise is key in resolving issues swiftly and effectively, resulting in a functional and optimized SQL query.
        """

        user_prompt = f"SQL Query: {query}, Errors: {errors}, Context: {context}"
        llm_response = await self.invoke_llm(
            HealedQuery,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return llm_response.query

    async def heal_regenerate_query(
        self, query: str, state: AgentState, errors: QueryExecutionResult
    ) -> str:
        """
        Regenerate the query by trying to understand the intent of the query.
        Take reference from the previous SQL query and error message.
        """
        system_prompt = """
        You are a SQL Expert with over 10 years of experience in {catalog.provider} dialect. Your task is to troubleshoot and fix SQL queries that are incorrect or have improper permissions. You will be provided with the original SQL query, the relevant information related to the query and the query execution result which includes any errors or unexpected results.

        The following kinds of queries are not not supported:
            - Queries with wildcard stars.
            - Queries that don't have a table name for a column.
            - Invalid SQL Queries

        User Permissions: A query is allowed if:
            - The role has access to the table in the query
            - The role has access to the columns in the query
            - The row level restrictions are satisfied for the query with where clauses on the required column scopes

        NOTE: The most common issue is the absence of table names for columns in the query. Ensure that all columns are prefixed with the table name to avoid ambiguity. You will be provided information about the location of the column where the table name is absent


        ```sql
            <!-- Queries with wildcard stars are not allowed -->
        SELECT * FROM employees

        select employees.name from employees where employees.salary > 1000 <!--This Query is allowed -->
        select employees.name from employees where salary > 1000 <!--This Query is not allowed -->
        select name from employees where employees.salary > 1000 <!--This Query is not allowed -->
        select name from employees where salary > 1000 <!--This Query is not allowed -->
        ```

        Task Requirements:
        1. Analyze the Problem: Carefully review the provided original SQL query. and the context, including the error message or details about the unexpected outcome.
        2. Diagnose and Fix the problem by Regenerating a completely new query based on the context that tries to fix the issue.

        Guidelines:
        1. Accuracy: Ensure that the corrected query adheres to best practices and produces the intended result.
        2. Efficiency: Optimize the query where possible to improve performance without altering its functionality.
        """
        user_query = f"""Fix Query: {query}, Context: {state}, Errors: {errors}"""

        llm_response = await self.invoke_llm(
            HealedQuery,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0.5,
        )
        return llm_response.query

    async def answer_question(self, nlq: str) -> Any:
        """
        Answer the question asked by the user
        """
        raise NotImplementedError
