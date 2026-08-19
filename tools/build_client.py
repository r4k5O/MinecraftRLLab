#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run(cmd: list[str], cwd: Path) -> None:
    print("\n" + "=" * 88)
    print("NATIVE BUILD COMMAND")
    print(" ".join(cmd))
    print("=" * 88 + "\n")
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    client = root / "client"
    out = root / args.output
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    build_info = {
        "version": os.getenv("MCRL_VERSION", "0.3.0-dev"),
        "build": os.getenv("GITHUB_RUN_NUMBER", "local"),
        "commit": os.getenv("GITHUB_SHA", "working-tree")[:12],
        "channel": "nightly",
        "build_mode": "normal",
    }
    (client / "BUILD_INFO.json").write_text(json.dumps(build_info, indent=2), encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--enable-plugin=pyside6",
        "--show-scons",
        "--assume-yes-for-downloads",
        "--output-dir=" + str(out),
        "--output-filename=MinecraftRLLab",
        "--include-data-file=BUILD_INFO.json=BUILD_INFO.json",
        str(client / "run_client.py"),
    ]
    run(cmd, client)
    dist_dirs = list(out.glob("*.dist"))
    if not dist_dirs:
        raise SystemExit("Nuitka did not produce a .dist directory")
    print(f"DIST_DIR={dist_dirs[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
