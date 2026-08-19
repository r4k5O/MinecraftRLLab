from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil
import subprocess
from typing import Sequence


class UpdateInstallError(RuntimeError):
    pass


def default_user_data_root() -> Path:
    return (Path.home() / ".minecraftrllab").resolve()


@dataclass(frozen=True)
class InstallLayout:
    root: Path
    app: Path
    updater: Path
    uninstall: Path
    staging: Path
    rollback: Path
    metadata: Path
    data_root: Path

    @classmethod
    def from_root(cls, root: Path, *, data_root: Path | None = None) -> "InstallLayout":
        resolved = Path(root).expanduser().resolve()
        data = (Path(data_root).expanduser().resolve() if data_root is not None else default_user_data_root())
        return cls(
            root=resolved,
            app=resolved / "app",
            updater=resolved / "updater",
            uninstall=resolved / "uninstall",
            staging=resolved / "update-staging",
            rollback=resolved / "rollback",
            metadata=resolved / "install.json",
            data_root=data,
        )


@dataclass(frozen=True)
class InstallMetadata:
    root: str
    data_root: str
    platform: str
    build: str
    executable: str

    def save(self, path: Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "InstallMetadata":
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            metadata = cls(
                root=str(raw["root"]),
                data_root=str(raw["data_root"]),
                platform=str(raw["platform"]),
                build=str(raw["build"]),
                executable=str(raw["executable"]),
            )
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise UpdateInstallError("Installation metadata is invalid") from exc
        layout = InstallLayout.from_root(Path(metadata.root), data_root=Path(metadata.data_root))
        if str(layout.root) != str(Path(metadata.root).expanduser().resolve()):
            raise UpdateInstallError("Installation root is invalid")
        return metadata


def _require_within(path: Path, root: Path, label: str) -> Path:
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(Path(root).resolve())
    except ValueError as exc:
        raise UpdateInstallError(f"{label} escapes its managed root") from exc
    return resolved


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def activate_staged_update(
    layout: InstallLayout,
    staged_app: Path,
    launch_command: Sequence[str],
    *,
    health_timeout: float = 30.0,
) -> None:
    staged = _require_within(Path(staged_app), layout.staging, "Staged application")
    if not staged.is_dir():
        raise UpdateInstallError("Staged application directory is missing")
    if not launch_command:
        raise UpdateInstallError("Health-check command is empty")

    layout.root.mkdir(parents=True, exist_ok=True)
    if layout.rollback.exists():
        _remove_path(layout.rollback)

    had_old_app = layout.app.exists()
    if had_old_app:
        layout.app.replace(layout.rollback)

    try:
        staged.replace(layout.app)
        result = subprocess.run(
            list(launch_command),
            cwd=layout.app,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=health_timeout,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            raise UpdateInstallError(f"Updated application health check failed with code {result.returncode}")
    except Exception as exc:
        if layout.app.exists():
            _remove_path(layout.app)
        if layout.rollback.exists():
            layout.rollback.replace(layout.app)
        if isinstance(exc, UpdateInstallError):
            raise
        raise UpdateInstallError(f"Could not activate staged update: {exc}") from exc
    else:
        if layout.rollback.exists():
            _remove_path(layout.rollback)


def allowed_uninstall_paths(layout: InstallLayout, *, remove_user_data: bool = False) -> tuple[Path, ...]:
    managed = (
        layout.app,
        layout.updater,
        layout.uninstall,
        layout.staging,
        layout.rollback,
        layout.metadata,
    )
    checked: list[Path] = []
    for path in managed:
        checked.append(_require_within(path, layout.root, "Uninstall path"))
    if remove_user_data:
        data = layout.data_root.resolve()
        home = Path.home().resolve()
        try:
            data.relative_to(home)
        except ValueError as exc:
            raise UpdateInstallError("Refusing to remove user data outside the user home directory") from exc
        if data == home:
            raise UpdateInstallError("Refusing to remove the user home directory")
        checked.append(data)
    return tuple(checked)


def write_apply_plan(
    path: Path,
    layout: InstallLayout,
    staged_app: Path,
    launch_command: Sequence[str],
    *,
    wait_pid: int | None = None,
    health_timeout: float = 30.0,
) -> Path:
    staged = _require_within(Path(staged_app), layout.staging, "Staged application")
    payload = {
        "root": str(layout.root),
        "data_root": str(layout.data_root),
        "staged_app": str(staged),
        "launch_command": list(launch_command),
        "wait_pid": wait_pid,
        "health_timeout": float(health_timeout),
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target
