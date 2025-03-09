from typing import Optional
import celery
from sqlalchemy.orm import Session

from db.catalog_utils import get_engine
from executor.models import QueryResults
from utils.logger import get_logger
from utils.notify_user import notify_user_on_failure, notify_user_on_success
from .celery import app
from sqlalchemy import text

from db.db_queries import get_execution_log, save_execution_result, set_execution_status
from dependencies.db import get_db_session
from executor.catalog import Catalog
from utils.rows_to_json import convert_rows_to_serializable

logger = get_logger("[DB-Queue]")


class ExecuteQueryOp(celery.Task):
    _db_session: Optional[Session] = None

    @property
    def db_session(self):
        if self._db_session is None:
            with get_db_session() as db_session:
                self._db_session = db_session
        return self._db_session

    def before_start(self, task_id, args, kwargs):
        if "execution_log_id" not in kwargs:
            return

        execution_log_id = kwargs["execution_log_id"]
        set_execution_status(self.db_session, execution_log_id, "RUNNING")

        logger.info(f"Execution with id '{execution_log_id}' STARTED")

    def on_success(self, retval: QueryResults, task_id, args, kwargs):
        if "execution_log_id" not in kwargs:
            return

        execution_log_id = kwargs["execution_log_id"]
        save_execution_result(self.db_session, execution_log_id, retval)
        set_execution_status(self.db_session, execution_log_id, "SUCCESS")

        logger.info(f"Execution with id '{execution_log_id}' SUCCEEDED")

        # Notify user on success
        execution_log = get_execution_log(self.db_session, execution_log_id)
        assert (
            execution_log is not None
        ), f"Expected execution log to be present for {execution_log_id}"
        notify_user_on_success(
            execution_log_id,
            retval,
            execution_log.notify_to,
        )

        if self._db_session is not None:
            self._db_session.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):

        if "execution_log_id" not in kwargs:
            logger.error(f"Task failed: {exc}")
            return

        execution_log_id = kwargs["execution_log_id"]

        logger.error(f"Execution with id '{execution_log_id}' FAILED: {exc}")
        set_execution_status(self.db_session, execution_log_id, "FAILED")

        # Notify user on failure
        execution_log = get_execution_log(self.db_session, execution_log_id)

        assert (
            execution_log is not None
        ), f"Expected execution log to be present for id {execution_log_id}"

        notify_user_on_failure(
            execution_log_id,
            execution_log.notify_to,
        )

        if self._db_session is not None:
            self._db_session.close()
            self._db_session = None


@app.task(base=ExecuteQueryOp, bind=True)
def execute_query_op(
    self: ExecuteQueryOp, execution_log_id: int, catalog_json: dict
) -> QueryResults:
    catalog = Catalog(**catalog_json)
    engine = get_engine(catalog)
    celery.Task.request

    execution_log = get_execution_log(self.db_session, execution_log_id)
    assert (
        execution_log is not None
    ), f"Expected execution log to be present for {execution_log_id}"
    self.db_session.commit()

    with engine.connect() as connection:
        stmt = text(execution_log.query.sqlquery)
        params = execution_log.query_params
        result = connection.execute(stmt, params).fetchall()
        serialized_result = convert_rows_to_serializable(result)
        return serialized_result
