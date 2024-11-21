from dataclasses import dataclass
from db.db_queries import ChatHistoryResponse, get_chat_history
from dependencies.auth import AuthenticatedUserInfo
from executor.config import AgentConfig
from executor.core import NLQExecutor
from executor.status import AgentStatus
from agents.azure_openai import AzureAIAgentTools
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from typing import AsyncIterator, List, Literal
from sqlalchemy.orm import Session
from uuid import UUID
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
    type: Literal["TEXT", "TABLE"]
    payload: str | List[dict]


async def nlq_sse_wrapper(
    user_info: AuthenticatedUserInfo, query: str, session_id: str
) -> AsyncIterator[str]:
    async for event in do_nlq(user_info, query, session_id):
        yield json.dumps(event.__dict__)


async def do_nlq(
    user_info: AuthenticatedUserInfo, query: str, session_id: str
) -> AsyncIterator[NLQUpdateEvent | NLQResponseEvent]:
    # Log info
    logger.info(f"Generating sql response for query : {query}")

    events = asyncio.Queue[NLQUpdateEvent]()

    def update_callback(status: AgentStatus):
        # Push the status to the event queue without awaiting
        asyncio.create_task(
            events.put(NLQUpdateEvent(kind="UPDATE", status=status.value))
        )

    config = AgentConfig(update_callback=update_callback, user_info=user_info)

    agent = AzureAIAgentTools()

    nlq_executor = (
        NLQExecutor()
        .with_tools(agent)
        .with_config(config)
        .with_catalogs(parsed_catalogs.catalogs)
    )

    agentic_loop_future = asyncio.create_task(nlq_executor.execute(query))

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
    if isinstance(result, str):
        yield NLQResponseEvent(kind="RESPONSE", type="TEXT", payload=result)

    if isinstance(result, list):
        yield NLQResponseEvent(kind="RESPONSE", type="TABLE", payload=result)

    logger.info("NLQ Completed")
    return


def chat_history(user_id: str, session_id:int ,db: Session) -> List[ChatHistoryResponse]:
    # Log info
    logger.info(f"History for user_id: {user_id} is requested!")
    return get_chat_history(user_id, db)


def get_session_history(
    session_id: UUID, user_id: str, db: Session
) -> List[ChatSessionHistory]:
    # Log info
    logger.info(
        f"History for session_id: {session_id} is requested! for user {user_id}"
    )
    return get_user_session_history(session_id, user_id, db)
