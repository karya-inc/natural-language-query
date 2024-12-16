from typing import Optional, cast
from fastapi import Request
from sqlalchemy.orm import Session
from db.config import Config
from db.session import Database

config = Config()
db = Database(config)


# Dependency to get database session
def get_db_session():
    return db.get_session()


def get_db_session_from_request(request: Request):
    try:
        session = cast(Optional[Session], request.state.db)
    except Exception:
        session = None

    if not session:
        return db.get_session()
