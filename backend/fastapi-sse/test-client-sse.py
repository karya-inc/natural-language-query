import aiohttp
import asyncio
import uuid
import logging
from typing import Optional


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
success_handler = logging.FileHandler('success_test.log')
success_handler.setFormatter(logging.Formatter(log_format))
success_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler('error_test.log')
error_handler.setFormatter(logging.Formatter(log_format))
error_handler.setLevel(logging.ERROR)

# Create a logger and add the handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(success_handler)
logger.addHandler(error_handler)


# URL for the chat API
URL = "http://127.0.0.1:8000/chat"


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