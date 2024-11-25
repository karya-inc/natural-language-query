from dataclasses import dataclass
from typing import Any, List, Optional, Union, cast
from db.models import UserSession
from executor.config import AgentConfig
from executor.errors import UnRecoverableError
from executor.models import QueryTypeLiteral
from rbac.check_permissions import PrivilageCheckResult
from utils.query_pipeline import QueryExecutionPipeline, QueryExecutionResult, QueryExecutionSuccessResult
from utils.parse_catalog import parsed_catalogs
from executor.catalog import Catalog
from executor.state import AgentState, QueryResults
from executor.status import AgentStatus
from executor.tools import AgentTools
from utils.logger import get_logger
import time

from utils.redis import get_cached_categorical_values, get_or_execute_query_result

TURN_LIMIT = 3
MAX_HEALING_ATTEMPTS = 5
FAILURE_RETRY_DELAY = 1

logger = get_logger("[AGENTIC LOOP]")


@dataclass
class AgenticLoopQueryResult:
    result: QueryResults
    query: str
    db_name: str


@dataclass
class AgenticLoopQuestionAnsweringResult:
    answer: str


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
    execution_result: Optional[QueryExecutionResult] = None
    while healing_attempts <= MAX_HEALING_ATTEMPTS:
        try:
            execution_result = get_or_execute_query_result(
                query_to_execute, state.relevant_catalog, query_pipeline.execute
            )

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
        except UnRecoverableError as e:
            raise e

        except Exception as e:
            logger.error(f"Error in execute_query_with_healing: {e}")
            continue

    # If the query was successfully executed, return the result
    if isinstance(execution_result, QueryExecutionSuccessResult):
        return execution_result.result

    # If there is not execution result, or it is not recoverable
    if not execution_result or not execution_result.recoverable:
        raise UnRecoverableError("Failed to get a result for the query")

    # If the permissions are not sufficient even after healing, raise UnRecoverableError
    if isinstance(execution_result.reason, PrivilageCheckResult):
        raise UnRecoverableError(
            "Failed to execute this query. You may not have the required permissions."
        )

    # Unknow error
    raise UnRecoverableError("Failed to execute this query")


