from sqlalchemy.orm import Session
from .models import User, UserQuery, UserSession
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

# Pydantic Models
class ChatHistory(BaseModel):
    user_query: str
    ai_response: str
    timestamp: datetime

def get_user(db: Session, user_id: str) -> Optional[User]:
    """
    Check if user exists in database.

    Args:
        db: SQLAlchemy session
        user_id: User identifier

    Returns:
        User object if found, None otherwise
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(db: Session, user_id: str) -> Optional[User]:
    """
    Create a new user entry.

    Args:
        db: SQLAlchemy session
        user_id: User identifier

    Returns:
        Created User object
    """
    try:
        user = User(user_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        return None

def get_or_create_user(db: Session, user_id: str) -> Optional[User]:
    """
    Get existing user or create new one if doesn't exist.

    Args:
        db: SQLAlchemy session
        user_id: User identifier

    Returns:
        User object
    """
    user = get_user(db, user_id)
    if user is None:
        user = create_user(db, user_id)
    return user


def create_session_and_query(
    db: Session,
    user_id: str,
    user_query: str,
    ai_response: str
) -> Optional[UserQuery]:
    """
    Create a new session for user and store query/response.

    Args:
        db: SQLAlchemy session
        user_id: User identifier
        user_query: Query text from user
        ai_response: Response from AI

    Returns:
        Created UserQuery object
    """
    try:
        # Get or create user
        user = get_or_create_user(db, user_id)
        if user is None:
            return None

        # Create new session
        session = UserSession(user_id=user_id)
        db.add(session)

        # Create query entry
        query = UserQuery(
            session_id=session.session_id,
            user_query=user_query,
            ai_response=ai_response
        )
        db.add(query)

        db.commit()
        db.refresh(query)
        return query
    except Exception as e:
        db.rollback()
        print(f"Error creating session and query: {e}")
        return None



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
            user_query=query.user_query,
            ai_response=query.ai_response,
            timestamp=query.timestamp
        ) for query in queries]

        # Sort the chat history by timestamp
        chat_history.sort(key=lambda item: item.timestamp)
        return chat_history
    else:
        return []
