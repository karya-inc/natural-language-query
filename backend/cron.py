import time
from os import environ

from redis import Connection
from db.catalog_utils import get_engine
from executor.catalog import Catalog
from sqlalchemy import text, Connection
from executor.catalog import Catalog
from utils.logger import get_logger
from utils.parse_catalog import parsed_catalogs
from utils.redis import get_redis_key, redis_client
from utils.rows_to_json import convert_rows_to_json

CACHE_INTERVAL_SEC = int(environ.get("CACHE_INTERVAL_SEC", 60))
DB_SEED_LIMIT = int(environ.get("DB_SEED_LIMIT", 2))

logger = get_logger("[CRON - REDIS CACHE]")


def cache_sample_table_rows(
    conn: Connection, catalog: Catalog, table_name: str
) -> None:
    """
    Cache a sample for the rows in a table
    """
    # Get the data from the database
    stmt = text(f"SELECT * FROM {table_name} ORDER BY random() LIMIT {DB_SEED_LIMIT}")
    data = conn.execute(stmt).fetchall()

    # Cache data in redis
    data_json = convert_rows_to_json(data)
    if data_json:
        key = get_redis_key(
            "samples",
            catalog.name,
            table_name,
        )
        redis_client.set(key, data_json)


def cache_categorical_tables(
    conn: Connection, catalog: Catalog, table_name: str, columns: list[str]
) -> None:
    """
    Cache the categorical columns in a table
    """
    # Get the data from the database
    column_names = ", ".join(columns)
    stmt = text(f"SELECT {column_names} FROM {table_name}")
    data = conn.execute(stmt).fetchall()

    # Cache data in redis
    data_json = convert_rows_to_json(data)
    if data_json:
        key = get_redis_key(
            "categorical",
            catalog.name,
            table_name,
        )
        redis_client.set(key, data_json)


def seed_sample_data_redis() -> None:
    """
    Seed the redis cache with sample data and categorical values from the database
    """
    catalogs = parsed_catalogs.catalogs
    for catalog in catalogs:
        engine = get_engine(catalog)

        with engine.connect() as connection:
            for table_name, table_info in catalog.schema.items():
                cache_sample_table_rows(connection, catalog, table_name)

                if table_info.get("is_categorical", False):
                    columns_to_cache = table_info.get("columns_to_cache", [])
                    if len(columns_to_cache) == 0:
                        logger.warning(
                            f"No categorical columns to cache for {table_name} even though is_categorical is set to true"
                        )
                        continue

                    logger.info(f"Caching categorical columns for {table_name}")
                    cache_categorical_tables(
                        connection, catalog, table_name, columns_to_cache
                    )


if __name__ == "__main__":
    while True:
        logger.info("Seeding sample data in redis")
        seed_sample_data_redis()
        logger.info("Sample data seeded in redis. Sleeping...")
        time.sleep(CACHE_INTERVAL_SEC)
