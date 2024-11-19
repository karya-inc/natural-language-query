import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

class User(Base):
    """User model representing user information"""
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    sessions: Mapped[List['Session']] = relationship('Session', back_populates='user')
    saved_queries: Mapped[List['SavedQuery']] = relationship('SavedQuery', back_populates='user')

class Session(Base):
    """Session model representing user sessions"""
    __tablename__ = 'sessions'

    session_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now()
    )

    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='sessions')
    turns: Mapped[List['Turn']] = relationship('Turn', back_populates='session')

class Turn(Base):
    """Turn model representing individual turns in a session"""
    __tablename__ = 'turns'

    turn_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('sessions.session_id'))
    nlq: Mapped[str] = mapped_column(Text)
    sqid: Mapped[uuid.UUID] = mapped_column(ForeignKey('sql_queries.sqid'))
    database_used: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    session: Mapped['Session'] = relationship('Session', back_populates='turns')
    sql_query: Mapped['SqlQuery'] = relationship('SqlQuery')

class SqlQuery(Base):
    """SQL Query model for storing generated SQL queries"""
    __tablename__ = 'sql_queries'

    sqid: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sqlquery: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    turns: Mapped[List['Turn']] = relationship('Turn', back_populates='sql_query')

class SavedQuery(Base):
    """Saved Queries model for users to store queries"""
    __tablename__ = 'saved_queries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    sqid: Mapped[uuid.UUID] = mapped_column(ForeignKey('sql_queries.sqid'))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='saved_queries')
    sql_query: Mapped['SqlQuery'] = relationship('SqlQuery')