from typing import Any, List, cast

from executor.config import AgentConfig

from executor.errors import UnRecoverableError
from utils.query_pipeline import QueryExecutionPipeline, QueryExecutionSuccessResult

from executor.catalog import Catalog
from executor.state import AgentState
from executor.status import AgentStatus
from executor.tools import AgentTools
from utils.logger import get_logger
import time
import sqlglot
import sqlglot.expressions as exp

from utils.redis import get_cached_categorical_values, get_cached_sample_rows, get_cached_sample_rows

TURN_LIMIT = 5
MAX_HEALING_ATTEMPTS = 5
FAILURE_RETRY_DELAY = 0.2
INTERMIDIATE_RESULT_LIMIT = 5

logger = get_logger("[AGENTIC LOOP]")


async def execute_query_with_healing(
    state: AgentState,
    query: str,
    tools: AgentTools,
    config: AgentConfig,
    set_limit: bool,
):
    assert state.relevant_catalog, "Relevant catalog not set"

    query_pipeline = QueryExecutionPipeline(
        catalog=state.relevant_catalog,
        active_role=config.user_info.role,
        scopes=config.user_info.scopes,
    )

    query_to_execute = query

    if set_limit:
        query_to_execute = (
            cast(
                exp.Query,
                sqlglot.parse_one(query_to_execute),
            )
            .limit(INTERMIDIATE_RESULT_LIMIT)
            .sql()
        )

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
) -> Any:
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

                for table_name, table_info in state.relevant_catalog.schema.items():
                    if table_info.get("is_categorical"):
                        categorical_info = get_cached_categorical_values(
                            state.relevant_catalog, table_name
                        )
                        categorical_tables[table_name] = categorical_info

                state.relevant_tables = relevant_tables
                state.categorical_tables = categorical_tables

            if len(state.queries) == 0:
                send_update(AgentStatus.GENERATING_QUERIES)
                # Generate queries
                state.queries = await tools.generate_queries(state)
                if len(state.queries) == 0:
                    raise Exception("Failed to generate queries")

            if len(state.intermediate_results) == 0:
                send_update(AgentStatus.EXECUTING_QUERIES)
                # Execute the queries
                for query in state.queries:
                    if query not in state.intermediate_results:
                        state.intermediate_results[query] = (
                            await execute_query_with_healing(
                                state=state,
                                query=query,
                                tools=tools,
                                set_limit=True,
                                config=config,
                            )
                        )

            if len(state.queries) == 1:
                state.aggregate_query = state.queries[0]

            if not state.aggregate_query:
                send_update(AgentStatus.REFINING_QUERY)
                # Generate the aggregate query
                state.aggregate_query = await tools.generate_aggregate_query(
                    state.intermediate_results, state.relevant_tables
                )

            if not state.final_result:
                send_update(AgentStatus.EXECUTE_REFINED_QUERY)
                # Execute the aggregate query
                state.final_result = await execute_query_with_healing(
                    state=state,
                    query=state.aggregate_query,
                    tools=tools,
                    set_limit=False,
                    config=config,
                )

            send_update(AgentStatus.TASK_COMPLETED)
            return state.final_result

        except UnRecoverableError as e:
            logger.error(f"Unrecoverable error in agentic loop: {e}")
            send_update(AgentStatus.TASK_FAILED)
            raise e
        except Exception as e:
            turns += 1
            logger.error(f"Error in agentic loop: {e}")
            logger.info(f"Retrying in {FAILURE_RETRY_DELAY} seconds...")
            time.sleep(FAILURE_RETRY_DELAY)
            raise e
