from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ServerInstallation:
    root: Path
    plugins: Path
    paper_jars: tuple[Path, ...]
    installed_rl_plugin: Path | None

    @property
    def looks_valid(self) -> bool:
        return bool(self.paper_jars) and self.plugins.is_dir()


def detect_server(path: str | Path) -> ServerInstallation:
    root = Path(path).expanduser().resolve()
    plugins = root / "plugins"
    jars = tuple(sorted(root.glob("paper-*.jar")))
    candidates = sorted(plugins.glob("MinecraftRLLab*.jar")) if plugins.is_dir() else []
    installed = candidates[-1] if candidates else None
    return ServerInstallation(root, plugins, jars, installed)
