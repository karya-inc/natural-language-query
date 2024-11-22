from db.config import Config
from db.session import Database

config = Config()
db = Database(config)


# Dependency to get database session
def get_db():
    return next(db.get_session())
