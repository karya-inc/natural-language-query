from typing import Any, Dict, List

from .catalog import Catalog
from .query import Query


class Result:
    """
    A representation of a query that has been executed
    """

    query: Query
    source_catalogs: List[Catalog]
    data: List[Dict[str, Any]]
