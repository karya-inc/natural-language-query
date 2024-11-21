import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models
from models import Base, User, UserSession, Turn, SqlQuery, SavedQuery

# Create engine and session
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def seed_database():
    # Create users
    users = [
        User(user_id=str(uuid.uuid4())),
        User(user_id=str(uuid.uuid4()))
    ]
    session.add_all(users)
    session.commit()

    # Create user sessions
    sessions = [
        UserSession(user_id=users[0].user_id),
        UserSession(user_id=users[1].user_id)
    ]
    session.add_all(sessions)
    session.commit()

    # Create SQL queries
    sql_queries = [
        SqlQuery(sqlquery='SELECT * FROM users'),
        SqlQuery(sqlquery='SELECT COUNT(*) FROM sessions')
    ]
    session.add_all(sql_queries)
    session.commit()

    # Create turns
    turns = [
        Turn(
            session_id=sessions[0].session_id,
            nlq='Show me all users',
            sqid=sql_queries[0].sqid,
            database_used='main_database'
        ),
        Turn(
            session_id=sessions[1].session_id,
            nlq='Count total sessions',
            sqid=sql_queries[1].sqid,
            database_used='analytics_database'
        )
    ]
    session.add_all(turns)
    session.commit()

    # Create saved queries
    saved_queries = [
        SavedQuery(
            turn_id=turns[0].turn_id,
            sqid=turns[0].sqid,
            user_id=users[0].user_id
        ),
        SavedQuery(
            turn_id=turns[1].turn_id,
            sqid=turns[1].sqid,
            user_id=users[1].user_id
        )
    ]
    session.add_all(saved_queries)
    session.commit()

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
    session.close()