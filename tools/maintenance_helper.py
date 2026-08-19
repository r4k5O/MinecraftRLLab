#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "client"
if str(CLIENT) not in sys.path:
    sys.path.insert(0, str(CLIENT))

from rl_client.update.install import (
    InstallLayout,
    InstallMetadata,
    UpdateInstallError,
    activate_staged_update,
    allowed_uninstall_paths,
)


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def wait_for_pid_exit(pid: int | None, timeout: float = 60.0) -> None:
    if not pid:
        return
    deadline = time.monotonic() + timeout
    while _pid_exists(pid):
        if time.monotonic() >= deadline:
            raise UpdateInstallError(f"Timed out waiting for process {pid} to exit")
        time.sleep(0.2)


def perform_apply_plan(plan_path: Path) -> None:
    try:
        raw = json.loads(Path(plan_path).read_text(encoding="utf-8"))
        layout = InstallLayout.from_root(Path(raw["root"]), data_root=Path(raw["data_root"]))
        staged_app = Path(raw["staged_app"])
        launch_command = [str(item) for item in raw["launch_command"]]
        wait_pid = raw.get("wait_pid")
        health_timeout = float(raw.get("health_timeout", 30.0))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise UpdateInstallError("Update plan is invalid") from exc

    wait_for_pid_exit(int(wait_pid) if wait_pid else None)
    health_command = [*launch_command, "--health-check"]
    activate_staged_update(layout, staged_app, health_command, health_timeout=health_timeout)
    subprocess.Popen(launch_command, cwd=layout.app, start_new_session=True)
    try:
        Path(plan_path).unlink()
    except OSError:
        pass


def perform_uninstall(metadata_path: Path, *, remove_user_data: bool = False) -> None:
    metadata = InstallMetadata.load(Path(metadata_path))
    layout = InstallLayout.from_root(Path(metadata.root), data_root=Path(metadata.data_root))
    try:
        from installer.platform_integration import remove_platform_integration
        remove_platform_integration(metadata)
    except Exception:
        pass
    for path in allowed_uninstall_paths(layout, remove_user_data=remove_user_data):
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path, ignore_errors=False)
        else:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
    try:
        layout.root.rmdir()
    except OSError:
        pass


def _self_command(copy_path: Path) -> list[str]:
    if getattr(sys, "frozen", False) or not str(sys.argv[0]).lower().endswith(".py"):
        return [str(copy_path)]
    return [sys.executable, str(copy_path)]


def spawn_uninstall_worker(metadata_path: Path, *, remove_user_data: bool = False) -> None:
    temp_root = Path(tempfile.mkdtemp(prefix="mcrl-uninstall-"))
    source = Path(sys.argv[0]).resolve()
    suffix = source.suffix or (".exe" if os.name == "nt" else "")
    helper_copy = temp_root / ("MinecraftRLLab-Uninstall" + suffix)
    shutil.copy2(source, helper_copy)
    metadata_copy = temp_root / "install.json"
    shutil.copy2(metadata_path, metadata_copy)
    command = _self_command(helper_copy) + ["--uninstall-worker", str(metadata_copy)]
    if remove_user_data:
        command.append("--remove-user-data")
    subprocess.Popen(command, cwd=temp_root, start_new_session=True)


def main() -> int:
    parser = argparse.ArgumentParser(prog="MinecraftRLLab-Maintenance")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply-plan")
    mode.add_argument("--uninstall")
    mode.add_argument("--uninstall-worker")
    parser.add_argument("--remove-user-data", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply_plan:
            perform_apply_plan(Path(args.apply_plan))
        elif args.uninstall:
            spawn_uninstall_worker(Path(args.uninstall), remove_user_data=args.remove_user_data)
        else:
            perform_uninstall(Path(args.uninstall_worker), remove_user_data=args.remove_user_data)
    except UpdateInstallError as exc:
        print(f"MinecraftRLLab maintenance error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
