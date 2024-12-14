from typing import cast
from executor.catalog import Catalog
from queues.tasks import ExecuteQueryOp, execute_query_op


def invoke_execute_query_op(execution_log_id: int, catalog: Catalog):
    task = cast(ExecuteQueryOp, execute_query_op)
    return task.apply_async(
        kwargs={"execution_log_id": execution_log_id, "catalog_json": catalog.__dict__},
        serialize="pickle",
    )
