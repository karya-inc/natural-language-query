from typing import Any, Literal
from pydantic import BaseModel


QueryTypeLiteral = Literal[
    "REPORT_GENERATION", "REPORT_FEEDBACK", "QUESTION_ANSWERING", "CASUAL_CONVERSATION"
]

QueryResults = list[dict[str, Any]]


class QueryType(BaseModel):
    query_type: QueryTypeLiteral


class RelevantCatalog(BaseModel):
    requires_multiple_catalogs: bool
    database_name: str


class NLQIntent(BaseModel):
    intent: str


class RelevantTables(BaseModel):
    tables: list[str]


class GeneratedQuery(BaseModel):
    query: str


class HealedQuery(BaseModel):
    query: str


class QuestionAnsweringResult(BaseModel):
    answer: str


class IsQueryRelevant(BaseModel):
    is_relevant: bool
