from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import ExecutionLog, ExecutionResult, ExecutionStatus, User, UserSession, Turn, SqlQuery, SavedQuery
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Any, List, Optional
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


def get_or_create_user(
    db_session: Session,
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> User:
    """Check if a user exists; if not, create a new user."""
    try:
        user = db_session.query(User).filter_by(user_id=user_id).first()
        logger.info(f"User: {user}")
        if not user:
            logger.warning(f"User not found, creating a new user with ID: {user_id}")
            user = User(user_id=user_id, name=name, email=email)
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
) -> Turn:
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
        raise e


def save_user_fav_query(
    db_session: Session,
    user_id: str,
    turn_id: int,
    sql_query_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[SavedQuery]:
    """
    Save a query as the user's favorite.
    """
    try:
        turn = db_session.query(Turn).filter_by(turn_id=turn_id).first()
        if not name and turn:
            name = turn.nlq
        else:
            name = "Unnamed Query"

        saved_query = SavedQuery(
            user_id=user_id,
            turn_id=turn_id,
            sqid=sql_query_id,
            name=name,
            description=description,
        )
        db_session.add(saved_query)
        db_session.commit()
        return saved_query
    except Exception as e:
        logger.error(f"Error saving query: {e}")
        db_session.rollback()
        return None


# Save the generated SQL query by AI agent
def create_query(
    db_session: Session, sql_query: str, user_id: Optional[str] = None
) -> SqlQuery:
    """
    Save a generated SQL query.
    """
    try:
        query = SqlQuery(sqlquery=sql_query, user_id=user_id)
        db_session.add(query)
        db_session.commit()
        return query
    except Exception as e:
        logger.error(f"Error saving query: {e}")
        db_session.rollback()
        raise e


def fetch_query_by_id(db_session: Session, query_id: str) -> SqlQuery:
    try:
        query = db_session.query(SqlQuery).filter_by(sqid=query_id).first()

        if not query:
            raise Exception(f"Query not found for id: {query_id}")

        return query
    except Exception as e:
        logger.error(f"Error fetching query: {e}")
        db_session.rollback()
        raise e


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
                    nlq=saved_query.turn.nlq,
                    sqlquery=saved_query.sql_query.sqlquery,
                )
            )
        return saved_queries_list
    except Exception as e:
        logger.error(f"Error getting saved queries: {e}")
        db_session.rollback()
        return []


def create_execution_entry(
    db_session: Session, user_id: str, query_id: str
) -> ExecutionLog:
    """
    Save the execution log for a query.
    """
    try:
        execution_log = ExecutionLog("RUNNING", query_id, user_id)
        db_session.add(execution_log)
        db_session.commit()
        return execution_log

    except Exception as e:
        logger.error(f"Error saving execution log: {e}")
        db_session.rollback()
        raise e


def set_execution_status(
    db_session: Session, execution_id: int, status: ExecutionStatus
) -> ExecutionLog:
    """
    Set the execution status for a query.
    """
    try:
        execution_log = (
            db_session.query(ExecutionLog).filter_by(id=execution_id).first()
        )
        if not execution_log:
            raise Exception("Execution log not found for {query_id}")

        execution_log.status = status
        db_session.commit()
        return execution_log
    except Exception as e:
        logger.error(f"Error setting execution status: {e}")
        db_session.rollback()
        raise e


def get_execution_log(db_session: Session, execution_id: int) -> ExecutionLog:
    """
    Get the execution log for a query.
    """
    try:
        execution_log = (
            db_session.query(ExecutionLog).filter_by(id=execution_id).first()
        )
        if not execution_log:
            raise Exception("Execution log not found for {query_id}")

        return execution_log
    except Exception as e:
        logger.error(f"Error getting execution log: {e}")
        db_session.rollback()
        raise e


def get_exeuction_result(db_session: Session, execution_id: int) -> dict[str, Any]:
    """
    Get the execution result for a query.
    """
    try:
        execution_result = (
            db_session.query(ExecutionResult)
            .filter_by(exeuction_id=execution_id)
            .first()
        )

        if not execution_result:
            raise Exception("Execution log not found for {query_id}")

        return execution_result.result
    except Exception as e:
        logger.error(f"Error getting execution result: {e}")
        db_session.rollback()
        raise e


def save_execution_result(
    db_session: Session, execution_id: int, result: dict[str, Any]
) -> ExecutionResult:
    """
    Save the execution result for a query.
    """
    try:
        execution_result = ExecutionResult(execution_id=execution_id, result=result)
        db_session.add(execution_result)
        db_session.commit()
        return execution_result
    except Exception as e:
        logger.error(f"Error saving execution result: {e}")
        db_session.rollback()
        raise e
