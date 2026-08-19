from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .detection import detect_server


@dataclass(frozen=True)
class InstallResult:
    destination: Path
    replaced: tuple[Path, ...]


def bundled_plugin_candidates(app_root: Path) -> list[Path]:
    return sorted((app_root / "server-plugin").glob("MinecraftRLLab*.jar"))


def install_plugin(server_root: str | Path, plugin_jar: str | Path) -> InstallResult:
    server = detect_server(server_root)
    if not server.root.is_dir():
        raise FileNotFoundError(f"Server folder not found: {server.root}")
    server.plugins.mkdir(parents=True, exist_ok=True)
    source = Path(plugin_jar).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Plugin JAR not found: {source}")
    replaced: list[Path] = []
    for old in server.plugins.glob("MinecraftRLLab*.jar"):
        if old.name != source.name:
            old.unlink()
            replaced.append(old)
    destination = server.plugins / source.name
    shutil.copy2(source, destination)
    return InstallResult(destination, tuple(replaced))
