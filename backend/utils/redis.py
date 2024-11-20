import json
from typing import Callable, Literal, Optional
from redis import Redis
from os import environ
from executor.catalog import Catalog
from executor.state import QueryResults

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
    cached_result = str(redis_client.get(key))

    if cached_result:
        return QueryResults(json.loads(cached_result))

    return None


def get_or_execute_query_result(
    query: str, catalog: Catalog, execute_query: Callable[[str], QueryResults]
) -> QueryResults:
    cached_result = get_cached_query_result(query, catalog)
    if cached_result:
        return cached_result

    result = execute_query(query)

    # Cache the result for 30 minutes
    key = get_redis_key("query_results", catalog.name, query.strip())
    redis_client.set(key, json.dumps(result), ex=REDIS_TTL)

    return result


def get_cached_categorical_values(catalog: Catalog, table: str) -> Optional[set]:
    key = get_redis_key("categorical", catalog.name, table)
    cached_result = str(redis_client.get(key))

    if cached_result:
        return set(json.loads(cached_result))

    return None


def get_cached_sample_rows(catalog: Catalog, table: str) -> Optional[set]:
    key = get_redis_key("samples", catalog.name, table)
    cached_result = str(redis_client.get(key))

    if cached_result:
        return set(json.loads(cached_result))

    return None
