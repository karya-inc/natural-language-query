from typing import Any, List

from .catalog import Catalog
from .loop import agentic_loop


class NLQExecutor:
    def __init__(self):
        self.tools = None
        self.config = None
        self.catalogs = None
        self.nlq = None

    def with_tools(self, tools) -> "NLQExecutor":
        """Sets the tools to be used by the executor."""
        self.tools = tools
        return self

    def with_config(self, config) -> "NLQExecutor":
        """Sets the configuration for the executor."""
        self.config = config
        return self

    def with_catalogs(self, catalogs: List[Catalog]) -> "NLQExecutor":
        """Sets the catalogs that will be used by the executor."""
        self.catalogs = catalogs
        return self

    def execute(self, nlq: str) -> Any:
        """Executes the agentic loop with the given natural language query (NLQ)."""
        if not all([self.tools, self.config, self.catalogs]):
            raise ValueError(
                "NLQExecutor requires tools, config, and catalogs to be set before execution."
            )

        self.nlq = nlq
        return agentic_loop(self.nlq, self.catalogs, self.tools, self.config)
