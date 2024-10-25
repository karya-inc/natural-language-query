from fastapi import FastAPI, HTTPException, Request
from starlette.responses import StreamingResponse
from typing import Optional, Generator
from text_to_sql import sql_generator
import json
import uuid
from logger import setup_logging, disable_logging
from fastapi.middleware.cors import CORSMiddleware



# disable_logging()

# Set up logging configuration
logger = setup_logging('success.log', 'error.log')


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


def generate_sql_query_responses(
    query: str,
    session_id: str,
    type: str
) -> Generator[str, None, None]:
    """
    Generates SQL query responses in a server-sent events format.
    
    Args:
        query: The natural language query to be processed.
        session_id: Optional session identifier for tracking the query session.
        type: Optional type of query response.
        
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
                    'type': type,
                    'payload': response.text
                },
                'session_id': session_id
            }

            logger.info(f"Sending intermediate response: {response.text}")

            yield f"{json.dumps(response_data)}\n\n"

        logger.info("Completed processing the query.")

    except Exception as e:
        logger.error(f"Error while processing query: {query}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error while generating SQL queries.")
    

@app.api_route("/chat", methods=["GET", "POST"])
async def stream_sql_query_responses(
    request: Request,
    query: Optional[str] = None,
    session_id: Optional[str] = None,
    type: Optional[str] = None
) -> StreamingResponse:
    if request.method == "POST":
        body = await request.json()
        query = body.get("query")
        session_id = body.get("session_id")
        type = body.get("type")

    # Same logic as before
    try:
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        if not type:
            type = "report"

        logger.info(f"Started streaming SQL responses for query: {query}")
        response = StreamingResponse(
            generate_sql_query_responses(query, session_id, type),
            media_type="text/event-stream"
        )

        logger.info("Streaming response successfully started.")
        return response

    except Exception as e:
        logger.error(f"Error while processing query: {query} with session_id: {session_id}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stream SQL query responses.")