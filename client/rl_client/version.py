from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import os

APP_VERSION = "0.3.0-dev"
PROTOCOL_VERSION = 1


@dataclass(frozen=True)
class BuildInfo:
    version: str = APP_VERSION
    build: str = "local"
    commit: str = "working-tree"
    channel: str = "development"


def _candidate_paths() -> list[Path]:
    here = Path(__file__).resolve()
    return [
        here.parents[2] / "BUILD_INFO.json",
        here.parents[1] / "BUILD_INFO.json",
        Path.cwd() / "BUILD_INFO.json",
    ]


def load_build_info() -> BuildInfo:
    for path in _candidate_paths():
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                return BuildInfo(
                    version=str(raw.get("version", APP_VERSION)),
                    build=str(raw.get("build", "local")),
                    commit=str(raw.get("commit", "working-tree")),
                    channel=str(raw.get("channel", "development")),
                )
            except (OSError, ValueError, TypeError):
                pass
    return BuildInfo(
        build=os.getenv("GITHUB_RUN_NUMBER", "local"),
        commit=os.getenv("GITHUB_SHA", "working-tree")[:12],
        channel=os.getenv("MCRL_CHANNEL", "development"),
    )


def display_version() -> str:
    info = load_build_info()
    return f"MinecraftRLLab {info.version} (build {info.build}, {info.commit}, {info.channel})"
