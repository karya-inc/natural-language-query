from typing import Any, Dict, List
import uuid
from .catalog import Catalog
from .query import Query


class Result:
    """
    A representation of a query that has been executed
    """

    id: uuid.UUID
    query: Query
    source_catalogs: List[Catalog]
    data: List[Dict[str, Any]]

    def __init__(
        self, query: Query, source_catalogs: List[Catalog], data: List[Dict[str, Any]]
    ):
        self.id = uuid.uuid4()
        self.query = query
        self.source_catalogs = source_catalogs
        self.data = data
