from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .encoder import ObservationEncoder


@dataclass(frozen=True)
class StepResult:
    state: np.ndarray
    observation: dict[str, Any]
    reward: float
    done: bool
    success: bool
    terminal_reason: str


class MinecraftRLEnv:
    def __init__(self, api, encoder: ObservationEncoder | None = None):
        self.api = api
        self.encoder = encoder or ObservationEncoder()
        info = api.info()
        self.actions = list(info.get("actions", []))
        self.goals = list(info.get("goals", []))
        self.profiles = list(info.get("profiles", []))
        if not self.actions:
            raise ValueError("Server did not advertise any RL actions")

    def reset(self, goal: str, profile: str = "SURVIVAL", episode: int = 0) -> tuple[np.ndarray, dict[str, Any]]:
        response = self.api.reset(goal, profile, episode)
        observation = self._observation(response)
        return self.encoder.encode(observation), observation

    def step(self, action_index: int) -> StepResult:
        if action_index < 0 or action_index >= len(self.actions):
            raise IndexError("action index out of range")
        response = self.api.step(self.actions[action_index])
        observation = self._observation(response)
        return StepResult(
            state=self.encoder.encode(observation),
            observation=observation,
            reward=float(response.get("reward", 0.0)),
            done=bool(response.get("done", False)),
            success=bool(response.get("success", False)),
            terminal_reason=str(response.get("terminal_reason", "")),
        )

    @staticmethod
    def _observation(response: dict[str, Any]) -> dict[str, Any]:
        observation = response.get("observation")
        if not isinstance(observation, dict):
            raise ValueError("Server response does not contain an observation object")
        return observation
