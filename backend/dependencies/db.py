from db.config import Config
from db.session import Database

config = Config()
db = Database(config)


# Dependency to get database session
def get_db_session():
    with db.get_session() as session:
        return session
