from typing import Literal, Optional
from redis import Redis
from os import environ

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
