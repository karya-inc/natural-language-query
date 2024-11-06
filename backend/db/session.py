from sqlalchemy import create_engine
from db.config import Config
from sqlalchemy.orm import sessionmaker

class Database:
    def __init__(self, config: Config):
        self.engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            **config.SQLALCHEMY_ENGINE_OPTIONS
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
