from fastapi import FastAPI, HTTPException, Request
from starlette.responses import StreamingResponse
from typing import Optional
import json
import uuid
from logger import setup_logging, disable_logging
from response_generator import generate_response
from chat_history import create_chat_history_table, get_chat_history
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.responses import JSONResponse


load_dotenv()

# disable_logging()

# Set up logging configuration
logger = setup_logging('server', 'server_success.log', 'server_error.log')


# Create the FastAPI app
app = FastAPI()


# Configure CORS
allowed_origin = os.getenv("CORS_ORIGINS", "").split(" ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request bodies
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    type: Optional[str] = "report"

class HistoryRequest(BaseModel):
    session_id: str


@app.post("/chat")
async def stream_sql_query_responses(
    chat_request: ChatRequest,
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    If type is not provided, it will be set to "report".
    
    The request body should contain:
    - query: The natural language query to process.
    - session_id: Optional session identifier; if not provided, one will be generated.
    - type: Optional type of query response (default is "report").
    
    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """

    try:
        query = chat_request.query
        session_id = chat_request.session_id
        type = chat_request.type

        # If no session_id is provided, generate a new UUID for the session
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        # Create chat history table for this session (if not already created)
        create_chat_history_table()
        logger.info("Chat history table created (if not exists).")

        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {query}")
        response = StreamingResponse(
            generate_response(query, session_id, type),
            media_type="text/event-stream"
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while processing query: {query} with session_id: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream SQL query responses.")
    

@app.post("/fetch_history")
async def fetch_chat_history(
    history_request: HistoryRequest
) -> JSONResponse:
    """
    Endpoint to fetch the chat history for a given session.

    The request body should contain:
        - session_id: The session identifier to fetch history.
   
    Returns:
        JSONResponse: The chat history as a JSON object.
    """
    try:
        # Extract the session_id from the request body
        session_id = history_request.session_id

        # Log the start of chat history retrieval
        logger.info(f"Fetching chat history for session: {session_id}")

        # Fetch the chat history
        chat_history = get_chat_history(session_id)

        logger.info("Chat history successfully fetched.")
        return JSONResponse(content={"history": chat_history})

    except Exception as e:
        logger.error(f"Error while retrieving chat history for session: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history.")