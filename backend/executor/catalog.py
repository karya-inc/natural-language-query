from typing import Literal, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Catalog:
    """
    A catalog is a representation of a database provider (e.g., postgres or ephemeral like sqlite for intermediate results),
    the schema of the database, alongside annotations of key columns.
    """

    provider: Literal["postgres", "sqlite"]
    schema: Dict[str, Any]  # A dictionary representing tables and their columns
    annotations: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ephemeral: bool = False
    connection_params: Optional[Dict[str, Any]] = None