from dataclasses import dataclass
from executor.catalog import Catalog
from sqlalchemy import Engine, create_engine, text


class QueryExecutionPipeline:
    catalog: Catalog
    engine: Engine

    def __init__(self, catalog: Catalog):
        self.catalog = catalog

        if self.catalog.provider == "postgres":
            host = self.catalog.connection_params["host"]
            dbname = self.catalog.connection_params["dbname"]
            user = self.catalog.connection_params["user"]
            password = self.catalog.connection_params["password"]

            # Setup connection to postgres
            engine = create_engine(f"postgresql://{user}:{password}@{host}/{dbname}")
            self.engine = engine

        else:
            raise NotImplementedError("Only postgres is supported at the moment")

    def execute(self, query: str):
        with self.engine.connect() as conn:
            stmt = text(query)
            result = conn.execute(stmt)
            return result.fetchall()
