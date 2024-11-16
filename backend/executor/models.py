from typing import Literal
from pydantic import BaseModel


class QueryType(BaseModel):
    query_type: Literal["QUESTION_ANSWERING", "REPORT_GENERATION"]


class RelevantCatalog(BaseModel):
    requires_multiple_catalogs: bool
    database_name: str


class NLQIntent(BaseModel):
    intent: str


class RelevantTables(BaseModel):
    tables: list[str]


class GeneratedQueryList(BaseModel):
    queries: list[str]


class AggregatedQuery(BaseModel):
    query: str

class HealedQuery(BaseModel):
    query: str
