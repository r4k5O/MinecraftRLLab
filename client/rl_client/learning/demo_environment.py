from __future__ import annotations
import random


class DemoEnvironment:
    ACTIONS = ("LOOK_AROUND", "MOVE_FORWARD", "BREAK_BLOCK", "CRAFT_WOODEN_SWORD", "CELEBRATE")

    def __init__(self, seed: int = 7) -> None:
        self.seed = seed
        self._rng = random.Random(seed)
        self.goal = "WOODEN_SWORD"
        self.step_index = 0
        self.total_reward = 0.0

    def reset(self, goal: str = "WOODEN_SWORD") -> dict:
        self._rng = random.Random(self.seed)
        self.goal = goal
        self.step_index = 0
        self.total_reward = 0.0
        return {"demo": True, "goal": goal, "step": 0, "reward": 0.0, "total_reward": 0.0}

    def step(self) -> dict:
        self.step_index += 1
        action = self.ACTIONS[min(self.step_index - 1, len(self.ACTIONS) - 1)]
        base = (0.05, 0.12, 0.35, 2.5, 0.5)[min(self.step_index - 1, 4)]
        reward = round(base + self._rng.uniform(-0.02, 0.02), 3)
        self.total_reward = round(self.total_reward + reward, 3)
        done = self.step_index >= 5
        return {"demo": True, "goal": self.goal, "step": self.step_index, "action": action, "reward": reward, "total_reward": self.total_reward, "done": done, "success": done}
