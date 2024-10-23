from fastapi import FastAPI, HTTPException, Request
from starlette.responses import StreamingResponse
from typing import Optional
import json
import uuid
from logger import setup_logging, disable_logging
from response_generator import generate_response
from chat_history import create_chat_history_table, get_chat_history
from fastapi.middleware.cors import CORSMiddleware

# disable_logging()

# Set up logging configuration
logger = setup_logging('server', 'server_success.log', 'server_error.log')


# Create the FastAPI app
app = FastAPI()
    
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/chat")
async def stream_sql_query_responses(
    request: Request,
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
        body = await request.json()
        query = body.get("query")
        session_id = body.get("session_id")
        type = body.get("type", "report")

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
async def stream_chat_history(
    request: Request
) -> StreamingResponse:
    """
    Endpoint to stream the chat history for a given session using Server-Sent Events (SSE).

    The request body should contain:
        - session_id: The session identifier to fetch history.
   
    Returns:
        StreamingResponse: The chat history streamed as Server-Sent Events (SSE).
    """
    try:
        # Extract the session_id from the request body
        body = await request.json()
        session_id = body.get("session_id")
        
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