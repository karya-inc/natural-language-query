from text_to_sql import sql_generator
from logger import setup_logging, disable_logging
from typing import Generator
from fastapi import HTTPException
import json
from chat_history import store_chat_history


# disable_logging()

# Set up logging configuration
logger = setup_logging('response_generator', 'response_generator_success.log', 'response_generator_error.log')


def generate_response(
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

            store_chat_history(session_id, query, response.text)

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