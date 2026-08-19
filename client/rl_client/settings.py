from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass
class Settings:
    host: str = "127.0.0.1"
    port: int = 8765
    player: str = ""
    github_owner: str = "r4k5O"
    github_repo: str = "MinecraftRLLab"
    update_channel: str = "verified"
    auto_check_updates: bool = True
    language: str = "en"
    experience_mode: str = "research"
    onboarding_complete: bool = False
    kid_name: str = "Explorer"


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / ".minecraftrllab" / "settings.json")

    def load(self) -> Settings:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            known = {k: v for k, v in data.items() if k in Settings.__dataclass_fields__}
            return Settings(**known)
        except (FileNotFoundError, OSError, ValueError, TypeError):
            return Settings()

    def save(self, settings: Settings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
