from typing import Any, Callable, List

from executor.config import AgentConfig
from executor.errors import UnRecoverableError
from utils.query_pipeline import QueryExecutionResult, QueryExecutionSuccessResult

from executor.catalog import Catalog
from executor.state import AgentState
from executor.status import AgentStatus
from executor.tools import AgentTools
from utils.logger import get_logger
import time

TURN_LIMIT = 5
MAX_HEALING_ATTEMPTS = 5
FAILURE_RETRY_DELAY = 2

logger = get_logger("[AGENTIC LOOP]")


def execute_query_with_healing(
    state: AgentState,
    query: str,
    tools: AgentTools,
    set_limit: bool,
    execute_query: Callable[[str], QueryExecutionResult],
):
    query_to_execute = query

    healing_attempts = 0
    while True:

        execution_result = execute_query(query_to_execute)
        if isinstance(execution_result, QueryExecutionSuccessResult):
            return execution_result.result

        if not execution_result.recoverable:
            raise Exception(execution_result.reason)

        # Attempt to heal the query
        healing_attempts += 1
        if healing_attempts % 2 == 0:
            query_to_execute = tools.heal_fix_query(query_to_execute)
        else:
            query_to_execute = tools.heal_regenerate_query(state, query_to_execute)


def agentic_loop(
    nlq: str,
    catalogs: List[Catalog],
    tools: AgentTools,
    config: AgentConfig,
    execute_query: Callable,
) -> Any:
    def send_update(status: AgentStatus):
        if config.update_callback:
            config.update_callback(status)

    send_update(AgentStatus.ANALYZING_INTENT)
    intent = tools.analaze_nlq_intent(nlq)
    nlq_type = tools.analyze_query_type(intent)

    if nlq_type == "QUESTION_ANSWERING":
        return tools.answer_question(intent)

    # Handle report generation
    assert (
        nlq_type == "REPORT_GENERATION"
    ), "Unknown query type - Expected REPORT_GENERATION"

    state = AgentState(nlq=nlq, intent=intent, query_type=nlq_type)

    turns = 0

    while True:
        if turns >= TURN_LIMIT:
            raise Exception("Agentic loop did not converge")

        try:
            # Get the relevant catalog
            if not state.relevant_catalog:
                send_update(AgentStatus.CATALOGING)
                relevant_catalog_name = tools.get_relevant_catalog(nlq, catalogs)
                state.relevant_catalog = next(
                    catalog
                    for catalog in catalogs
                    if catalog.name == relevant_catalog_name
                )

            if not state.relevant_tables:
                # Get the relevant table names
                send_update(AgentStatus.CATALOGING)
                relevant_table_names = tools.get_relevant_tables(
                    nlq, state.relevant_catalog
                )
                relevant_tables = {}
                for table_name, table_info in state.relevant_catalog.schema.items():
                    if table_name in relevant_table_names:
                        relevant_tables[table_name] = table_info

                state.relevant_tables = relevant_tables

            if len(state.queries) == 0:
                send_update(AgentStatus.GENERATING_QUERIES)
                # Generate queries
                state.queries = tools.generate_queries(nlq, state.relevant_tables)
                if len(state.queries) == 0:
                    raise Exception("Failed to generate queries")

            if len(state.intermediate_results) == 0:
                send_update(AgentStatus.EXECUTING_QUERIES)
                # Execute the queries
                for query in state.queries:
                    if query not in state.intermediate_results:
                        state.intermediate_results[query] = execute_query_with_healing(
                            state=state,
                            query=query,
                            tools=tools,
                            set_limit=True,
                            execute_query=execute_query,
                        )

            if not state.aggregate_query:
                send_update(AgentStatus.REFINING_QUERY)
                # Generate the aggregate query
                state.aggregate_query = tools.generate_aggregate_query(
                    state.intermediate_results
                )

            if not state.final_result:
                send_update(AgentStatus.EXECUTE_REFINED_QUERY)
                # Execute the aggregate query
                state.final_result = execute_query_with_healing(
                    state=state,
                    query=state.aggregate_query,
                    tools=tools,
                    set_limit=False,
                    execute_query=execute_query,
                )

            send_update(AgentStatus.TASK_COMPLETED)
            return state.final_result

        except Exception as e:
            turns += 1
            logger.error(f"Error in agentic loop: {e}")
            logger.info(f"Retrying in {FAILURE_RETRY_DELAY} seconds...")
            time.sleep(FAILURE_RETRY_DELAY)
            pass
