from fastapi import FastAPI
import logging
from typing import Optional, Generator
from fastapi import HTTPException
import json
from starlette.responses import StreamingResponse
import uuid
from text_to_sql import sql_generator


# def disable_logging():
#     logging.disable(logging.CRITICAL)

# disable_logging()


# Set up logging configuration
log_format = '%(asctime)s - %(levelname)s - %(message)s'

# Create two handlers: one for console output and one for file output
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
console_handler.setLevel(logging.INFO)

# Create file handlers for success and error logs
success_handler = logging.FileHandler('success.log')
success_handler.setFormatter(logging.Formatter(log_format))
success_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler('error.log')
error_handler.setFormatter(logging.Formatter(log_format))
error_handler.setLevel(logging.ERROR)

# Create a logger and add the handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(success_handler)
logger.addHandler(error_handler)

# Create the FastAPI app
app = FastAPI()

def generate_sql_query_responses(
    query: str,
    session_id: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Generates SQL query responses in a server-sent events format.
    
    Args:
        query: The natural language query to be processed.
        session_id: Optional session identifier for tracking the query session.
        
    Yields:
        A formatted string containing the SQL query response as an event stream.
    """
    try:
        logger.info(f"Started processing query: {query}")

        sql_query_responses = sql_generator(query)

        for response in sql_query_responses:
            # Creating structured data to be sent in the event stream
            response_data = {
                'response': {
                    'type': 'reply',
                    'payload': response
                },
                'session_id': session_id
            }

            logger.info(f"Sending intermediate response: {response}")

            yield f"{json.dumps(response_data)}\n\n"

        logger.info("Completed processing the query.")

    except Exception as e:
        logger.error(f"Error while processing query: {query}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error while generating SQL queries.")
    

@app.get("/chat")
async def stream_sql_query_responses(query: str,
    session_id: Optional[str] = None
) -> StreamingResponse:
    """
    Endpoint to stream SQL query responses as Server-Sent Events (SSE).
    If session_id is not provided, a new one will be generated.
    
    Args:
        query: The natural language query to process.
        session_id: Optional session identifier; if not provided, one will be generated.
    
    Returns:
        StreamingResponse: The response streamed as Server-Sent Events.
    """
    try:
        # If no session_id is provided, generate a new UUID for the session
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        # Returning the StreamingResponse with the proper media type for SSE
        logger.info(f"Started streaming SQL responses for query: {query}")
        response = StreamingResponse(
            generate_sql_query_responses(query, session_id),
            media_type="text/event-stream"
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while processing query: {query} with session_id: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream SQL query responses.")