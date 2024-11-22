from abc import ABC, abstractmethod
import json
from typing import Any, List, Optional, cast
from openai.types.chat import ChatCompletionMessageParam
from db.db_queries import get_saved_queries
from db.models import Turn
from rbac.check_permissions import ErrorCode, PrivilageCheckResult

from executor.errors import UnRecoverableError
from executor.models import GeneratedQuery, HealedQuery, QueryType, QueryTypeLiteral, QuestionAnsweringResult, RelevantCatalog, RelevantTables, NLQIntent
from executor.state import AgentState, QueryResults
from executor.catalog import Catalog
from utils.logger import get_logger
from utils.query_pipeline import QueryExecutionFailureResult, QueryExecutionResult
from utils.parse_catalog import parsed_catalogs
from utils.table_to_markdown import get_table_markdown

logger = get_logger("[AGENTIC TOOLS]")


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
        self, nlq: str, nlq_turns: list[Turn]
    ) -> QueryTypeLiteral:
        """
        Analyze the natural language query (NLQ) and return the type of query.
        Type can be Question Answering, or Report Generation
        """
        system_prompt = """
        Your task is to categorize natural language queries into one of three types based on the user's intent:
        1.  QUESTION_ANSWERING
            When the user asks for a specific summary or analysis of existing data. This is only applicable required data is already available in the conversation history.
            If answering the query requires additional information, prefer REPORT_GENERATION or REPORT_FEEDBACK over QUESTION_ANSWERING.

            Examples:
            "Summarize the marketing campaign performance."
            "What are the key insights from the sales data?"
            "Is the payout for the last quarter higher than the previous quarter?"

        2.  REPORT_GENERATION
            When the user requests new data or information that has not been previously generated or summarized. This typically requires querying a database.

            Examples:
            "What are the total sales by product category?"
            "Show me the top 10 customers by revenue."
            "Provide a detailed report on the marketing campaign's performance."

        3.  REPORT_FEEDBACK
            When the user gives feedback on an existing report, often asking for additional details or adjustments.

            Examples:
            "Add a breakdown of sales by region."
            "Include the customer acquisition cost."
            "The report is missing last year's sales comparison."

        4. CASUAL_CONVERSATION
            When the user is engaging in casual conversation or asking general questions that do not require data analysis or reporting.

            Examples:
            "How are you?"
            "How's the weather today?"
            "What's the latest news?"
            "What can you do"
            "What is your name"

        To help you decide the query type, you will have access to the historical interaction between the user and the assistant. You need to do the classification based on the most recent user message
        """
        old_messages: list[ChatCompletionMessageParam] = []
        for turn in nlq_turns:
            old_messages.append({"role": "user", "content": turn.nlq})
            old_messages.append(
                {"role": "assistant", "content": json.dumps(turn.sql_query)}
            )

        llm_response = await self.invoke_llm(
            QueryType,
            [
                {"role": "system", "content": system_prompt},
                *old_messages,
                {"role": "user", "content": nlq},
            ],
        )
        return llm_response.query_type

    async def get_relevant_catalog(
        self, nlq: str, catalogs: List[Catalog], prev_turn: Optional[Turn] = None
    ) -> str:
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

        user_prompt = ""
        if prev_turn:
            user_prompt = f"""
            ## Previous Query:
            The following query was executed previously. You can use this information to determine the relevant database catalog.
            {prev_turn.sql_query}

            ## Original User Query:
            This was the query used to generate the above SQL query.
            {prev_turn.nlq}
            """

        user_prompt += f"""
            ## User asked query: 
            {nlq}
            ## Database Catalogs: 
            {database_info_json}
            """

        llm_resp = await self.invoke_llm(
            RelevantCatalog,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if llm_resp.requires_multiple_catalogs:
            raise UnRecoverableError("Multiple catalogs/databases are required")
        return llm_resp.database_name

    async def get_relevant_tables(
        self, nlq: str, catalog: Catalog, prev_turn: Optional[Turn] = None
    ) -> List[str]:
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
        user_prompt = ""
        if prev_turn:
            user_prompt = f"""
            ## Previous Query:
            The following query was executed previously. You can use this information to determine the relevant tables
            {prev_turn.sql_query}

            ## Original User Query:
            This was the query used to generate the above SQL query.
            {prev_turn.nlq}
            """

        user_prompt += f"""
        ## User asked query: 
        {nlq} 
        ## Database Catalog: 
        {tables_info_json}
        """

        llm_response = await self.invoke_llm(
            RelevantTables,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return llm_response.tables

    async def generate_queries(
        self, state: AgentState, prev_turn: Optional[Turn] = None
    ) -> str:
        """
        Generate a list of queries as simple as possible for the given natural language query (NLQ) and catalogs
        """

        catalog = cast(Catalog, state.relevant_catalog)

        system_prompt = f"""
        You are a seasoned SQL Expert with over 10 years of experience with {catalog.provider} dialect.
        Your task is to create SQL queries based on the given user intent, using metadata from a provided database catalog.
        The catalog includes database descriptions, table names, column names, and other relevant metadata to guide your query generation.

        The following types of queries are not allowed:
            - Queries with wildcard stars.
            - Queries that don't have a table name for a column.
            - Queries that have subqueries that are in where clasues, joins, group by, order by, etc.
            - SQL Functions that are user defined. Inbuilt functions like SUM, AVG, COUNT, etc are allowed.

        ```sql
            <!-- Queries with wildcard stars are not allowed -->
        SELECT * FROM employees

        select employees.name from employees where employees.salary > 1000 <!--This Query is allowed -->
        select employees.name from employees where salary > 1000 <!--This Query is not allowed -->
        select name from employees where employees.salary > 1000 <!--This Query is not allowed -->
        select name from employees where salary > 1000 <!--This Query is not allowed -->
        ```

        ## Guidelines:
        1. Leverage the Catalog: Use the metadata to align your queries with the correct database, tables, and columns.
        2. Output: Create a single query that is optimized to retrieve the required data efficiently.
        3. Column Prefixing: Ensure that all columns are prefixed with the table name to avoid ambiguity.
        4. JSON Data: Do not return JSON data stored in columns directly. If required, only select the necessary fields from the JSON columns.
        5. Feedback: In case you have already generated queries for user's queries, treat the user's most recent message as the feedback for previously generated queries.
        Ensure that your generated queries are precise, efficient, and easy to understand, showcasing your extensive experience.

        ##  Schema for Relevant Tables:
        {state.relevant_tables}
        """

        if len(state.categorical_tables) > 0:
            system_prompt += f"""
            ## Categorical Tables:
            These can be used in the queries to filter the data based on specific categories or values.
            If you get a query task requires filtring by specific values, identify the list of relevant values from these tables, and use primary key fields to filter the data.

            For example, if you have a table 'departments' with columns 'id' and 'name', you can use the 'id' field to filter the data in other tables that have a 'dept_id' field.

            You will find all the categorical values for the categorical tables below:
            """

            for table_name, data in state.categorical_tables.items():
                if len(data) == 0:
                    continue

                system_prompt += f"""
                ### {table_name}:
                {get_table_markdown(data)}
                """

        user_prompt = f"""{state.intent}"""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
        ]
        if prev_turn:
            messages.append({"role": "user", "content": prev_turn.nlq})
            messages.append(
                {"role": "assistant", "content": prev_turn.sql_query.sqlquery}
            )

        messages.append({"role": "user", "content": user_prompt})

        llm_response = await self.invoke_llm(
            GeneratedQuery,
            messages,
        )
        print(system_prompt)
        logger.info(f"Generated Queries: {llm_response.query}")
        return llm_response.query

    async def is_result_relevant(self, results: QueryResults, nlq: str) -> bool:
        """
        Check if the aggregated result is relevant to the original natural language query (NLQ).
        """
        raise NotImplementedError

    async def heal_fix_query(
        self,
        query: str,
        state: AgentState,
        errors: QueryExecutionFailureResult,
        regenerate: bool = False,
    ) -> str:
        """
        Fix the query by looking at the error message and the query itself.
        """

        catalog = cast(Catalog, state.relevant_catalog)
        system_prompt = f"""
        You are a SQL Expert with over 10 years of experience in {catalog.provider} dialect. 
        You will be provided with the original SQL query, the relevant information related to the query and the query execution result.
        """

        if regenerate:
            system_prompt += f"""
            Others have tried to fix this query but failed. There's probably something wrong with the approach or the query itself
            Your task is to regenerate an SQL query that servers the same purpose as the current one. 
            The query should be syntactically correct and should adhere to the best practices.
            """
        else:
            system_prompt += f"""
            Your task is to troubleshoot and fix all the issue with the provided SQL query 
            """

        example_tables = f"""
        departments:
        id | name
        1  | IT
        2  | HR

        employees:
        id | name | dept_id | salary
        1  | John | 1       | 1000
        2  | Jane | 2       | 1500

        """

        if isinstance(errors.reason, PrivilageCheckResult):
            err = errors.reason.err_code
            match err:
                case ErrorCode.MISSING_TABLE_NAME_PREFIX:
                    system_prompt += f""" 
                    Your task is to ensure that all columns in the query are prefixed with the table name to avoid 
                    ambiguity about the table the column orignates from.
                    Example:

                    Assuming the following tables:

                    {example_tables}

                    The following queries are not allowed:
                         select employees.name from employees where salary > 1000
                         select name from employees where employees.salary > 1000
                         select name from employees where salary > 1000
                         select employees.name, departments.name as dept_name join departments on departments.id = dept_id from employees where employees.salary > 1000
                    
                    The following queries are allowed:
                         select employees.name from employees where employees.salary > 1000
                         select employees.name from employees join departments on departments.id = employees.dept_id where employees.salary > 1000
                    """

                case ErrorCode.INVALID_SQL_QUERY:
                    system_prompt += """
                    The query is not valid SQL. Please check the syntax and ensure that all SQL keywords are 
                    used correctly and it is syntactically correct.
                    """

                case ErrorCode.WILDCARD_STAR_NOT_ALLOWED:
                    system_prompt += f"""
                    Your task is to remove the wildcard stars from the select clauses and 
                    replace them with explicit column names. This will ensure that the query is more specific and avoids ambiguity. 

                    Example: 
                    Assuming the following tables:

                    {example_tables}

                    The following queries are not allowed:

                    SELECT * FROM employees
                    SELECT employees.name, departments.* FROM employees JOIN departments ON employees.dept_id = departments.id

                    You need to use the table information provided with the context to replace the wildcard stars.
                    """
                case ErrorCode.ROLE_NO_COLUMN_ACCESS:
                    system_prompt += f"""
                    Your task is to remove the columns that the role does not have access to. You will be given the 
                    information about the columns that the role has access to i the context.
                    """
                case ErrorCode.ROLE_NO_ROWS_ACCESS:
                    system_prompt += f"""
                    Your task is to add where clauses to the query to restrict the rows that the role has access to. 
                    A column scope defines the filters/restrictions that are applied to a column to restrict the rows that a role has access to.

                    Privilages defined for the tables are as follows
                    {parsed_catalogs.database_privileges}
                    """

                case ErrorCode.CTE_ERROR:
                    system_prompt += f"""
                    Your task is to fix the specified Common Table Expression (CTE) in the query. You will be provided information about exactly what is wrong with the CTE.
                    """
                case ErrorCode.SUBQUERY_ERROR:
                    system_prompt += f"""
                    Your task is to fix the specified subquery in the query. You will be provided information about exactly what is wrong with the subquery.
                    """

                case _:
                    system_prompt += f"""
                    Your task is to fix the query based on the error message provided. You will be given the context of the query and the error message to help you identify the issue.
                    """
        else:
            system_prompt += f"""
            The error is most likely from the database driver, which means that the query is not valid SQL. 
            Please check the syntax and ensure that all SQL keywords are used correctly and it is syntactically correct.
            """

        system_prompt += f"""
        ### Intent of the query: 
        {state.intent}

        ### Table Schema
        ```json
        {json.dumps(catalog.schema)}
        ```

        ### Relevant Tables: 
        The following tables are relevant to the query:
        {state.relevant_tables}
        """

        user_prompt = f"""
        ## SQL Query: 
        {query}

        ## Errors: 
        {errors}
        """
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

        catalog = cast(Catalog, state.relevant_catalog)

        system_prompt = f"""
        You are a seasoned SQL Expert with over 10 years of experience with {catalog.provider} dialect.
        You will be provided with the original SQL query, the relevant information related to the query and the query
        execution result which includes any errors or unexpected results. Your task is to troubleshoot and fix SQL
        queries that are incorrect, not allowed or have improper permissions.

        The catalog includes database descriptions, table names, column names, and other relevant metadata to guide your query generation.

        The following kinds of queries are not not supported:
            - Queries with wildcard stars.
            - Queries that don't have a table name for a column.
            - Queries that have subqueries that are in where clasues, joins, group by, order by, etc.
            - SQL Functions that are user defined. Inbuilt functions like SUM, AVG, COUNT, etc are allowed.

        ```sql
            <!-- Queries with wildcard stars are not allowed -->
        SELECT * FROM employees

        select employees.name from employees where employees.salary > 1000 <!--This Query is allowed -->
        select employees.name from employees where salary > 1000 <!--This Query is not allowed -->
        select name from employees where employees.salary > 1000 <!--This Query is not allowed -->
        select name from employees where salary > 1000 <!--This Query is not allowed -->
        ```

        Make sure the query is distint from the original query and serves the same purpose. Also make sure the query answers the 
        user's intent

        Schems for the tables are as follows:
        ```json
        {catalog.schema}
        ```
        """
        user_query = f"""
        ### Original Query: 
        {query}

        ### Errors: 
        {errors}
        """

        llm_response = await self.invoke_llm(
            HealedQuery,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0.5,
        )
        return llm_response.query

    async def answer_question(self, nlq: str, data: QueryResults) -> str:
        """
        Answer the question asked by the user
        """
        system_prompt = f"""
        You are a Data Analyst. You need to analyze the following data:

        {get_table_markdown(data)}

        Your task is to analyze the data and provide a clear and concise answer to the user's question.

        """

        if len(system_prompt) > 32000:
            raise UnRecoverableError(
                "Cannot answer the question. The data is too large"
            )

        user_prompt = f"""
        {nlq}
        """

        llm_response = await self.invoke_llm(
            QuestionAnsweringResult,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return llm_response.answer
