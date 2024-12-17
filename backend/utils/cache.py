import json
from typing import Callable, Optional
from db.db_queries import fetch_query_by_value, get_exeuction_log_result, get_recent_execution_for_query
from dependencies.db import get_db_session
from executor.catalog import Catalog
from utils.logger import get_logger
from utils.query_pipeline import QueryExecutionResult, QueryExecutionSuccessResult
from utils.redis import get_redis_key, redis_client, REDIS_TTL

logger = get_logger("[CACHING UTILS]")


def save_result_to_redis(
    execution_result: QueryExecutionSuccessResult,
):
    query = execution_result.execution_log.query
    key = get_redis_key("query_results", str(query.sqid))
    redis_client.set(key, json.dumps(execution_result.to_dict()), ex=REDIS_TTL)


def get_result_from_redis(
    query: str, catalog_name: str
) -> Optional[QueryExecutionSuccessResult]:
    with get_db_session() as db_session:
        query_obj = fetch_query_by_value(db_session, query, catalog_name)

    if not query_obj:
        return None

    try:
        key = get_redis_key("query_results", str(query_obj.sqid))
        cached_result = redis_client.get(key)
        if cached_result:
            return QueryExecutionSuccessResult.from_json(str(cached_result))

    except Exception as e:
        logger.error(f"Error while fetching result from redis: {e}")
        return None


def get_cached_query_result(
    sql_query: str, catalog: Catalog
) -> Optional[QueryExecutionSuccessResult]:

    # Check if the result is cached in redis
    if cached_result := get_result_from_redis(sql_query, catalog.name):
        return cached_result

    # Fetch the most recent query result from the database if not found in redis cache
    with get_db_session() as db_session:
        query = fetch_query_by_value(db_session, sql_query, catalog.name)
        if not query:
            return None

        execution_log = get_recent_execution_for_query(
            db_session, str(query.sqid), catalog.name
        )
        if not execution_log:
            return None

        execution_result_info = get_exeuction_log_result(db_session, execution_log.id)
        if not execution_result_info or not execution_result_info.result:
            return None

    # Cache the result in redis and return
    cached_result = QueryExecutionSuccessResult(
        execution_result_info.result, execution_log
    )
    save_result_to_redis(
        cached_result,
    )
    return cached_result


def get_or_execute_query_result(
    sql_query: str,
    catalog: Catalog,
    execute_query: Callable[[str, bool], QueryExecutionResult],
    is_background: bool = False,
) -> QueryExecutionResult:
    """
    This function will first try to fetch the result from redis or database.
    If not found, it will execute the query and cache the result in redis.
    """

    cached_result = get_cached_query_result(sql_query=sql_query, catalog=catalog)
    if cached_result:
        return cached_result

    # If the result is not found in redis and database, execute the query
    execution_result = execute_query(sql_query, is_background)
    if isinstance(execution_result, QueryExecutionSuccessResult):
        save_result_to_redis(execution_result)

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
        redis_client.set(key, json.dumps(execution_result.__dict__), ex=REDIS_TTL)

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
