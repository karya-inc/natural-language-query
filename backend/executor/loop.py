from typing import Any, Callable, List

from executor.config import AgentConfig

from .catalog import Catalog
from .state import AgentState
from .status import AgentStatus
from .tools import AgentTools


def agentic_loop(
    nlq: str,
    catalogs: List[Catalog],
    tools: AgentTools,
    config: AgentConfig,
    execute_query: Callable,
) -> Any:
    state = AgentState(nlq=nlq)

    def send_update(status: AgentStatus):
        if config.update_callback:
            config.update_callback(status)

    turns = 0
    while True:
        if turns > 10:
            raise Exception("Agentic loop did not converge")
        turns += 1

        if not state.relevant_catalogs:
            send_update(AgentStatus.CATALOGING)
            state.relevant_catalogs = tools.analyze_catalogs(state.nlq, catalogs)

        if not state.queries:
            send_update(AgentStatus.GENERATING_QUERIES)
            state.queries = tools.generate_queries(state.nlq, state.relevant_catalogs)

        if not state.results:
            send_update(AgentStatus.EXECUTING_QUERIES)
            state.results = execute_query(state.queries)

        if len(state.results) > 1:
            send_update(AgentStatus.PROCESSING_RESULTS)
            intermediate_catalog = tools.store_intermediate_results(state.results)
            aggregate_query = tools.generate_aggregate_query(
                state.results, intermediate_catalog
            )
            state.results = execute_query([aggregate_query])

        send_update(AgentStatus.EVALUATING_RESULTS)
        is_sufficient, result = tools.is_result_relevant(state.results, state.nlq)
        if is_sufficient:
            state.final_formatted_result = tools.format_result(state.nlq, result)
            send_update(AgentStatus.TASK_COMPLETED)
            return state.final_formatted_result
