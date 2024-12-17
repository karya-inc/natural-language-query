import json
from dataclasses import dataclass, field
from typing import Any, Optional, Union
from db.models import ExecutionLog
from dataclass_wizard import JSONWizard


@dataclass
class QueryExecutionSuccessResult:
    result: list[dict]
    execution_log: ExecutionLog

    def to_dict(self) -> dict:
        return {
            "result": self.result,
            "execution_log": self.execution_log.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict):
        return QueryExecutionSuccessResult(
            result=data["result"],
            execution_log=ExecutionLog.from_dict(data["execution_log"]),
        )

    @staticmethod
    def from_json(data: str):
        return QueryExecutionSuccessResult.from_dict(json.loads(data))


@dataclass
class QueryExecutionFailureResult(JSONWizard):
    reason: Any
    recoverable: bool = True
    context: Optional[dict] = field(default=None)


QueryExecutionResult = Union[
    QueryExecutionSuccessResult, QueryExecutionFailureResult, ExecutionLog
]
