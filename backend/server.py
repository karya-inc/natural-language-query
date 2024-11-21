from dotenv import load_dotenv

from db.models import UserSession

load_dotenv()

import os
import uuid
from typing import Annotated, Optional, List
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Depends, Header
from starlette.responses import StreamingResponse
from auth.oauth import OAuth2Phase2Payload
from dependencies.auth import AuthenticatedUserInfo, TokenVerificationResult, get_authenticated_user_info, verify_token, auth_handler
from utils.logger import get_logger
from controllers.sql_response import chat_history, get_fav_queries_user, get_session_history, nlq_sse_wrapper, save_fav
from fastapi.middleware.cors import CORSMiddleware
from db.db_queries import ChatHistoryResponse, SavedQueriesResponse, UserSessionsResponse, create_session, get_session_for_user
from db.config import Config
from db.session import Database
from sqlalchemy.orm import Session
from uuid import UUID
from utils.parse_catalog import parsed_catalogs

parsed_catalogs.database_privileges


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
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    If type is not provided, it will be set to "report".

    Args:
        chat_request (ChatRequest): The request containing the SQL query and optional session_id.
        db (Session): The database session.
        user_info (AuthenticatedUserInfo): The user info extracted from the token after successfully authenticating.

    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """

    # Dependency check to validate user

    # If no session_id is provided, generate a new UUID for the session
    current_session: Optional[UserSession] = None
    if not chat_request.session_id:
        current_session = create_session(db, user_info.user_id)
    else:
        current_session = get_session_for_user(
            db, user_info.user_id, UUID(chat_request.session_id)
        )
        session_id = chat_request.session_id

    if not current_session:
        raise HTTPException(status_code=400, detail="Session not found for the user.")

    session_id = str(current_session.session_id)
    try:
        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {chat_request.query}")
        response = StreamingResponse(
            nlq_sse_wrapper(user_info, chat_request.query, current_session),
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
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[UserSessionsResponse]:
    """
    Get chat history for the user

    Returns:
       Chat history
    """

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_info.user_id}")

        # Create a StreamingResponse for the chat history generator
        response = get_session_history(db=db, user_id=user_info.user_id)

        logger.info("Chat history for user return successfully!!")
        return response

    except Exception as e:
        logger.error(
            f"Error while retrieving chat history for user_id: {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to stream chat history.")


@app.get("/fetch_session_history/{session_id}")
async def get_session_history_for_user(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[ChatHistoryResponse]:
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
        response = chat_history(db, session_id, user_info.user_id)
        logger.info("Session history for session_id return successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while retrieving session history for session_id: {session_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to get session history.")


@app.get("/fetch_favorite_queries")
async def get_favorite_queries(
    db: Annotated[Session, Depends(get_db)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
) -> List[SavedQueriesResponse]:
    """
    Get favorite queries for the user

    Returns:
       User favorite queries
    """

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_info.user_id}")

        # Create a StreamingResponse for the chat history generator
        response = get_fav_queries_user(db=db, user_id=user_info.user_id)

        logger.info("Return user favorite queries successfully!!")
        return response

    except Exception as e:
        logger.error(
            f"Error while returning favorite queries for user : {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to return favorite queries."
        )


@app.post("/save_favorite_query/{turn_id}/{sql_query_id}")
async def save_favorite_query(
    turn_id: int,
    sql_query_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    user_info: Annotated[AuthenticatedUserInfo, Depends(get_authenticated_user_info)],
):
    """
    Save favorite query for the user

    Args:
        turn_id (int): Turn ID
        sql_query_id (UUID): SQL Query ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        None
    """
    logger.info(
        f"Saving fav query of user : {user_info.user_id} with turn_id: {turn_id} and sql_query_id: {sql_query_id}"
    )
    try:
        response = save_fav(db, user_info.user_id, turn_id, sql_query_id)
        logger.info("Favorite query saved successfully!!")
        return response
    except Exception as e:
        logger.error(
            f"Error while saving favorite query for user : {user_info.user_id}. Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to save favorite query.")
