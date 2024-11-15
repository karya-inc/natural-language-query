from dataclasses import dataclass, field
from typing import Callable, Optional

from executor.status import AgentStatus
from dependencies.auth import AuthenticatedUserInfo

@dataclass
class AgentConfig:
    user_info: AuthenticatedUserInfo
    update_callback: Optional[Callable[[AgentStatus], None]] = field(default=None)
