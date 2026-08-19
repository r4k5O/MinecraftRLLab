from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path


@dataclass
class LearningProgress:
    tutorial_steps: dict[str, int] = field(default_factory=dict)
    completed_tutorials: list[str] = field(default_factory=list)
    unlocked_achievements: list[str] = field(default_factory=list)
    stars: int = 0


class ProgressStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / ".minecraftrllab" / "learning-progress.json")

    def load(self) -> LearningProgress:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return LearningProgress(
                tutorial_steps={str(k): int(v) for k, v in data.get("tutorial_steps", {}).items()},
                completed_tutorials=list(data.get("completed_tutorials", [])),
                unlocked_achievements=list(data.get("unlocked_achievements", [])),
                stars=int(data.get("stars", 0)),
            )
        except (FileNotFoundError, OSError, ValueError, TypeError):
            return LearningProgress()

    def save(self, progress: LearningProgress) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(progress), indent=2, ensure_ascii=False), encoding="utf-8")
