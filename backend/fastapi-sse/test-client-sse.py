import aiohttp
import asyncio
import uuid
from typing import Optional
from logger import setup_logging, disable_logging
import os
from dotenv import load_dotenv

load_dotenv()

# URL for the chat API
URL = os.getenv("ENDPOINT")  # "http://127.0.0.1:8000/chat"


# disable_logging()

# Set up logging configuration
logger = setup_logging('client_success.log', 'client_error.log')


async def async_get_event(user_query: str, session_id: Optional[str] = None, type: Optional[str] = None) -> None:
    """
    Asynchronously sends a query to the chat API and processes the server-sent events (SSE).
    
    Args:
        user_query (str): The query to be sent to the API.
        session_id (Optional[str]): Optional session identifier; if not provided, one will be generated.
    
    Logs the server-sent events received in response to the query.
    """
    # Prepare the request parameters
    params = {'query': user_query}
    if session_id:
        params['session_id'] = session_id
    if type:
        params['type'] = type

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, params=params) as response:
                # Check for valid response status and content type
                if response.status == 200 and 'text/event-stream' in response.headers.get('Content-Type', ''):
                    async for line in response.content:
                        # Decode and log non-empty lines
                        if line.strip():
                            logger.info(f"Received event: {line.decode('utf-8')}")
                else:
                    # Log unexpected response status and content type to error log
                    logger.error(f"Unexpected response: {response.status} - {response.headers.get('Content-Type')}")

    except aiohttp.ClientError as e:
        # Log network or request-related errors to error log
        logger.error(f"AIOHTTP error occurred: {e}")

    except Exception as e:
        # Log any other unexpected errors to error log with stack trace
        logger.exception(f"Unexpected error occurred: {e}")


async def main() -> None:
    """
    Main function to run the query and handle the session.
    """
    # Simulate user-query provided by the user at frontend
    user_query = "What is the total sales for last month?"
    
    # Simulate session-id provided by system at frontend, which will be None as the session starts 
    session_id = None

    # Simulate type provided by the system at frontend
    type = "reply" # None or "report" or "reply"
    
    # Perform the API request and handle exceptions gracefully
    await async_get_event(user_query, session_id, type)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())