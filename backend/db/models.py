from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableList


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for SQLAlchemy models"""

    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[str]: ARRAY(String),
    }


class User(Base):
    """User model representing user information"""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    # Relationships
    saved_queries: Mapped[List["SavedQuery"]] = relationship(
        "SavedQuery", back_populates="user", default_factory=list
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        back_populates="user", init=False
    )


class UserSession(Base):
    """Session model representing user sessions"""

    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))

    # Fields with Default values
    session_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default_factory=uuid.uuid4
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

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.session_id"))
    nlq: Mapped[str] = mapped_column(Text)
    sqid: Mapped[uuid.UUID] = mapped_column(ForeignKey("sql_queries.sqid"))
    database_used: Mapped[str] = mapped_column(Text)

    # Fields with Default values
    turn_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    session: Mapped["UserSession"] = relationship(back_populates="turns", init=False)
    sql_query: Mapped["SqlQuery"] = relationship(back_populates="turns", init=False)


class SqlQuery(Base):
    """SQL Query model for storing generated SQL queries"""

    __tablename__ = "sql_queries"

    sqlquery: Mapped[str] = mapped_column(Text)

    # Fields with Default values
    sqid: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default_factory=uuid.uuid4
    )

    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), default=None
    )

    # Relationships
    turns: Mapped[List["Turn"]] = relationship(
        "Turn", back_populates="sql_query", default_factory=list
    )


class SavedQuery(Base):
    """Saved Queries model for users to store queries"""

    __tablename__ = "saved_queries"

    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()

    turn_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("turns.turn_id"), nullable=True
    )
    sqid: Mapped[uuid.UUID] = mapped_column(ForeignKey("sql_queries.sqid"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))

    # Fields with Default values
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    # Relationships
    turn: Mapped["Turn"] = relationship(init=False)
    user: Mapped["User"] = relationship(back_populates="saved_queries", init=False)
    sql_query: Mapped["SqlQuery"] = relationship(init=False)


ExecutionStatus = Literal["SUCCESS", "FAILED", "PENDING", "RUNNING"]


class ExecutionLog(Base):
    """
    Logs the status of the query execution
    """

    __tablename__ = "execution_logs"

    status: Mapped[ExecutionStatus] = mapped_column()
    query_id: Mapped[str] = mapped_column(ForeignKey("sql_queries.sqid"))
    executed_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"))

    # Fields with Default values
    notify_to: Mapped[list[str]] = mapped_column(default_factory=list)
    logs: Mapped[Optional[dict[str, Any]]] = mapped_column(default=None, init=False)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(init=False)

    # Relationships
    query: Mapped["SqlQuery"] = relationship(init=False)
    user: Mapped["User"] = relationship(init=False)

class ExecutionResult(Base):
    """
    Execution Result model for storing the result of the query execution
    """

    __tablename__ = "execution_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)

    execution_id: Mapped[int] = mapped_column(ForeignKey("execution_logs.id"))
    result: Mapped[dict[str, Any]] = mapped_column(default=None, init=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)

    # Relationships
    execution_log: Mapped["ExecutionLog"] = relationship(init=False)
