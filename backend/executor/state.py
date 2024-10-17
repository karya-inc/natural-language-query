from .catalog import Catalog
from .query import Query
from .result import Result


from dataclasses import dataclass
from typing import Any, List


@dataclass
class AgentState:
    nlq: str
    relevant_catalogs: List[Catalog] = None
    queries: List[Query] = None
    results: List[Result] = None
    final_formatted_result: str = None
