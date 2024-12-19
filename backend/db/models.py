import uuid
from datetime import datetime
from typing import Any, List, Literal, Optional
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from executor.models import QueryResults


def get_uuid_str():
    return str(uuid.uuid4())


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for SQLAlchemy models"""

    type_annotation_map = {
        dict[str, Any]: JSONB,
        QueryResults: JSONB,
        list[str]: ARRAY(String),
    }


class User(Base):
    """User model representing user information"""

    __tablename__ = "users"
    name: Mapped[Optional[str]] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    # Relationships
    saved_queries: Mapped[List["SavedQuery"]] = relationship(
        "SavedQuery",
        back_populates="user",
        default_factory=list,
        foreign_keys="[SavedQuery.user_id]",
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        back_populates="user", init=False
    )

    # Fields with Default values
    user_id: Mapped[str] = mapped_column(primary_key=True, default_factory=get_uuid_str)


class UserSession(Base):
    """Session model representing user sessions"""

    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), index=True)

    # Fields with Default values
    session_id: Mapped[str] = mapped_column(
        primary_key=True, default_factory=get_uuid_str
    )
    started_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=None, onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions", init=False)
    turns: Mapped[List["Turn"]] = relationship(
        back_populates="session", default_factory=list
    )


class Turn(Base):
    """Turn model representing individual turns in a session"""

    __tablename__ = "turns"

    nlq: Mapped[str] = mapped_column()
    execution_log_id: Mapped[int] = mapped_column(
        ForeignKey("execution_logs.id"), index=True
    )
    database_used: Mapped[str] = mapped_column(Text)

    # Fields with Default values
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.session_id"), default_factory=get_uuid_str, index=True
    )
    turn_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    session: Mapped["UserSession"] = relationship(back_populates="turns", init=False)
    execution_log: Mapped["ExecutionLog"] = relationship(init=False)


class SqlQuery(Base):
    """SQL Query model for storing generated SQL queries"""

    __tablename__ = "sql_queries"
    sqlquery: Mapped[str] = mapped_column()
    database_used: Mapped[Optional[str]] = mapped_column()

    # Fields with Default values
    sqid: Mapped[str] = mapped_column(primary_key=True, default_factory=get_uuid_str)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), default=None
    )


class SavedQuery(Base):
    """Saved Queries model for users to store queries"""

    __tablename__ = "saved_queries"
    # Fields without defaults
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column()
    sqid: Mapped[str] = mapped_column(ForeignKey("sql_queries.sqid"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), index=True)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="saved_queries", foreign_keys="[SavedQuery.user_id]", init=False
    )

    # Fields with defaults
    description: Mapped[Optional[str]] = mapped_column(default=None)
    turn_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("turns.turn_id"), nullable=True, default=None, index=True
    )
    saved_by: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), default=None, index=True
    )
    sql_query: Mapped["SqlQuery"] = relationship(init=False)
    turn: Mapped["Turn"] = relationship(init=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sqid": self.sqid,
            "user_id": self.user_id,
            "created_at": str(self.created_at),
            "description": self.description,
            "turn_id": self.turn_id,
            "saved_by": self.saved_by,
        }


ExecutionStatus = Literal["SUCCESS", "FAILED", "PENDING", "RUNNING"]


class ExecutionLog(Base):
    """
    Logs the status of the query execution
    """

    __tablename__ = "execution_logs"

    status: Mapped[ExecutionStatus] = mapped_column()
    query_id: Mapped[str] = mapped_column(ForeignKey("sql_queries.sqid"), index=True)
    executed_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"), index=True)

    # Fields with Default values
    notify_to: Mapped[list[str]] = mapped_column(default_factory=list)
    logs: Mapped[Optional[dict[str, Any]]] = mapped_column(default=None, init=False)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(init=False)

    # Relationships
    query: Mapped["SqlQuery"] = relationship(init=False)
    user: Mapped["User"] = relationship(init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "query_id": self.query_id,
            "executed_by": self.executed_by,
            "notify_to": self.notify_to,
            "logs": self.logs,
            "id": self.id,
            "created_at": str(self.created_at),
            "completed_at": str(self.completed_at),
        }

    @staticmethod
    def from_dict(data: dict):
        log = ExecutionLog(
            status=data["status"],
            query_id=data["query_id"],
            executed_by=data["executed_by"],
            notify_to=data["notify_to"],
        )

        # Force init remaining fields
        log.logs = data["logs"]
        log.id = data["id"]
        log.created_at = datetime.fromisoformat(data["created_at"])
        log.completed_at = datetime.fromisoformat(data["completed_at"])
        return log


class ExecutionResult(Base):
    """
    Execution Result model for storing the result of the query execution
    """

    __tablename__ = "execution_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)

    execution_id: Mapped[int] = mapped_column(
        ForeignKey("execution_logs.id"), index=True
    )
    result: Mapped[QueryResults] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)

    # Relationships
    execution_log: Mapped["ExecutionLog"] = relationship(init=False)
