from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentTaskResult:
    name: str
    payload: Any
