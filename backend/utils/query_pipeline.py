from dataclasses import dataclass, field
from typing import List, Optional, Union
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from executor.catalog import Catalog
from sqlalchemy import Engine, create_engine, text
from rbac.check_permissions import ColumnScope, check_query_privilages
from urllib.parse import quote


logger = get_logger("[QUERY_PIPELINE]")


@dataclass
class QueryExecutionSuccessResult:
    result: list[dict]


@dataclass
class QueryExecutionFailureResult:
    reason: str
    recoverable: bool
    context: Optional[dict] = field(default=None)


QueryExecutionResult = Union[QueryExecutionSuccessResult, QueryExecutionFailureResult]


class QueryExecutionPipeline:
    catalog: Catalog
    engine: Engine
    active_role: str
    scopes: dict[str, List[ColumnScope]]

    def __init__(
        self,
        catalog: Catalog,
        active_role: str,
        scopes: dict[str, List[ColumnScope]] = {},
    ):
        self.catalog = catalog
        self.scopes = scopes
        self.active_role = active_role

        if self.catalog.provider == "postgres":
            host = quote(self.catalog.connection_params["host"])
            dbname = quote(self.catalog.connection_params["dbname"])
            user = quote(self.catalog.connection_params["user"])
            password = quote(self.catalog.connection_params["password"])
            port = self.catalog.connection_params.get("port", 5432)

            # Setup connection to postgres
            engine = create_engine(
                f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            )
            self.engine = engine

        else:
            raise NotImplementedError("Only postgres is supported at the moment")

    def execute(self, query: str) -> QueryExecutionResult:
        table_privilages = parsed_catalogs.database_privileges[self.catalog.name]
        try:
            query_validation_result = check_query_privilages(
                table_privilages_map=table_privilages,
                active_role=self.active_role,
                table_scopes=self.scopes,
                query=query,
            )
        except Exception as e:
            logger.error(f"Error while checking query privilages: {e}")
            return QueryExecutionFailureResult(reason=str(e), recoverable=True)

        if not query_validation_result.query_allowed:
            err = query_validation_result.err_code
            context = query_validation_result.context

            logger.warning(
                "Error occurred while checking for permissions: ",
                query_validation_result,
            )

            if not err:
                return QueryExecutionFailureResult(
                    reason="Unknown", recoverable=False, context=context
                )

            else:
                return QueryExecutionFailureResult(
                    reason=err.value,
                    context=context,
                    recoverable=True,
                )

        try:
            with self.engine.connect() as conn:
                stmt = text(query)
                result = conn.execute(stmt).fetchall()
                result_formatted = [row._asdict() for row in result]
                print(result_formatted)
                return QueryExecutionSuccessResult(result_formatted)

        except Exception as e:
            logger.error(f"Failed to execute Query: {e}")
            return QueryExecutionFailureResult(reason=str(e), recoverable=True)
