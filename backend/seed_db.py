# Seed the database with queries and save them
from db.db_queries import create_saved_query, get_or_create_query
from dependencies.db import get_db_session


sample_data = [
    {
        "query": "SELECT worker.id, worker.phone_number FROM worker limit 5",
        "name": "Get 5 workers",
        "description": "Get details of the first 5 workers",
        "database_used": "karya_db",
    },
    {
        "query": "SELECT worker.id, worker.phone_number FROM worker limit 10",
        "name": "Get 10 workers",
        "description": "Get details of the first 10 workers",
        "database_used": "karya_db",
    },
    {
        "query": "SELECT worker.id, worker.phone_number FROM worker limit 15",
        "name": "Get 15 workers",
        "description": "Get details of the first 15 workers",
        "database_used": "karya_db",
    },
    {
        "query": "SELECT worker.id, worker.phone_number FROM worker limit 20",
        "name": "Get 20 workers",
        "description": "Get details of the first 20 workers",
        "database_used": "karya_db",
    },
    {
        "query": "SELECT * FROM worker",
        "name": "Get all the details of all the workers",
        "database_used": "karya_db",
    },
]

for data in sample_data:
    db_session = get_db_session()
    query = get_or_create_query(db_session, data["query"], "1", data["database_used"])
    create_saved_query(
        db_session=db_session,
        name=data["name"],
        description=data["description"] if "description" in data else None,
        sqid=query.sqid,
        user_id="1",
        turn_id=None,
        saved_by="1",
    )

    db_session.commit()
