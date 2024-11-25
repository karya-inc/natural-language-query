from typing import Literal, Optional
from pydantic import BaseModel


QueryTypeLiteral = Literal[
    "REPORT_GENERATION", "REPORT_FEEDBACK", "QUESTION_ANSWERING", "CASUAL_CONVERSATION"
]


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


class IsResultRelevant(BaseModel):
    relevance_score: float
    reason: Optional[str]
