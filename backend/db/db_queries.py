from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import User, UserSession, Turn, SqlQuery, SavedQuery
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from utils.logger import get_logger
import enum

logger = get_logger("[DATABASE_QUERIES]")


# Enums
class Roles(enum.Enum):
    USER = "user"
    BOT = "bot"


# Pydantic Models
class ChatHistoryResponse(BaseModel):
    id: int | UUID
    message: str
    role: Roles
    timestamp: datetime


def get_or_create_user(db_session: Session, user_id: str) -> User:
    """Check if a user exists; if not, create a new user."""
    try:
        user = db_session.query(User).filter_by(user_id=user_id).first()
        logger.info(f"User: {user}")
        if not user:
            logger.warning(f"User not found, creating a new user with ID: {user_id}")
            user = User(user_id=user_id)
            db_session.add(user)
            db_session.commit()
        return user
    except Exception as e:
        logger.error(f"Error getting or creating user: {e}")
        db_session.rollback()
        raise e


def create_session(db_session: Session, user_id: str) -> Optional[UserSession]:
    """Create a new session for a user."""
    try:
        session = UserSession(user_id=user_id)
        db_session.add(session)
        db_session.commit()
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        db_session.rollback()
        return None


# Saving to database functions
def store_turn(
    db_session: Session,
    session_id: UUID,
    nlq: str,
    database_used: str,
    sql_query_id: UUID,
) -> Optional[Turn]:
    """
    Stores a new turn for a session.
    """
    try:
        turn = Turn(
            session_id=session_id,
            nlq=nlq,
            database_used=database_used,
            sqid=sql_query_id,
        )
        db_session.add(turn)
        db_session.commit()
        return turn
    except Exception as e:
        logger.error(f"Error storing turn: {e}")
        db_session.rollback()
        return None


def save_user_fav_query(
    db_session: Session, user_id: str, turn_id: int, sql_query_id: UUID
) -> Optional[SavedQuery]:
    """
    Save a query as the user's favorite.
    """
    try:
        saved_query = SavedQuery(user_id=user_id, turn_id=turn_id, sqid=sql_query_id)
        db_session.add(saved_query)
        db_session.commit()
        return saved_query
    except Exception as e:
        logger.error(f"Error saving query: {e}")
        db_session.rollback()
        return None


# Save the generated SQL query by AI agent
def save_query(db_session: Session, sql_query: str) -> Optional[SqlQuery]:
    """
    Save a generated SQL query.
    """
    try:
        query = SqlQuery(sqlquery=sql_query)
        db_session.add(query)
        db_session.commit()
        return query
    except Exception as e:
        logger.error(f"Error saving query: {e}")
        db_session.rollback()
        return None


# check if session exists for that user
def get_session_for_user(
    db_session: Session, user_id: str, session_id: UUID
) -> Optional[UserSession]:
    """
    Check if session id is for the user; if not, return None
    """
    try:
        session = (
            db_session.query(UserSession)
            .filter_by(user_id=user_id, session_id=session_id)
            .first()
        )
        if not session:
            logger.warning(
                f"Session not found for user: {user_id}, session_id: {session_id}"
            )
            return None
        return session
    except Exception as e:
        logger.error(f"Error getting or creating session: {e}")
        db_session.rollback()
        return None


# Get data from database functions


def get_chat_history(
    db_session: Session, session_id: UUID
) -> List[ChatHistoryResponse]:
    """
    Get chat history for a session.
    """
    try:
        turns = (
            db_session.query(Turn)
            .filter_by(session_id=session_id)
            .order_by(desc(Turn.created_at))
            .all()
        )
        chat_history = []
        for turn in turns:
            chat_history.append(
                ChatHistoryResponse(
                    id=turn.turn_id,
                    message=turn.nlq,
                    role=Roles.USER,
                    timestamp=turn.created_at,
                )
            )
            chat_history.append(
                ChatHistoryResponse(
                    id=turn.sql_query.sqid,
                    message=turn.sql_query.sqlquery,
                    role=Roles.BOT,
                    timestamp=turn.sql_query.created_at,
                )
            )
        return chat_history
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        db_session.rollback()
        return []


class UserSessionsResponse(BaseModel):
    session_id: UUID
    nlq: str


# Get the list of session by user and first turn nlq
def get_history_sessions(
    db_session: Session, user_id: str
) -> List[UserSessionsResponse]:
    """
    Get all sessions for a user, along with first NLQ turn for each session.
    """
    try:
        sessions = db_session.query(UserSession).filter_by(user_id=user_id).all()
        sessions_list = []
        if not sessions:
            return sessions_list
        for session in sessions:
            first_turn = (
                db_session.query(Turn)
                .filter_by(session_id=session.session_id)
                .order_by(Turn.created_at)
                .first()
            )
            if first_turn:
                sessions_list.append(
                    UserSessionsResponse(
                        session_id=session.session_id, nlq=f"{first_turn.nlq}"
                    )
                )
            else:
                sessions_list.append(
                    UserSessionsResponse(session_id=session.session_id, nlq="")
                )

        return sessions_list
    except Exception as e:
        logger.error(f"Error getting history sessions: {e}")
        db_session.rollback()
        return []


class SavedQueriesResponse(BaseModel):
    sqid: UUID
    nlq: str
    sqlquery: str


def get_saved_queries(db_session: Session, user_id: str) -> List[SavedQueriesResponse]:
    """
    Get all saved queries for a user.
    """
    try:
        saved_queries = db_session.query(SavedQuery).filter_by(user_id=user_id).all()
        saved_queries_list = []
        if not saved_queries:
            return saved_queries_list
        for saved_query in saved_queries:
            saved_queries_list.append(
                SavedQueriesResponse(
                    sqid=saved_query.sqid,
                    nlq=saved_query.turns.nlq,
                    sqlquery=saved_query.sql_query.sqlquery,
                )
            )
        return saved_queries_list
    except Exception as e:
        logger.error(f"Error getting saved queries: {e}")
        db_session.rollback()
        return []
