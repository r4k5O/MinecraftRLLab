from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random

import numpy as np


@dataclass(frozen=True)
class ReplayBatch:
    states: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    next_states: np.ndarray
    dones: np.ndarray


class ReplayBuffer:
    def __init__(self, capacity: int = 50_000, seed: int | None = None):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._data: deque[tuple[np.ndarray, int, float, np.ndarray, bool]] = deque(maxlen=capacity)
        self._random = random.Random(seed)

    def add(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool) -> None:
        self._data.append((
            np.asarray(state, dtype=np.float32).copy(),
            int(action),
            float(reward),
            np.asarray(next_state, dtype=np.float32).copy(),
            bool(done),
        ))

    def sample(self, batch_size: int) -> ReplayBatch:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > len(self._data):
            raise ValueError("not enough transitions in replay buffer")
        rows = self._random.sample(list(self._data), batch_size)
        states, actions, rewards, next_states, dones = zip(*rows)
        return ReplayBatch(
            np.stack(states).astype(np.float32, copy=False),
            np.asarray(actions, dtype=np.int64),
            np.asarray(rewards, dtype=np.float32),
            np.stack(next_states).astype(np.float32, copy=False),
            np.asarray(dones, dtype=np.float32),
        )

    def __len__(self) -> int:
        return len(self._data)
