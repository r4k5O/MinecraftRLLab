from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class TrainingState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    FINISHED = "finished"
    ERROR = "error"


@dataclass
class AppState:
    connection: ConnectionState = ConnectionState.DISCONNECTED
    training: TrainingState = TrainingState.IDLE
    player: str = ""
    goal: str = "WOODEN_SWORD"
    profile: str = "CURRICULUM"
    episode: int = 0
    step: int = 0
    reward: float = 0.0
    epsilon: float = 1.0
    loss: float | None = None
    last_action: str = "NOOP"
    observation: dict[str, Any] = field(default_factory=dict)
