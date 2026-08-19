from __future__ import annotations

import math
from typing import Any, Mapping

import numpy as np


class ObservationEncoder:
    GOALS = ("DIAMOND", "NETHER_PORTAL", "WOODEN_SWORD", "KILL_ZOMBIE")
    DIMENSIONS = ("NORMAL", "NETHER", "THE_END")
    INVENTORY_KEYS = (
        "logs", "planks", "sticks", "crafting_table", "wooden_pickaxe",
        "stone_pickaxe", "cobblestone", "raw_iron", "iron_ingot",
        "iron_pickaxe", "wooden_sword", "diamond", "obsidian", "flint",
        "flint_and_steel",
    )
    FEATURE_SIZE = 111

    def encode(self, observation: Mapping[str, Any]) -> np.ndarray:
        max_air = max(1.0, self._number(observation.get("max_air"), 300.0))
        yaw = math.radians(self._number(observation.get("yaw"), 0.0))
        pitch = self._number(observation.get("pitch"), 0.0)
        slot = self._number(observation.get("selected_slot"), 0.0)

        values: list[float] = [
            self._clip(self._number(observation.get("health"), 20.0) / 20.0, 0.0, 1.0),
            self._clip(self._number(observation.get("food"), 20.0) / 20.0, 0.0, 1.0),
            self._clip(self._number(observation.get("air"), max_air) / max_air, 0.0, 1.0),
            self._clip((self._number(observation.get("y"), 64.0) + 64.0) / 448.0, 0.0, 1.0),
            math.sin(yaw),
            math.cos(yaw),
            self._clip(pitch / 90.0, -1.0, 1.0),
            1.0 if observation.get("on_ground", False) else 0.0,
            self._clip(slot / 8.0, 0.0, 1.0),
        ]

        dimension = str(observation.get("dimension", "NORMAL"))
        values.extend(1.0 if dimension == item else 0.0 for item in self.DIMENSIONS)

        goal = str(observation.get("goal", "WOODEN_SWORD"))
        values.extend(1.0 if goal == item else 0.0 for item in self.GOALS)

        inventory = observation.get("inventory", {})
        if not isinstance(inventory, Mapping):
            inventory = {}
        for key in self.INVENTORY_KEYS:
            values.append(self._clip(self._number(inventory.get(key), 0.0) / 64.0, 0.0, 1.0))

        grid = observation.get("local_grid", [])
        if not isinstance(grid, (list, tuple)):
            grid = []
        for i in range(75):
            category = self._number(grid[i], 0.0) if i < len(grid) else 0.0
            values.append(self._clip(category / 15.0, 0.0, 1.0))

        values.extend([
            self._clip(self._number(observation.get("target_block_category"), 0.0) / 15.0, 0.0, 1.0),
            self._distance(observation.get("target_block_distance")),
            self._clip(self._number(observation.get("target_entity_category"), 0.0) / 3.0, 0.0, 1.0),
            self._distance(observation.get("target_entity_distance")),
            self._clip(self._number(observation.get("nearby_zombies"), 0.0) / 10.0, 0.0, 1.0),
        ])

        array = np.asarray(values, dtype=np.float32)
        if array.shape != (self.FEATURE_SIZE,):
            raise ValueError(f"Encoder produced {array.shape}, expected ({self.FEATURE_SIZE},)")
        return array

    @staticmethod
    def _number(value: Any, fallback: float = 0.0) -> float:
        try:
            number = float(value)
            return number if math.isfinite(number) else fallback
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _clip(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def _distance(self, value: Any) -> float:
        distance = self._number(value, -1.0)
        if distance < 0:
            return 0.0
        return self._clip(distance / 8.0, 0.0, 1.0)
