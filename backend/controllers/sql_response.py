from dataclasses import dataclass
from db.db_queries import ChatHistory, ChatSessionHistory, get_chat_history, get_user_session_history
from executor.config import AgentConfig
from executor.loop import agentic_loop
from executor.status import AgentStatus
from executor.tools import GPTAgentTools
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from typing import AsyncIterator, List, Literal
from sqlalchemy.orm import Session
from uuid import UUID
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


async def do_nlq(
    user_id: str, query: str, session_id: str
) -> AsyncIterator[NLQUpdateEvent | NLQResponseEvent]:
    # Log info
    logger.info(f"Generating sql response for query : {query}")

    events = asyncio.Queue[NLQUpdateEvent]()

    def update_callback(status: AgentStatus):
        # Push the status to the event queue without awaiting
        asyncio.create_task(
            events.put(NLQUpdateEvent(kind="UPDATE", status=status.value))
        )

    agent_config = AgentConfig(update_callback=update_callback)

    agent_tools = GPTAgentTools()

    agentic_loop_future = asyncio.to_thread(
        agentic_loop,
        nlq=query,
        catalogs=parsed_catalogs.catalogs,
        tools=agent_tools,
        config=agent_config,
        # TODO: Implement execute_query
        execute_query=lambda x: None,
    )

    while True:
        event = await events.get()
        if event.status == AgentStatus.TASK_COMPLETED:
            break

        yield event

    result = await agentic_loop_future

    # Store chat in sql table with session id
    # create_session_and_query(user_id, query, ai_response)
    if isinstance(result, str):
        yield NLQResponseEvent(kind="RESPONSE", type="TEXT", payload=result)

    if isinstance(result, list):
        yield NLQResponseEvent(kind="RESPONSE", type="TABLE", payload=result)


def chat_history(user_id: str, db: Session) -> List[ChatHistory]:
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
