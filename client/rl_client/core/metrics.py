from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import statistics


@dataclass(frozen=True)
class EpisodeMetric:
    episode: int
    steps: int
    reward: float
    success: bool
    reason: str


class MetricHistory:
    def __init__(self, capacity: int = 1000) -> None:
        self._episodes: deque[EpisodeMetric] = deque(maxlen=max(1, capacity))

    def add(self, item: EpisodeMetric) -> None:
        self._episodes.append(item)

    def snapshot(self) -> list[EpisodeMetric]:
        return list(self._episodes)

    @property
    def success_rate(self) -> float:
        if not self._episodes:
            return 0.0
        return sum(1 for item in self._episodes if item.success) / len(self._episodes)

    @property
    def best_reward(self) -> float:
        return max((item.reward for item in self._episodes), default=0.0)

    @property
    def average_reward(self) -> float:
        values = [item.reward for item in self._episodes]
        return statistics.fmean(values) if values else 0.0
