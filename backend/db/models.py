import uuid
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func, UUID

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Text, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    sessions = relationship('Session', back_populates='user')


class UserSession(Base):
    __tablename__ = 'sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    started_at = Column(TIMESTAMP, server_default=func.now())
    ended_at = Column(TIMESTAMP, nullable=True)

    user = relationship('User', back_populates='sessions')
    queries = relationship('Query', back_populates='session')


class UserQuery(Base):
    __tablename__ = 'queries'

    query_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'))
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    session = relationship('Session', back_populates='queries')
