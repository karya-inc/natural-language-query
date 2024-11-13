from dataclasses import dataclass, field
from typing import Any, List, Optional

from executor.config import AgentConfig
from executor.tools import AgentTools

from .catalog import Catalog
from .loop import agentic_loop


@dataclass
class NLQExecutor:
    tools: Optional[AgentTools] = field(default=None)
    config: Optional[AgentConfig] = field(default=None)
    nlq: Optional[str] = field(default=None)
    catalogs: List[Catalog] = field(default_factory=list)

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

        if not self.tools or not self.config or len(self.catalogs) == 0:
            raise ValueError(
                "NLQExecutor requires tools, config, and catalogs to be set before execution."
            )

        if not self.nlq:
            self.nlq = nlq
        return agentic_loop(
            self.nlq, self.catalogs, self.tools, self.config, lambda x: None
        )
