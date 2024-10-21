import aiohttp
import asyncio
import uuid
from typing import Optional
from logger import setup_logging, disable_logging
import os
from dotenv import load_dotenv

load_dotenv()

# URL for the chat API and fetch history API
CHAT_URL = os.getenv("CHAT_ENDPOINT")  # e.g., "http://127.0.0.1:8000/chat"
HISTORY_URL = os.getenv("HISTORY_ENDPOINT")  # e.g., "http://127.0.0.1:8000/fetch_history"

# Set up logging configuration
logger = setup_logging('client', 'client_success.log', 'client_error.log')

async def fetch_chat_response(user_query: str, session_id: Optional[str] = None, type: Optional[str] = None) -> None:
    """
    Asynchronously sends a query to the chat API and processes the server-sent events (SSE).
    
    Args:
        user_query (str): The query to be sent to the API.
        session_id (Optional[str]): Optional session identifier; if not provided, one will be generated.
        type (Optional[str]): Type of query response.
    
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
            async with session.get(CHAT_URL, params=params) as response:
                # Check for valid response status and content type
                if response.status == 200 and 'text/event-stream' in response.headers.get('Content-Type', ''):
                    async for line in response.content:
                        # Decode and log non-empty lines
                        if line.strip():
                            logger.info(f"Received chat event: {line.decode('utf-8')}")
                else:
                    # Log unexpected response status and content type to error log
                    logger.error(f"Unexpected response: {response.status} - {response.headers.get('Content-Type')}")

    except aiohttp.ClientError as e:
        # Log network or request-related errors to error log
        logger.error(f"AIOHTTP error occurred: {e}")

    except Exception as e:
        # Log any other unexpected errors to error log with stack trace
        logger.exception(f"Unexpected error occurred while streaming chat: {e}")


async def fetch_chat_history(session_id: str) -> None:
    """
    Asynchronously fetches chat history for a given session ID using the fetch history API via SSE.
    
    Args:
        session_id (str): The session identifier to fetch history.
    
    Logs the retrieved chat history from the SSE stream.
    """
    params = {'session_id': session_id}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(HISTORY_URL, params=params) as response:
                if response.status == 200:
                    async for line in response.content:
                        # SSE sends empty lines between events, so skip them
                        if line.strip():
                            # Decode the SSE data from bytes to a string and log it
                            logger.info(f"Received history event: {line.decode('utf-8')}")
                else:
                    logger.error(f"Failed to fetch history: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"AIOHTTP error occurred while fetching history: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while fetching history: {e}")