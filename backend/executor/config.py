from dataclasses import dataclass, field
from typing import Callable, Optional

from executor.status import AgentStatus


@dataclass
class AgentConfig:
    update_callback: Optional[Callable[[AgentStatus], None]] = field(default=None)
