from dataclasses import dataclass, field
from typing import Any, List, Optional, Union, cast
from sqlalchemy.orm import Session
from db.db_queries import create_execution_entry, get_or_create_query
from db.models import ExecutionLog
from dependencies.db import get_db_session
from executor.state import QueryResults
from queues.typed_tasks import invoke_execute_query_op
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from executor.catalog import Catalog
from rbac.check_permissions import ColumnScope, PrivilageCheckResult, check_query_privilages


logger = get_logger("[QUERY_PIPELINE]")


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


@dataclass
class QueryExecutionPipeline:
    catalog: Catalog
    user_id: str
    active_role: str
    scopes: dict[str, List[ColumnScope]]
    db_session: Session = field(init=False)

    def __post_init__(self):
        self.db_session = get_db_session()

    def check_query_privilages(self, sql_query: str) -> PrivilageCheckResult:
        table_privilages = parsed_catalogs.database_privileges[self.catalog.name]
        query_validation_result = check_query_privilages(
            table_privilages_map=table_privilages,
            active_role=self.active_role,
            table_scopes=self.scopes,
            query=sql_query,
        )
        return query_validation_result

    def check_and_execute(
        self, sql_query: str, is_background: bool = False
    ) -> QueryExecutionResult:
        query_validation_result = self.check_query_privilages(sql_query)

        if not query_validation_result.query_allowed:
            logger.warning(
                "Error occurred while checking for permissions: ",
                query_validation_result,
            )

            return QueryExecutionFailureResult(
                reason=query_validation_result,
                recoverable=True,
            )

        try:
            # Create Execution Log
            saved_query = get_or_create_query(
                self.db_session, sql_query, self.user_id, self.catalog.name
            )
            execution_entry = create_execution_entry(
                self.db_session, self.user_id, str(saved_query.sqid)
            )

            execution_result = invoke_execute_query_op(execution_entry.id, self.catalog)

            if is_background:
                return execution_entry

            result_value = cast(QueryResults, execution_result.get())
            return QueryExecutionSuccessResult(
                result=result_value, execution_log=execution_entry
            )

        except Exception as e:
            logger.error(f"Failed to execute Query: {e}")
            return QueryExecutionFailureResult(reason=str(e), recoverable=True)
