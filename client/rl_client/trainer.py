from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable, Any

from .agent import DQNAgent
from .environment import MinecraftRLEnv


@dataclass(frozen=True)
class TrainingConfig:
    goal: str
    profile: str = "SURVIVAL"
    episodes: int = 100
    episode_offset: int = 0
    max_steps_override: int | None = None


class Trainer:
    def __init__(self, env: MinecraftRLEnv, agent: DQNAgent,
                 on_event: Callable[[dict[str, Any]], None] | None = None):
        self.env = env
        self.agent = agent
        self.on_event = on_event or (lambda event: None)
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self, config: TrainingConfig) -> None:
        self._stop.clear()
        for local_episode in range(max(0, int(config.episodes))):
            if self._stop.is_set():
                break
            episode_number = int(config.episode_offset) + local_episode
            state, observation = self.env.reset(config.goal, config.profile, episode_number)
            episode_reward = 0.0
            steps = 0
            success = False
            terminal_reason = ""
            max_steps = int(config.max_steps_override or 0)

            self.on_event({
                "type": "reset", "episode": episode_number, "observation": observation,
                "epsilon": self.agent.epsilon,
            })

            while not self._stop.is_set():
                action = self.agent.act(state, training=True)
                result = self.env.step(action)
                self.agent.observe(state, action, result.reward, result.state, result.done)
                loss = self.agent.learn()
                state = result.state
                observation = result.observation
                steps += 1
                episode_reward += result.reward
                success = result.success
                terminal_reason = result.terminal_reason
                self.on_event({
                    "type": "step",
                    "episode": episode_number,
                    "step": steps,
                    "action": self.env.actions[action],
                    "reward": result.reward,
                    "episode_reward": episode_reward,
                    "done": result.done,
                    "success": result.success,
                    "terminal_reason": result.terminal_reason,
                    "loss": loss,
                    "epsilon": self.agent.epsilon,
                    "observation": observation,
                })
                if result.done or (max_steps > 0 and steps >= max_steps):
                    break

            self.on_event({
                "type": "episode",
                "episode": episode_number,
                "steps": steps,
                "reward": episode_reward,
                "success": success,
                "terminal_reason": terminal_reason or ("stopped" if self._stop.is_set() else "client_limit"),
                "epsilon": self.agent.epsilon,
            })
            if self._stop.is_set():
                break
        self.on_event({"type": "training_stopped" if self._stop.is_set() else "training_finished"})
