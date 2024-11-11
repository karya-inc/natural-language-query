from dotenv import load_dotenv

load_dotenv()

import os
import uuid
from typing import Annotated, Optional, List
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Depends
from starlette.responses import StreamingResponse
from auth.oauth import OAuth2Phase2Payload
from dependencies.auth import TokenVerificationResult, verify_token, auth_handler, get_user_id
from utils.logger import get_logger
from controllers.sql_response import sql_response, chat_history, get_session_history
from fastapi.middleware.cors import CORSMiddleware
from db.db_queries import ChatHistory, ChatSessionHistory
from db.config import Config
from db.session import Database
from sqlalchemy.orm import Session
from uuid import UUID

config = Config()
db = Database(config)

# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(" "),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging configuration
logger = get_logger("NLQ-Server")


# Dependency to get database session
def get_db():
    return next(db.get_session())


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    type: Optional[str] = None


@app.get("/auth/verify")
async def verify_auth(auth: Annotated[TokenVerificationResult, Depends(verify_token)]):
    """
    Returns the token verification result
    """
    return auth.__dict__


@app.get("/auth/login_stratergy")
async def get_login_stratergy(
    code: Annotated[str | None, str, Body()] = None,
    state: Annotated[str | None, str, Body()] = None,
):
    """
    Returns information on how to login the user
    """

    payload = None
    if code:
        payload = OAuth2Phase2Payload(code=code, state=state)

    response = auth_handler.login(payload)
    return response.__dict__


@app.post("/chat")
async def stream_sql_query_responses(
    chat_request: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_user_id)]
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    If type is not provided, it will be set to "report".

    Args:
        chat_request (ChatRequest): The request containing the SQL query and optional session_id.
        db (Session): The database session.
        user_id (str): The user ID extracted from the token.

    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """

    # Dependency check to validate user

    # If no session_id is provided, generate a new UUID for the session
    if not chat_request.session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
    else:
        session_id = chat_request.session_id

    try:
        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {chat_request.query}")
        response = StreamingResponse(
            sql_response(user_id, chat_request.query, session_id),
            media_type="text/event-stream",
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(
            f"Error while processing query: {chat_request.query} with session_id: {session_id}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to stream SQL query responses."
        )


@app.get("/fetch_history")
async def get_chat_history(
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_user_id)]
) -> List[ChatHistory]:
    """
    Get chat history for the user

    Returns:
       Chat history
    """

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_id}")

        # Create a StreamingResponse for the chat history generator
        response = chat_history(user_id, db)

        logger.info("Chat history for user return successfully!!")
        return response

    except Exception as e:
        logger.error(
            f"Error while retrieving chat history for user_id: {user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to stream chat history.")

@app.get("/fetch_session_history/{session_id}")
async def get_session_history_for_user( session_id: UUID,
                                       db: Annotated[Session, Depends(get_db)],
                                       user_id: Annotated[str, Depends(get_user_id)]
                                       ) -> List[ChatSessionHistory]:
    """
    Get session id from query params and fetch the session history for the user

    Args:
        session_id (UUID): Session ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Session history
    """
    logger.info(f"Session history for session_id: {session_id}")
    try:
        response = get_session_history(session_id, user_id, db)
        logger.info("Session history for session_id return successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while retrieving session history for session_id: {session_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to get session history.")
