from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from db.models import (
    ExecutionLog,
    ExecutionResult,
    ExecutionStatus,
    User,
    UserSession,
    Turn,
    SqlQuery,
    SavedQuery,
    get_uuid_str,
)
from datetime import datetime
from pydantic import BaseModel
from executor.models import QueryResults, ColumnOrder, SqlQueryParams
from typing import Any, List, Literal, Optional, cast
from utils.logger import get_logger
import enum

from utils.rows_to_json import convert_rows_to_serializable

logger = get_logger("[DATABASE_QUERIES]")


# Enums
class Roles(enum.Enum):
    USER = "user"
    BOT = "bot"


# Pydantic Models
class ChatHistoryResponse(BaseModel):
    id: int | str
    turn_id: int
    role: Roles
    timestamp: datetime
    type: Optional[Literal["text", "table", "error", "execution"]]
    session_id: str
    query: Optional[str]
    sql_query_id: Optional[str] = None
    message: Optional[str] = None
    execution_id: Optional[int] = None


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
    session_id: str,
    nlq: str,
    database_used: str,
    execution_log_id: int,
) -> Turn:
    """
    Stores a new turn for a session.
    """
    try:
        turn = Turn(
            session_id=session_id,
            nlq=nlq,
            database_used=database_used,
            execution_log_id=execution_log_id,
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
    sql_query_id: str,
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
def get_or_create_query(
    db_session: Session,
    sql_query: str,
    user_id: Optional[str],
    catalog_name: str,
) -> SqlQuery:
    """
    Save a generated SQL query.
    """
    try:
        # Search for the query in the database
        query = fetch_query_by_value(db_session, sql_query, catalog_name)
        if query:
            return query

        # If the query is not found, create a new query
        query = SqlQuery(
            sqlquery=sql_query.strip(), user_id=user_id, database_used=catalog_name
        )
        db_session.add(query)
        db_session.commit()
        return query
    except Exception as e:
        logger.error(f"Error saving query: {e}")
        db_session.rollback()
        raise e


def get_query_by_id(db_session: Session, sqid: str) -> Optional[SqlQuery]:
    """
    Get a query by its ID.
    """
    try:
        query = db_session.query(SqlQuery).filter_by(sqid=sqid).first()
        return query
    except Exception as e:
        logger.error(f"Error getting query by ID: {e}")
        db_session.rollback()
        return None


def fetch_query_by_value(
    db_session: Session, sql_query: str, catalog_name: str
) -> Optional[SqlQuery]:
    try:
        query = (
            db_session.query(SqlQuery)
            .filter_by(sqlquery=sql_query.strip(), database_used=catalog_name)
            .first()
        )
        return query

    except Exception as e:
        logger.error(f"Error fetching query: {e}")
        db_session.rollback()
        raise e


# check if session exists for that user
def get_session_for_user(
    db_session: Session, user_id: str, session_id: str
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


def get_chat_history(db_session: Session, session_id: str) -> List[ChatHistoryResponse]:
    """
    Get chat history for a session.
    """
    try:
        turns = (
            db_session.query(Turn)
            .filter_by(session_id=session_id)
            .order_by(asc(Turn.created_at))
            .all()
        )

        chat_history = []
        for turn in turns:
            if turn.execution_log:
                execution_id = turn.execution_log.id
                query = turn.execution_log.query.sqlquery
            else:
                execution_id = None
                query = None

            # User Turn Message
            chat_history.append(
                ChatHistoryResponse(
                    id=get_uuid_str(),
                    turn_id=turn.turn_id,
                    message=turn.nlq,
                    role=Roles.USER,
                    timestamp=turn.created_at,
                    type="text",
                    session_id=str(session_id),
                    query=None,
                    execution_id=None,
                )
            )

            # Bot Turn Message
            chat_history.append(
                ChatHistoryResponse(
                    id=get_uuid_str(),
                    turn_id=turn.turn_id,
                    role=Roles.BOT,
                    timestamp=turn.created_at,
                    execution_id=execution_id,
                    query=query,
                    type="execution",
                    session_id=str(session_id),
                    sql_query_id=(
                        turn.execution_log.query.sqid if turn.execution_log else None
                    ),
                )
            )
        return chat_history
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        db_session.rollback()
        return []


class UserSessionsResponse(BaseModel):
    session_id: str
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
        return sessions_list
    except Exception as e:
        logger.error(f"Error getting history sessions: {e}")
        db_session.rollback()
        return []


class SavedQueriesResponse(BaseModel):
    id: int
    sql_query_id: str
    name: str
    description: Optional[str]
    saved_for: str
    saved_by: Optional[str]


def get_saved_queries(
    db_session: Session, user_id: str, filter_type: Optional[str] = "saved"
) -> List[SavedQueriesResponse]:
    """
    Get all saved queries for a user.
    """
    try:
        if filter_type != "all":
            saved_queries = (
                db_session.query(SavedQuery).filter_by(user_id=user_id).all()
            )
        else:
            saved_queries = (
                db_session.query(SavedQuery).filter(SavedQuery.user_id != user_id).all()
            )
        saved_queries_list = []
        if not saved_queries:
            return saved_queries_list

        for saved_query in saved_queries:
            saved_queries_list.append(
                SavedQueriesResponse(
                    id=saved_query.id,
                    sql_query_id=saved_query.sqid,
                    name=saved_query.name,
                    description=saved_query.description,
                    saved_for=saved_query.user_id,
                    saved_by=saved_query.saved_by,
                )
            )
        return saved_queries_list
    except Exception as e:
        logger.error(f"Error getting saved queries: {e}")
        db_session.rollback()
        return []


def get_saved_query_by_id(
    db_session: Session, sqid: str, user_id: str
) -> Optional[SavedQuery]:
    """
    Get a saved query by its ID.
    """
    try:
        saved_query = (
            db_session.query(SavedQuery).filter_by(sqid=sqid, user_id=user_id).first()
        )
        return saved_query
    except Exception as e:
        logger.error(f"Error getting saved query by ID: {e}")
        db_session.rollback()
        return None


def create_execution_entry(
    db_session: Session,
    user_id: str,
    query_id: str,
    query_params: SqlQueryParams = {},
    status: ExecutionStatus = "PENDING",
) -> ExecutionLog:
    """
    Save the execution log for a query.
    """
    try:
        execution_log = ExecutionLog(status, query_id, user_id, query_params)
        db_session.add(execution_log)
        db_session.commit()
        return execution_log

    except Exception as e:
        logger.error(f"Error saving execution log: {e}")
        db_session.rollback()
        raise e


def set_execution_status(
    db_session: Session, execution_id: int, status: ExecutionStatus
) -> Optional[ExecutionLog]:
    """
    Set the execution status for a query.
    """
    try:
        execution_log = (
            db_session.query(ExecutionLog).filter_by(id=execution_id).first()
        )
        if not execution_log:
            return None

        execution_log.status = status
        if status == "SUCCESS":
            execution_log.completed_at = datetime.now()

        db_session.commit()
        return execution_log
    except Exception as e:
        logger.error(f"Error setting execution status: {e}")
        db_session.rollback()
        raise e


def get_execution_log(db_session: Session, execution_id: int) -> Optional[ExecutionLog]:
    """
    Get the execution log for a query.
    """
    try:
        execution_log = (
            db_session.query(ExecutionLog).filter_by(id=execution_id).first()
        )
        if not execution_log:
            return None

        return execution_log
    except Exception as e:
        logger.error(f"Error getting execution log: {e}")
        db_session.rollback()
        raise e


def get_recent_execution_for_query_id(
    db_session: Session, sqid: str, status: ExecutionStatus = "SUCCESS"
) -> ExecutionLog | None:
    """
    Get the most recent execution log for a query.
    """
    query_obj = get_query_by_id(db_session, sqid)
    if not query_obj:
        return None

    execution_log = (
        db_session.query(ExecutionLog)
        .filter_by(query_id=query_obj.sqid, status=status)
        .order_by(desc(ExecutionLog.created_at))
        .first()
    )

    return execution_log


def get_recent_execution_for_query(
    db_session: Session, sql_query: str, catalog_name: str
) -> ExecutionLog | None:
    """
    Get the most recent execution log for a query.
    """
    query_obj = fetch_query_by_value(db_session, sql_query, catalog_name)
    if not query_obj:
        return None

    return get_recent_execution_for_query_id(db_session, query_obj.sqid)


class ExecutionLogResult(BaseModel):
    execution_log: dict[str, Any]
    result: Optional[QueryResults]
    column_order: Optional[ColumnOrder]


def get_exeuction_log_result(
    db_session: Session, execution_log_id: int
) -> Optional[ExecutionLogResult]:
    """
    Get the execution result for a query.

    Args:
        db_session (Session): SQLAlchemy Session
        execution_log_id (int): Execution Log ID
    """
    try:
        execution_result_with_log = (
            db_session.query(ExecutionLog, ExecutionResult)
            .options(
                joinedload(ExecutionLog.query),
                joinedload(ExecutionLog.user),
                joinedload(ExecutionResult.execution_log),
            )
            .outerjoin(
                ExecutionResult,
                ExecutionLog.id == ExecutionResult.execution_id,
            )
            .filter(ExecutionLog.id == execution_log_id)
            .first()
        )

        if not execution_result_with_log:
            return None

        # Unpack the tuple
        execution_log, execution_result = execution_result_with_log

        return ExecutionLogResult(
            execution_log=execution_log.to_dict(),
            result=execution_result.result if execution_result else None,
            column_order=execution_result.column_order if execution_result else None,
        )

    except Exception as e:
        logger.error(f"Error getting execution result: {e}")
        db_session.rollback()
        raise e


def save_execution_result(
    db_session: Session, execution_id: int, result: QueryResults
) -> ExecutionResult:
    """
    Save the execution result for a query.
    """
    try:
        result = convert_rows_to_serializable(result)
        column_order = cast(ColumnOrder, list(result[0].keys()) if result else [])
        execution_result = ExecutionResult(execution_id=execution_id,
                                           result=result, column_order=column_order)
        db_session.add(execution_result)
        db_session.commit()
        return execution_result
    except Exception as e:
        logger.error(f"Error saving execution result: {e}")
        db_session.rollback()
        raise e


def check_if_sql_query_exist(db_session: Session, sqid: str) -> Optional[SqlQuery]:
    """
    Check if sql query exists in the database
    """
    try:
        sql_query = db_session.query(SqlQuery).filter_by(sqid=sqid).first()
        return sql_query
    except Exception as e:
        logger.error(f"Error checking if SQL query exists: {e}")
        db_session.rollback()
        return None


def check_if_query_against_user_exist(
    db_session: Session, sqid: str, user_id: str
) -> Optional[SavedQuery]:
    """
    Check if the query against the user exists
    """
    try:
        saved_query = (
            db_session.query(SavedQuery).filter_by(sqid=sqid, user_id=user_id).first()
        )
        return saved_query
    except Exception as e:
        logger.error(f"Error checking if query against user exists: {e}")
        db_session.rollback()
        return None


def create_saved_query(
    db_session: Session,
    name: str,
    user_id: str,
    sqid: str,
    turn_id: Optional[int],
    saved_by: Optional[str],
    description: Optional[str],
) -> Optional[SavedQuery]:
    """
    Save the query against the user id
    """
    try:
        saved_query = SavedQuery(
            name=name,
            user_id=user_id,
            sqid=sqid,
            turn_id=turn_id,
            saved_by=saved_by,
            description=description,
        )
        db_session.add(saved_query)
        db_session.commit()
        return saved_query
    except Exception as e:
        logger.error(f"Error storing query: {e}")
        db_session.rollback()
        return None


def get_type_of_query(
    db_session: Session, query_id: str,
):
    try:
        result = (
            db_session.query(SqlQuery.query_type)
            .filter(SqlQuery.sqid == query_id)
            .scalar()
        )
        return result
    except Exception as e:
        logger.error(f"Error getting query type: {e} ")
        return None

def get_dynamic_query_params(
    db_session: Session, query_id: str,
) -> SqlQueryParams:
    try:
        result = (
            db_session.query(SqlQuery.query_params)
            .filter(SqlQuery.sqid == query_id)
            .first()
        )
        if result is not None:
            params = result[0]
            return params if params is not None else {}
        return {}
    except Exception as e:
        logger.error(f"Error getting query params: {e}")
        return {}

def get_all_user_info(db_session: Session) -> List[User]:
    """
    Get all user information
    """
    try:
        users = db_session.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Error getting all user info: {e}")
        db_session.rollback()
        return []
