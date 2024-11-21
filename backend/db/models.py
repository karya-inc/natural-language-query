import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for SQLAlchemy models"""

    pass


class User(Base):
    """User model representing user information"""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(primary_key=True)
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
    user: Mapped["User"] = relationship(back_populates="sessions", default=None)
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

    # Relationships
    saved_queries: Mapped[List["SavedQuery"]] = relationship(
        back_populates="turns", default_factory=list
    )
    session: Mapped["UserSession"] = relationship(back_populates="turns", default=None)
    sql_query: Mapped["SqlQuery"] = relationship(back_populates="turns", default=None)


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

    # Relationships
    turns: Mapped[List["Turn"]] = relationship(
        "Turn", back_populates="sql_query", default_factory=list
    )


class SavedQuery(Base):
    """Saved Queries model for users to store queries"""

    __tablename__ = "saved_queries"

    turn_id: Mapped[int] = mapped_column(ForeignKey("turns.turn_id"))
    sqid: Mapped[uuid.UUID] = mapped_column(ForeignKey("sql_queries.sqid"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))

    # Fields with Default values
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None
    )

    # Relationships
    turns: Mapped["Turn"] = relationship(
        "Turn", back_populates="saved_queries", default=None
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="saved_queries", default=None
    )
    sql_query: Mapped["SqlQuery"] = relationship("SqlQuery", default=None)
