from dataclasses import dataclass, field
from typing import Callable, Optional

from dependencies.auth import AuthenticatedUserInfo

from .status import AgentStatus


@dataclass
class AgentConfig:
    user_info: AuthenticatedUserInfo
    update_callback: Optional[Callable[[AgentStatus], None]] = field(default=None)
