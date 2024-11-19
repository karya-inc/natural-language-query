from typing import Literal
from pydantic import BaseModel


QueryTypeLiteral = Literal["REPORT_GENERATION", "REPORT_FEEDBACK", "QUESTION_ANSWERING"]
class QueryType(BaseModel):
    query_type: QueryTypeLiteral


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
