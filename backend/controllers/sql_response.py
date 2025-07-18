from dataclasses import dataclass
from db.db_queries import *
from db.models import SavedQuery, User, UserSession
from dependencies.auth import AuthenticatedUserInfo
from executor.config import AgentConfig
from executor.core import NLQExecutor
from executor.loop import (
    AgenticLoopFailure,
    AgenticLoopQueryResult,
    AgenticLoopQuestionAnsweringResult,
)
from executor.status import AgentStatus
from agents.azure_openai import AzureAIAgentTools
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from typing import AsyncIterator, List, Literal, Optional
from sqlalchemy.orm import Session
import json
import asyncio

logger = get_logger("NLQ-Server")


@dataclass
class NLQUpdateEvent:
    kind: Literal["UPDATE"]
    status: str


@dataclass
class NLQResponseEvent:
    kind: Literal["RESPONSE"]
    type: Literal["TEXT", "TABLE", "ERROR"]
    payload: str | List[dict]
    session_id: str
    query: Optional[str] = None
    sql_query_id: Optional[str] = None
    execution_id: Optional[int] = None
    turn_id: Optional[int] = None


class ExecuteQueryRequest(BaseModel):
    params: Optional[SqlQueryParams] = None


async def nlq_sse_wrapper(
    user_info: AuthenticatedUserInfo,
    query: str,
    session: UserSession,
    db_session: Session,
) -> AsyncIterator[str]:
    async for event in do_nlq(user_info, query, session, db_session):
        yield json.dumps(event.__dict__)


async def do_nlq(
    user_info: AuthenticatedUserInfo,
    nlq: str,
    session: UserSession,
    db_session: Session,
) -> AsyncIterator[NLQUpdateEvent | NLQResponseEvent]:
    # Log info
    logger.info(f"Generating sql response for query : {nlq}")

    events = asyncio.Queue[NLQUpdateEvent]()

    def update_callback(status: AgentStatus):
        # Push the status to the event queue without awaiting
        asyncio.create_task(
            events.put(NLQUpdateEvent(kind="UPDATE", status=status.value))
        )

    config = AgentConfig(update_callback=update_callback, user_info=user_info)

    agent = AzureAIAgentTools()

    nlq_executor = (
        NLQExecutor(db_session)
        .with_tools(agent)
        .with_config(config)
        .with_catalogs(parsed_catalogs.catalogs)
        .with_session(session)
    )

    agentic_loop_future = asyncio.create_task(nlq_executor.execute(nlq))

    while True:
        event = await events.get()
        if (
            event.status == AgentStatus.TASK_COMPLETED.value
            or event.status == AgentStatus.TASK_FAILED.value
        ):
            logger.info(
                f"Task completed with status: {event.status}. Exiting event loop"
            )
            break

        yield event

    logger.info("Waiting for the nlq executor to return")
    result = await agentic_loop_future

    # Store chat in sql table with session id
    # create_session_and_query(user_id, query, ai_response)
    if isinstance(result, AgenticLoopQueryResult):
        turn = store_turn(
            db_session=db_session,
            session_id=session.session_id,
            nlq=nlq,
            database_used=result.db_name,
            execution_log_id=result.execution_log.id,
        )
        yield NLQResponseEvent(
            kind="RESPONSE",
            type="TABLE",
            payload=result.result,
            session_id=str(session.session_id),
            query=result.query,
            sql_query_id=result.execution_log.query_id,
            turn_id=turn.turn_id,
        )

    if isinstance(result, AgenticLoopQuestionAnsweringResult):
        yield NLQResponseEvent(
            kind="RESPONSE",
            type="TEXT",
            payload=result.answer,
            session_id=str(session.session_id),
        )

    if isinstance(result, AgenticLoopFailure):
        yield NLQResponseEvent(
            kind="RESPONSE",
            type="ERROR",
            payload=result.reason,
            session_id=str(session.session_id),
        )

    db_session.close()
    logger.info("NLQ Completed")


def chat_history(
    db_session: Session, session_id: str, user_id: str
) -> List[ChatHistoryResponse]:
    # Log info
    logger.info(
        f"History for session_id: {session_id} is requested! for user {user_id}"
    )
    # check if session exist of the user
    session = get_session_for_user(
        db_session=db_session, user_id=user_id, session_id=session_id
    )
    if not session:
        return []
    logger.info(f"History for user_id: {user_id} is requested!")
    return get_chat_history(db_session, session_id)


def get_session_history(user_id: str, db: Session) -> List[UserSessionsResponse]:
    # Log info
    logger.info(f"History requested for user {user_id}")
    return get_history_sessions(db_session=db, user_id=user_id)


def save_fav(db: Session, user_id: str, turn_id: int, sql_query_id: str):
    # Log info
    logger.info(
        f"Saving fav query of user : {user_id} with turn_id: {turn_id} and sql_query_id: {sql_query_id}"
    )
    return save_user_fav_query(db, user_id, turn_id, sql_query_id)


def get_saved_queries_user(
    db: Session, user_id: str, filter: Optional[str]
) -> List[SavedQueriesResponse]:
    # Log info
    logger.info(f"Get saved queries for user: {user_id} is requested!")
    return get_saved_queries(db, user_id, filter_type=filter)


def save_query_for_user(
    db: Session,
    user_id: str,
    turn_id: int,
    sqid: str,
    name: str,
    description: Optional[str],
) -> Optional[SavedQuery]:
    # Log info
    logger.info(f"Save query for user: {user_id} is requested!")
    return create_saved_query(
        db_session=db,
        user_id=user_id,
        turn_id=turn_id,
        sqid=sqid,
        name=name,
        description=description,
        saved_by=user_id,
    )


def get_all_users_info(db: Session, user_id: str) -> List[User]:
    # Log info
    logger.info(f"Get all users info requested by user: {user_id}")
    return get_all_users_info(db, user_id)
