import uuid
from typing import List
from datetime import datetime
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, TIMESTAMP, func, UUID

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        back_populates='user',
        cascade="all, delete-orphan"
    )

class UserSession(Base):
    __tablename__ = 'sessions'

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.user_id', ondelete='CASCADE')
    )
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    user: Mapped["User"] = relationship(back_populates='sessions')
    queries: Mapped[List["UserQuery"]] = relationship(back_populates='session')

class UserQuery(Base):
    __tablename__ = 'queries'

    query_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('sessions.session_id', ondelete='CASCADE')
    )
    user_query: Mapped[str] = mapped_column(nullable=False)
    ai_response: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    session: Mapped["UserSession"] = relationship(back_populates='queries')