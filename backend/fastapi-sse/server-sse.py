import uuid
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
from logger import setup_logging, disable_logging
from response_generator import generate_response
from fastapi.middleware.cors import CORSMiddleware
from chat_history import create_chat_history_table, get_chat_history

# Create the FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging configuration
logger = setup_logging('server', 'server_success.log', 'server_error.log')

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    type: Optional[str] = None

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
    print("query", chat_request.query)
    print("session_id", chat_request.session_id)
    print("type", chat_request.type)

    # If no session_id is provided, generate a new UUID for the session
    if not chat_request.session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
    else:
        session_id = chat_request.session_id

    try:
        # Create chat history table for this session (if not already created)
        create_chat_history_table()
        logger.info("Chat history table created (if not exists).")

        # If no type is provided, set it to default option of "report"
        if not chat_request.type:
            type = "report"

        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {chat_request.query}")
        response = StreamingResponse(
            generate_response(chat_request.query, session_id, type),
            media_type="text/event-stream"
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while processing query: {chat_request.query} with session_id: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream SQL query responses.")


@app.get("/fetch_history")
async def stream_chat_history(session_id: str) -> StreamingResponse:
    """
    Endpoint to stream the chat history for a given session using Server-Sent Events (SSE).

    Args:
        session_id: The session identifier to fetch history.

    Returns:
        StreamingResponse: The chat history streamed as Server-Sent Events (SSE).
    """
    try:
        # Log the start of chat history streaming
        logger.info(f"Started streaming chat history for session: {session_id}")

        # Create a StreamingResponse for the chat history generator
        response = StreamingResponse(
            get_chat_history(session_id),
            media_type="text/event-stream"
        )

        logger.info("Chat history streaming successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while retrieving chat history for session: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream chat history.")