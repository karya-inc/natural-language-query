from sqlalchemy import Engine, create_engine
from urllib.parse import quote
from executor.catalog import Catalog


def get_engine(catalog: Catalog) -> Engine:
    if catalog.provider == "postgres":
        host = quote(catalog.connection_params["host"])
        dbname = quote(catalog.connection_params["dbname"])
        user = quote(catalog.connection_params["user"])
        password = quote(catalog.connection_params["password"])
        port = catalog.connection_params.get("port", 5432)

        # Setup connection to postgres
        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

        return engine

    else:
        raise NotImplementedError("Only postgres is supported at the moment")
