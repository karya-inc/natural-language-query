from dotenv import load_dotenv

load_dotenv()

import os
import uuid
from typing import Annotated, Optional, List
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException, Depends
from starlette.responses import StreamingResponse
from auth.oauth import OAuth2Phase2Payload
from dependencies.auth import TokenVerificationResult, verify_token, auth_handler
from utils.logger import get_logger
from controllers.sql_response import sql_response, chat_history
from fastapi.middleware.cors import CORSMiddleware
from db.db_queries import ChatHistory
from db.config import Config
from db.session import Database
from sqlalchemy.orm import Session

config = Config()
db = Database(config)

# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = os.getenv("CORS_ORIGINS", "").split(" "),
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
    db: Session = Depends(get_db)

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
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    If type is not provided, it will be set to "report".

    Args:
        query: The natural language query to process.
        session_id: Optional session identifier; if not provided, one will be generated.
        type: Optional type of query response.

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

    # user_id comes from auth dependency
    #get user id from token

    try:
        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {chat_request.query}")
        response = StreamingResponse(
            sql_response(chat_request.user_id, chat_request.query, session_id),
            media_type="text/event-stream"
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while processing query: {chat_request.query} with session_id: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream SQL query responses.")


@app.get("/fetch_history")
async def get_chat_history(db: Session=Depends(get_db)) -> List[ChatHistory]:
    """
    Get chat history for the user

    Returns:
       Chat history
    """
    # Get user information from dependency injection
    # send it forward to retireve the data

    # get user_id from token

    try:
        # Log the start of chat history streaming
        logger.info(f"User chat history for user_id: {user_id}")

        # Create a StreamingResponse for the chat history generator
        response = chat_history(user_id, db)

        logger.info("Chat history for user return successfully!!")
        return response

    except Exception as e:
        logger.error(f"Error while retrieving chat history for user_id: {user_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream chat history.")