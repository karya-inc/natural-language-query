from dataclasses import dataclass

from .catalog import Catalog


@dataclass
class Query:
    """
    A representation of a query that has been generated from an AI to be executed on a catalog
    """

    nlq: str  # the original natural language query
    sql: str  # the generated sql query that will be executed
    catalog: Catalog  # the catalog that the query will be executed on
