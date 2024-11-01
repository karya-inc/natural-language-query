from utils.gemini_service import sql_generator
from utils.logger import get_logger
from typing import Generator
from typing import List
from db.db_queries import store_query, get_chat_history, ChatHistory

def sql_response(query: str, session_id: str) -> Generator:
    # Log info

    # Send the query to sql generator

    # Store chat in sql table with session id

    pass


def chat_history(user_id: str) -> List[ChatHistory]:
    # Log info


    # Get chat history from get_chat_history

    pass