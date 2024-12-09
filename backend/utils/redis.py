import json
from typing import Callable, Literal, Optional
from redis import Redis
from os import environ
from executor.catalog import Catalog
from executor.state import QueryResults
from utils.query_pipeline import QueryExecutionResult, QueryExecutionSuccessResult

REDIS_HOSTNAME = environ.get("REDIS_HOSTNAME", "localhost")
REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = environ.get("REDIS_PASSWORD", None)
REDIS_TTL = int(environ.get("REDIS_TTL", 30 * 60))


redis_client = Redis(
    host=REDIS_HOSTNAME, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
)


def get_redis_key(
    kind: Optional[Literal["samples", "categorical", "query_results"]] = None,
    *argv: str,
) -> str:
    """
    Get the key for a given path in redis
    """

    key = ":".join(argv)
    if kind:
        key = f"{kind}:{key}"

    return key


def get_cached_query_result(query: str, catalog: Catalog) -> Optional[QueryResults]:
    key = get_redis_key("query_results", catalog.name, query.strip())
    cached_result = redis_client.get(key)

    if cached_result:
        return QueryResults(json.loads(str(cached_result)))

    return None


def get_or_execute_query_result(
    query: str, catalog: Catalog, execute_query: Callable[[str], QueryExecutionResult]
) -> QueryExecutionResult:
    cached_result = get_cached_query_result(query, catalog)
    if cached_result:
        return QueryExecutionSuccessResult(cached_result)

    execution_result = execute_query(query)

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
