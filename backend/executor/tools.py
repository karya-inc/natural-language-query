from abc import ABC, abstractmethod
import json
from typing import Any, List, Literal, Tuple
from openai.types.chat import ChatCompletionMessageParam

from executor.state import AgentState, QueryResults
from .storage import EphemeralTools
from .catalog import Catalog
from .query import Query
from .result import Result


class AgentTools(EphemeralTools, ABC):

    @abstractmethod
    def invoke_llm[
        T
    ](self, response_type: type[T], messages: list[ChatCompletionMessageParam]) -> T:
        raise NotImplementedError

    def analaze_nlq_intent(self, nlq: str) -> str:
        """
        Analyze the natural language query (NLQ) and return the intent of the query.
        """
        return self.invoke_llm(
            str,
            [
                {"role": "user", "content": ""},
            ],
        )

    def analyze_query_type(
        self, nlq: str
    ) -> Literal["QUESTION_ANSWERING", "REPORT_GENERATION"]:
        """
        Analyze the natural language query (NLQ) and return the type of query.
        Type can be Question Answering, or Report Generation
        """
        raise NotImplementedError

    def get_relevant_catalog(self, nlq: str, catalogs: List[Catalog]) -> str:
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

        raise NotImplementedError("Call LLM to get the relevant catalogs")

    def get_relevant_tables(self, nlq: str, catalog: Catalog) -> List[str]:
        tables_info = []
        for tablename, tableinfo in catalog.schema.items():
            columns_info_map = map(
                lambda col_kv: {
                    "name": col_kv[0],
                    "description": col_kv[1]["description"],
                },
                tableinfo["columns"].items(),
            )
            curr_table_info = {
                "table": tablename,
                "description": tableinfo["description"],
                "columns": list(columns_info_map),
            }
            tables_info.append(curr_table_info)

        tables_info_json = json.dumps(tables_info)

        raise NotImplementedError("Call LLM to get the relevant tables")

    def generate_queries(self, nlq: str, relevant_tables: dict[str, Any]) -> List[str]:
        """
        Generate a list of queries as simple as possible for the given natural language query (NLQ) and catalogs
        """
        raise NotImplementedError

    def generate_aggregate_query(
        self, intermediate_results: dict[str, QueryResults]
    ) -> str:
        """
        Generate an aggregate query by looking at the queries used to generate results
        in the ephimeral storage. Use subqueries and CTES (with clause) to generate the aggregate query.
        """
        raise NotImplementedError

    def is_result_relevant(self, results: QueryResults, nlq: str) -> bool:
        """
        Check if the aggregated result is relevant to the original natural language query (NLQ).
        """
        raise NotImplementedError

    def heal_fix_query(self, query: str) -> str:
        """
        Fix the query by looking at the error message and the query itself.
        """
        raise NotImplementedError

    def heal_regenerate_query(self, state: AgentState, query: str) -> str:
        """
        Regenerate the query by trying to understand the intent of the query.
        Take reference from the previous SQL query and error message.
        """
        raise NotImplementedError

    def answer_question(self, nlq: str) -> Any:
        """
        Answer the question asked by the user
        """
        raise NotImplementedError
