from abc import ABC, abstractmethod
from typing import Any, List, Literal, Tuple
from enum import Enum

from openai.types.chat import ChatCompletionMessageParam
from .storage import EphemeralTools
from .catalog import Catalog
from .query import Query
from .result import Result


class GenerationType(Enum):
    ANALYZE_NLQ = "analyze_nlq"
    ANALYZE_QUERY_TYPE = "analyze_query_type"
    ANALYZE_CATALOGS = "analyze_catalogs"
    GENERATE_QUERIES = "generate_queries"
    STORE_INTERMEDIATE_RESULTS = "store_intermediate_results"
    GENERATE_AGGREGATE_QUERY = "generate_aggregate_query"
    IS_RESULT_RELEVANT = "is_result_relevant"
    HEAL_FIX_QUERY = "heal_fix_query"
    HEAL_REGENERATE_QUERY = "heal_regenerate_query"


class AgentTools(EphemeralTools, ABC):

    @abstractmethod
    def invoke_llm[T](self, response_type: type[T], messages: list[ChatCompletionMessageParam]) -> T:
        raise NotImplementedError

    def analaze_nlq(self, nlq: str) -> str:
        """
        Analyze the natural language query (NLQ) and return the intent of the query.
        """
        raise NotImplementedError

    def analyze_query_type(self, nlq: str) -> str:
        """
        Analyze the natural language query (NLQ) and return the type of query.
        Type can be Question Answering, or Report Generation
        """
        raise NotImplementedError

    def analyze_catalogs(self, nlq: str, catalogs: List[Catalog]) -> List[Catalog]:
        """
        Get the subset of catalogs that might be relevant to the given natural language query (NLQ).
        """
        raise NotImplementedError

    def generate_queries(self, nlq: str, catalogs: List[Catalog]) -> List[Query]:
        """
        Generate a list of queries as simple as possible for the given natural language query (NLQ) and catalogs
        """
        raise NotImplementedError

    def store_intermediate_results(self, results: List[Result]) -> List[Catalog]:
        """
        Store queries and results in an ephimeral storage.
        """
        raise NotImplementedError

    def generate_aggregate_query(
        self, results: List[Result], intermediate_catalogs: List[Catalog]
    ) -> Query:
        """
        Generate an aggregate query by looking at the queries used to generate results
        in the ephimeral storage. Use subqueries and CTES (with clause) to generate the aggregate query.
        """
        raise NotImplementedError

    def is_result_relevant(
        self, results: List[Result], nlq: str
    ) -> Tuple[bool, Result]:
        """
        Check if the aggregated result is relevant to the original natural language query (NLQ).
        """
        raise NotImplementedError

    def heal_fix_query(self, query: Query) -> Query:
        """
        Fix the query by looking at the error message and the query itself.
        """
        raise NotImplementedError

    def heal_regenerate_query(self, query: Query) -> Query:
        """
        Regenerate the query by trying to understand the intent of the query.
        Take reference from the previous SQL query and error message.
        """
        raise NotImplementedError
