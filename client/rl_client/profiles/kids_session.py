from __future__ import annotations
from dataclasses import dataclass
from ..learning.achievements import AchievementTracker


@dataclass(frozen=True)
class KidsEventResult:
    reward: float
    success: bool
    unlocked: list[str]


class KidsSessionModel:
    def __init__(self, unlocked: set[str] | None = None) -> None:
        self.goal = "WOODEN_SWORD"
        self.reward = 0.0
        self.real_successes = 0
        self.achievements = AchievementTracker(unlocked)

    def select_goal(self, goal: str) -> None:
        self.goal = str(goal)

    def consume_training_event(self, event: dict) -> KidsEventResult:
        reward = float(event.get("reward", event.get("episode_reward", 0.0)) or 0.0)
        self.reward = reward
        success = bool(event.get("success", False))
        unlocked: list[str] = []
        if event.get("type") == "episode" and not bool(event.get("demo", False)):
            payload = dict(event)
            payload.setdefault("goal", self.goal)
            unlocked = self.achievements.consume("episode.completed", payload)
            if success:
                self.real_successes += 1
        return KidsEventResult(reward, success, unlocked)
