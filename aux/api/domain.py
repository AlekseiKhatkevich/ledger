import uuid
from dataclasses import dataclass
from typing import Literal


@dataclass
class HealthCheckStatus:
    status: Literal['OK']


@dataclass
class NNGNodeInfo:
    dialers: list[str]
    local_addr: str
    name: str
    event_state: bool
    seen_messages: set[uuid.UUID]
    peers: set[str]
