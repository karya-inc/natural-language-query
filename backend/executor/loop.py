from dataclasses import dataclass, field
from typing import Any, List, Optional, Union, cast
from executor.config import AgentConfig
from executor.errors import UnRecoverableError
from utils.query_pipeline import QueryExecutionPipeline, QueryExecutionSuccessResult
from utils.parse_catalog import parsed_catalogs
from executor.catalog import Catalog
from executor.state import AgentState, QueryResults
from executor.status import AgentStatus
from executor.tools import AgentTools
from utils.logger import get_logger
import time

from utils.redis import get_cached_categorical_values

TURN_LIMIT = 3
MAX_HEALING_ATTEMPTS = 5
FAILURE_RETRY_DELAY = 1

logger = get_logger("[AGENTIC LOOP]")


@dataclass
class AgenticLoopQueryResult:
    result: QueryResults = field(default_factory=QueryResults)
    query: Optional[str] = field(default=None)


@dataclass
class AgenticLoopFailure(Exception):
    reason: str


async def execute_query_with_healing(
    state: AgentState,
    query: str,
    tools: AgentTools,
    config: AgentConfig,
):
    assert state.relevant_catalog, "Relevant catalog not set"

    query_pipeline = QueryExecutionPipeline(
        catalog=state.relevant_catalog,
        active_role=config.user_info.role,
        scopes=config.user_info.scopes,
    )

    query_to_execute = query

    healing_attempts = 0
    while True:
        if healing_attempts >= MAX_HEALING_ATTEMPTS:
            raise UnRecoverableError("Failed to heal query")

        execution_result = query_pipeline.execute(query_to_execute)
        if isinstance(execution_result, QueryExecutionSuccessResult):
            return execution_result.result

        if not execution_result.recoverable:
            raise UnRecoverableError(execution_result.reason)

        # Attempt to heal the query
        healing_attempts += 1
        if healing_attempts % 3 == 0:
            # Couldn't fix after 2mes, try to regenerate the query
            query_to_execute = await tools.heal_fix_query(
                query_to_execute, state, execution_result
            )
        else:
            query_to_execute = await tools.heal_regenerate_query(
                query_to_execute, state, execution_result
            )


async def agentic_loop(
    nlq: str,
    catalogs: List[Catalog],
    tools: AgentTools,
    config: AgentConfig,
) -> Union[AgenticLoopQueryResult, AgenticLoopFailure]:
    def send_update(status: AgentStatus):
        logger.info(status.value)
        if config.update_callback:
            config.update_callback(status)

    send_update(AgentStatus.ANALYZING_INTENT)
    intent = await tools.analaze_nlq_intent(nlq)

    state = AgentState(
        nlq=nlq,
        intent=intent,
        query_type="REPORT_GENERATION",
        active_role=config.user_info.role,
    )

    turns = 0

    while True:
        if turns >= TURN_LIMIT:
            raise Exception("Agentic loop did not converge")

        try:

            if len(catalogs) == 0:
                raise UnRecoverableError("No catalogs available")

            if len(catalogs) == 1:
                state.relevant_catalog = catalogs[0]

            # Get the relevant catalog
            if not state.relevant_catalog:
                send_update(AgentStatus.CATALOGING)
                relevant_catalog_name = await tools.get_relevant_catalog(nlq, catalogs)
                state.relevant_catalog = next(
                    catalog
                    for catalog in catalogs
                    if catalog.name == relevant_catalog_name
                )

            state.scopes = config.user_info.scopes.get(state.relevant_catalog.name, [])

            if not state.relevant_tables:
                # Get the relevant table names
                send_update(AgentStatus.CATALOGING)
                relevant_table_names = await tools.get_relevant_tables(
                    nlq, state.relevant_catalog
                )

                relevant_tables = {}
                categorical_tables = {}
                json_schema = parsed_catalogs.json_schema

                relevant_tables_schemas = filter(
                    lambda x: x[0] in relevant_table_names,
                    state.relevant_catalog.schema.items(),
                )

                for table_name, table_info in relevant_tables_schemas:
                    if table_info.get("is_categorical"):
                        categorical_info = get_cached_categorical_values(
                            state.relevant_catalog, table_name
                        )
                        categorical_tables[table_name] = categorical_info

                    for column in table_info["columns"]:
                        column = cast(dict[str, Any], column)
                        json_schema_id = column.get("json_schema_id")

                        if json_schema_id and json_schema_id in json_schema:
                            column["schema"] = json_schema[json_schema_id]

                    relevant_tables[table_name] = table_info
                state.relevant_tables = relevant_tables
                state.categorical_tables = categorical_tables

            if not state.query:
                send_update(AgentStatus.GENERATING_QUERIES)
                # Generate queries
                state.query = await tools.generate_queries(state)
                if not state.query:
                    raise Exception("Failed to generate queries")

            if not state.final_result:
                send_update(AgentStatus.EXECUTE_REFINED_QUERY)
                # Execute the aggregate query
                state.final_result = await execute_query_with_healing(
                    state=state,
                    query=state.query,
                    tools=tools,
                    config=config,
                )

            send_update(AgentStatus.TASK_COMPLETED)
            return AgenticLoopQueryResult(result=state.final_result, query=state.query)

        except UnRecoverableError as e:
            logger.error(f"Unrecoverable error in agentic loop: {e}")
            send_update(AgentStatus.TASK_FAILED)
            return AgenticLoopFailure(reason=e.message)
        except Exception as e:
            turns += 1
            logger.error(f"Error in agentic loop: {e}")
            logger.info(f"Retrying in {FAILURE_RETRY_DELAY} seconds...")
            time.sleep(FAILURE_RETRY_DELAY)
