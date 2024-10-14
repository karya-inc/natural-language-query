from dataclasses import dataclass
from typing import Callable

from .status import AgentStatus


@dataclass
class AgentConfig:
    update_callback: Callable[[AgentStatus], None] = None