async def agentic_loop(
    nlq: str,
    catalogs: List[Catalog],
    tools: AgentTools,
    config: AgentConfig,
    session: UserSession,
) -> Union[
    AgenticLoopQueryResult, AgenticLoopQuestionAnsweringResult, AgenticLoopFailure
]:
    def send_update(status: AgentStatus):
        logger.info(status.value)
        if config.update_callback:
            config.update_callback(status)

    send_update(AgentStatus.ANALYZING_INTENT)

    nlq_type: QueryTypeLiteral
    if len(session.turns) == 0:
        nlq_type = "REPORT_GENERATION"
    else:
        nlq_type = await tools.analyze_query_type(nlq, session.turns)

    intent = await tools.analaze_nlq_intent(nlq, session.turns)
    state = AgentState(
        nlq=nlq,
        intent=intent,
        query_type="REPORT_GENERATION",
        active_role=config.user_info.role,
    )

    turns = 0

    if nlq_type == "CASUAL_CONVERSATION":
        send_update(AgentStatus.TASK_FAILED)
        return AgenticLoopFailure(
            reason="Sorry, I am not trained to handle casual conversations. Please try being more specific."
        )

    if nlq_type == "QUESTION_ANSWERING":
        prev_turn = session.turns[-1]
        catalog = next(
            catalog for catalog in catalogs if catalog.name == prev_turn.database_used
        )
        send_update(AgentStatus.EXECUTING_QUERIES)
        query_pipeline = QueryExecutionPipeline(
            catalog=catalog,
            active_role=config.user_info.role,
            scopes=config.user_info.scopes,
        )
        prev_turn_result = get_or_execute_query_result(
            query=prev_turn.nlq, catalog=catalog, execute_query=query_pipeline.execute
        )

        if not isinstance(prev_turn_result, QueryExecutionSuccessResult):
            send_update(AgentStatus.TASK_FAILED)
            return AgenticLoopFailure(
                reason="Unable to find data for the previous query"
            )

        try:
            answer = await tools.answer_question(intent, prev_turn_result.result)
            send_update(AgentStatus.TASK_COMPLETED)
            return AgenticLoopQuestionAnsweringResult(answer=answer)
        except UnRecoverableError as e:
            return AgenticLoopFailure(reason=e.message)
        except Exception as e:
            return AgenticLoopFailure(reason=str(e))

    while True:
        try:
            if turns >= TURN_LIMIT:
                raise UnRecoverableError(
                    "Failed to generate a result for your query. Try rephrasing your question."
                )

            if len(catalogs) == 0:
                raise UnRecoverableError("No catalogs available")

            if len(catalogs) == 1:
                state.relevant_catalog = catalogs[0]

            # Select the relevant catalog if it is not already selected
            if not state.relevant_catalog:
                send_update(AgentStatus.CATALOGING)
                relevant_catalog_name = await tools.get_relevant_catalog(nlq, catalogs)
                state.relevant_catalog = next(
                    catalog
                    for catalog in catalogs
                    if catalog.name == relevant_catalog_name
                )

            state.scopes = config.user_info.scopes.get(state.relevant_catalog.name, [])

            # Get the relevant tables if they are not already selected
            if not state.relevant_tables:
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

            # Generate the query if it is not already generated
            if not state.query:
                send_update(AgentStatus.GENERATING_QUERIES)
                state.query = await tools.generate_queries(state)
                if not state.query:
                    raise Exception("Failed to generate queries")

            # Execute the final query if it is not already executed
            if not state.final_result:
                send_update(AgentStatus.EXECUTING_QUERIES)
                state.final_result = await execute_query_with_healing(
                    state=state,
                    query=state.query,
                    tools=tools,
                    config=config,
                )

            if not state.result_relevance:
                send_update(AgentStatus.EVALUATING_RESULTS)
                state.result_relevance = await tools.is_result_relevant(
                    state.final_result, state.intent, state.query
                )
                logger.info(f"Result relevance: {state.result_relevance}")

            relevance = state.result_relevance

            # If the result is relevant, return the result
            if relevance.relevance_score >= 7:
                send_update(AgentStatus.TASK_COMPLETED)
                return AgenticLoopQueryResult(
                    result=state.final_result,
                    query=state.query,
                    db_name=state.relevant_catalog.name,
                )

            # Try to improve the query by providing feedback to make it more relevant
            elif relevance.relevance_score >= 3:
                logger.info(
                    f"Relevance score: {relevance.relevance_score}. Refining query..."
                )
                send_update(AgentStatus.REFINING_QUERY)
                state.query = None
                state.final_result = None
                continue

            # If the result is not relevant, raise an error
            elif relevance.reason:
                logger.warning(f"Generated result is not relevant: {relevance.reason}")
                send_update(AgentStatus.TASK_FAILED)
                raise UnRecoverableError(relevance.reason)

            # If the result is not relevant and no reason is provided, raise an error
            else:
                logger.error(
                    "Failed to generate a relevant result. Reason not provided."
                )
                send_update(AgentStatus.TASK_FAILED)
                raise UnRecoverableError(
                    "Failed to generate a result for your query. Try rephrasing your question."
                )

        except UnRecoverableError as e:
            logger.error(f"Unrecoverable error in agentic loop: {e}")
            send_update(AgentStatus.TASK_FAILED)
            return AgenticLoopFailure(reason=e.message)
        except Exception as e:
            turns += 1
            logger.error(f"Error in agentic loop: {e}")
            logger.info(f"Retrying in {FAILURE_RETRY_DELAY} seconds...")
            send_update(AgentStatus.FIXING)
            time.sleep(FAILURE_RETRY_DELAY)
