from executor.catalog import Catalog
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from executor.models import IsResultRelevant
from rbac.check_permissions import ColumnScope

QueryType = Literal["QUESTION_ANSWERING", "REPORT_GENERATION"]

QueryResults = list[dict[str, Any]]


@dataclass
class AgentState:
    nlq: str
    intent: str
    active_role: str
    query_type: QueryType
    scopes: list[ColumnScope] = field(default_factory=list)
    relevant_catalog: Optional[Catalog] = field(default=None)
    relevant_tables: Optional[dict[str, Any]] = field(default=None)
    categorical_tables: dict[str, QueryResults] = field(default_factory=dict)
    table_sample_rows: dict[str, QueryResults] = field(default_factory=dict)
    query: Optional[str] = field(default=None)
    final_result: Optional[QueryResults] = field(default=None)
    result_relevance: Optional[IsResultRelevant] = field(default=None)
