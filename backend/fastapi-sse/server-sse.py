from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
from typing import Optional, Generator
import json
import uuid
from logger import setup_logging, disable_logging
from response_generator import generate_response


# disable_logging()

# Set up logging configuration
logger = setup_logging('server_success.log', 'server_error.log')


# Create the FastAPI app
app = FastAPI()
    

@app.get("/chat")
async def stream_sql_query_responses(
    query: str,
    session_id: Optional[str] = None,
    type: Optional[str] = None
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
    try:
        # If no session_id is provided, generate a new UUID for the session
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        # If no type is provided, set it to default option of "report"
        if not type:
            type = "report" 

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