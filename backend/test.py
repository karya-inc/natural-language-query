from typing import cast
from db.db_queries import create_execution_entry, get_or_create_query
from dependencies.db import get_db_session
from executor.state import QueryResults
from queues.typed_tasks import invoke_execute_query_op
from utils.parse_catalog import parsed_catalogs


print("Starting test")
db_session = get_db_session()
query = get_or_create_query(
    db_session, "SELECT worker.id, worker.phone_number FROM worker limit 5", "1"
)
execution_entry = create_execution_entry(db_session, "1", str(query.sqid))
curr_catalog = parsed_catalogs.catalogs[0]

result = invoke_execute_query_op(execution_entry.id, curr_catalog)
result_value =cast(QueryResults, result.get())
print("Result: ", result_value)
