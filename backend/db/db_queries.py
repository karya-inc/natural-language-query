from sqlalchemy.orm import Session
from models import User, UserQuery
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

# Pydantic Models
class ChatHistory(BaseModel):
    user_query: str
    ai_response: str
    timestamp: datetime


# Query functions
def store_query(session_id, user_query, ai_response, db_session:Session):
    """
    Stores a new query and its AI response in the database

    Args:
        session_id(UUID): The ID of the session this query belongs to.
        user_query(str): The user's query text.
        ai_response(str): The AI's response text.
        db_session(Session): The SQLAlchemy ORM session.

    Returns:
        Query: The newly created Query object.
    """

    new_query = UserQuery(
        session_id=session_id,
        user_query = user_query,
        ai_response=ai_response,
        timestamp = datetime.now()
    )

    db_session.add(new_query)
    db_session.commit()

    return new_query


def get_chat_history(user_id: str, db_session: Session) -> List[ChatHistory]:
    """
    Returns chat history from the user

    Args:
        user_id(str): Unique user id stored in db

    Returns:
        ChatHistory: Returns chat history of user
    """
    user = db_session.query(User).filter(User.user_id == user_id).first()
    if user:
        queries = db_session.query(UserQuery).filter(UserQuery.session_id.in_([session.session_id for session in user.sessions])).all()
        chat_history = [ChatHistory(
            user_query=query.user_query.user_query,
            ai_response=query.ai_response.ai_response,
            timestamp=query.timestamp.timestamp
        ) for query in queries]

        # Sort the chat history by timestamp
        chat_history.sort(key=lambda item: item.timestamp)
        return chat_history
    else:
        return []
