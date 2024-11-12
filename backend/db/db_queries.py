from sqlalchemy.orm import Session
from .models import User, UserQuery, UserSession
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional

# Pydantic Models
class ChatHistory(BaseModel):
    user_query: str
    session_id: UUID

class ChatSessionHistory(BaseModel):
    session_id: str
    user_queries: str
    ai_responses: str

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
    Returns all chat history from the user, including session ID and user query, sorted by timestamp.

    Args:
        user_id (str): Unique user ID stored in the database.

    Returns:
        List[ChatHistory]: Returns sorted chat history of the user.
    """

    user_queries = (
        db_session.query(UserQuery)
        .join(UserSession, UserQuery.session_id == UserSession.session_id)
        .filter(UserSession.user_id == user_id)
        .order_by(UserQuery.timestamp)
        .all()
    )

    chat_history = [
        ChatHistory(user_query=query.user_query, session_id=query.session_id)
        for query in user_queries
    ]

    return chat_history


def get_user_session_history(session_id: UUID, user_id: str, db_session) -> List[ChatSessionHistory]:
    """
    Returns chat history from the user, for the provided session ID.

    Args:
        session_id(uuid): UUID of the session.
        user_id (str): Unique user ID stored in the database.
        db_session(DB session): Database session object.

    Returns:
        List[ChatHistory]: Returns chat history of the user for session id provided.
    """
    # Check if user exists
    user = get_user(db_session, user_id)
    if user is None:
        return []

    user_queries = (
        db_session.query(UserQuery)
        .filter(UserQuery.session_id == session_id)
        .all()
        )

    chat_history = [
        ChatSessionHistory(
            session_id=query.session_id,
            user_queries=query.user_query,
            ai_responses=query.ai_response
        )
        for query in user_queries
        ]

    return chat_history
