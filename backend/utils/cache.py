import json
from typing import Callable, Optional
from db.db_queries import fetch_query_by_value, get_exeuction_result, get_recent_execution_for_query
from dependencies.db import get_db_session
from executor.catalog import Catalog
from executor.state import QueryResults
from utils.logger import get_logger
from utils.query_pipeline import QueryExecutionResult, QueryExecutionSuccessResult
from utils.redis import get_redis_key, redis_client, REDIS_TTL

logger = get_logger("[CACHING UTILS]")


def get_cached_query_result(sql_query: str, catalog: Catalog) -> Optional[QueryResults]:
    key = get_redis_key("query_results", catalog.name, sql_query.strip())
    cached_result = redis_client.get(key)

    if cached_result:
        return QueryResults(json.loads(str(cached_result)))

    db_session = get_db_session()
    query = fetch_query_by_value(db_session, sql_query)

    if not query:
        return None

    execution = get_recent_execution_for_query(
        db_session, str(query.sqid), catalog.name
    )

    if not execution or execution.status != "SUCCESS":
        return None

    try:
        execution_result = get_exeuction_result(db_session, execution.id)
        return QueryResults(execution_result.result)
    except Exception as e:
        logger.error(
            f"Execution with id {execution.id} was SUCCESS but failed to fetch result: {e}"
        )
        return None


def get_or_execute_query_result(
    query: str,
    catalog: Catalog,
    execute_query: Callable[[str, bool], QueryExecutionResult],
    is_background: bool = False,
) -> QueryExecutionResult:

    cached_result = get_cached_query_result(query, catalog)
    if cached_result:
        return QueryExecutionSuccessResult(cached_result)

    execution_result = execute_query(query, is_background)

    if isinstance(execution_result, QueryExecutionSuccessResult):
        # Cache the result for 30 minutes
        key = get_redis_key("query_results", catalog.name, query.strip())
        redis_client.set(key, json.dumps(execution_result.result), ex=REDIS_TTL)

    return execution_result


def execute_and_cache_query_result(
    query: str,
    catalog: Catalog,
    execute_query: Callable[[str, bool], QueryExecutionResult],
    is_background: bool = False,
) -> QueryExecutionResult:
    execution_result = execute_query(query, is_background)

    if isinstance(execution_result, QueryExecutionSuccessResult):
        # Cache the result for 30 minutes
        key = get_redis_key("query_results", catalog.name, query.strip())
        redis_client.set(key, json.dumps(execution_result.result), ex=REDIS_TTL)

    return execution_result


def get_cached_categorical_values(catalog: Catalog, table: str) -> Optional[set]:
    key = get_redis_key("categorical", catalog.name, table)
    cached_result = redis_client.get(key)

    if cached_result:
        return json.loads(str(cached_result))

    return None


def get_cached_sample_rows(catalog: Catalog, table: str) -> Optional[set]:
    key = get_redis_key("samples", catalog.name, table)
    cached_result = str(redis_client.get(key))

    if cached_result:
        return json.loads(cached_result)

    return None
