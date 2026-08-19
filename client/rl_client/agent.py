from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np

try:
    import torch
    from torch import nn
    import torch.nn.functional as F
except ImportError:  # pragma: no cover - handled at runtime
    torch = None
    nn = None
    F = None

from .replay import ReplayBuffer


if nn is not None:
    class QNetwork(nn.Module):
        def __init__(self, input_size: int, action_count: int):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, 256),
                nn.ReLU(),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Linear(128, action_count),
            )

        def forward(self, x):
            return self.net(x)
else:
    QNetwork = object


class DQNAgent:
    def __init__(
        self,
        input_size: int,
        action_count: int,
        *,
        seed: int = 0,
        gamma: float = 0.99,
        learning_rate: float = 1e-3,
        batch_size: int = 64,
        replay_capacity: int = 50_000,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay_steps: int = 40_000,
        target_update_interval: int = 500,
    ):
        if torch is None:
            raise RuntimeError("PyTorch is required for DQN training. Install torch or use manual stepping.")
        if input_size <= 0 or action_count <= 0:
            raise ValueError("input_size and action_count must be positive")
        self.input_size = int(input_size)
        self.action_count = int(action_count)
        self.gamma = float(gamma)
        self.batch_size = int(batch_size)
        self.epsilon_start = float(epsilon_start)
        self.epsilon_end = float(epsilon_end)
        self.epsilon_decay_steps = max(1, int(epsilon_decay_steps))
        self.target_update_interval = max(1, int(target_update_interval))
        self.random = random.Random(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.online = QNetwork(self.input_size, self.action_count).to(self.device)
        self.target = QNetwork(self.input_size, self.action_count).to(self.device)
        self.target.load_state_dict(self.online.state_dict())
        self.target.eval()
        self.optimizer = torch.optim.Adam(self.online.parameters(), lr=learning_rate)
        self.replay = ReplayBuffer(replay_capacity, seed=seed)
        self.environment_steps = 0
        self.learning_steps = 0

    @property
    def epsilon(self) -> float:
        fraction = min(1.0, self.environment_steps / self.epsilon_decay_steps)
        return self.epsilon_start + fraction * (self.epsilon_end - self.epsilon_start)

    def act(self, state: np.ndarray, training: bool = True) -> int:
        if training and self.random.random() < self.epsilon:
            return self.random.randrange(self.action_count)
        tensor = torch.as_tensor(np.asarray(state, dtype=np.float32), device=self.device).unsqueeze(0)
        with torch.no_grad():
            return int(self.online(tensor).argmax(dim=1).item())

    def observe(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool) -> None:
        self.replay.add(state, action, reward, next_state, done)
        self.environment_steps += 1

    def learn(self) -> float | None:
        if len(self.replay) < self.batch_size:
            return None
        batch = self.replay.sample(self.batch_size)
        states = torch.as_tensor(batch.states, device=self.device)
        actions = torch.as_tensor(batch.actions, device=self.device).unsqueeze(1)
        rewards = torch.as_tensor(batch.rewards, device=self.device)
        next_states = torch.as_tensor(batch.next_states, device=self.device)
        dones = torch.as_tensor(batch.dones, device=self.device)

        q_values = self.online(states).gather(1, actions).squeeze(1)
        with torch.no_grad():
            next_actions = self.online(next_states).argmax(dim=1, keepdim=True)
            next_q = self.target(next_states).gather(1, next_actions).squeeze(1)
            target_values = rewards + (1.0 - dones) * self.gamma * next_q

        loss = F.smooth_l1_loss(q_values, target_values)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online.parameters(), 10.0)
        self.optimizer.step()
        self.learning_steps += 1
        if self.learning_steps % self.target_update_interval == 0:
            self.target.load_state_dict(self.online.state_dict())
        return float(loss.item())

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "input_size": self.input_size,
            "action_count": self.action_count,
            "online": self.online.state_dict(),
            "target": self.target.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "environment_steps": self.environment_steps,
            "learning_steps": self.learning_steps,
        }, path)

    def load(self, path: str | Path) -> None:
        checkpoint = torch.load(Path(path), map_location=self.device, weights_only=False)
        if int(checkpoint["input_size"]) != self.input_size or int(checkpoint["action_count"]) != self.action_count:
            raise ValueError("Checkpoint dimensions do not match this environment")
        self.online.load_state_dict(checkpoint["online"])
        self.target.load_state_dict(checkpoint["target"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.environment_steps = int(checkpoint.get("environment_steps", 0))
        self.learning_steps = int(checkpoint.get("learning_steps", 0))
