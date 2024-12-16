from dataclasses import dataclass, field
from typing import Any, Optional, Union
from db.models import ExecutionLog


@dataclass
class QueryExecutionSuccessResult:
    result: list[dict]
    execution_log: ExecutionLog


@dataclass
class QueryExecutionFailureResult:
    reason: Any
    recoverable: bool = True
    context: Optional[dict] = field(default=None)


QueryExecutionResult = Union[
    QueryExecutionSuccessResult, QueryExecutionFailureResult, ExecutionLog
]
