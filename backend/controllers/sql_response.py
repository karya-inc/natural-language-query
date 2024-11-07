from utils.gemini_service import sql_generator
from utils.logger import get_logger
from typing import Generator
from typing import List
from db.db_queries import create_session_and_query, get_chat_history, ChatHistory
from sqlalchemy.orm import Session

logger = get_logger("NLQ-Server")


def sql_response(user_id: str, query: str, session_id: str) -> Generator:
    # Log info
    logger.info(f'Generating sql response for query : {query}')

    # Send the query to sql generator
    # ai_response = sql_generator(user_query=query)



    # Store chat in sql table with session id
    # create_session_and_query(user_id, query, ai_response)


    # return ai_response


def chat_history(user_id: str, db: Session) -> List[ChatHistory]:
    # Log info
    logger.info(f"History for user_id: {user_id} is requested!")
    return get_chat_history(user_id, db)