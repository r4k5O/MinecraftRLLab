#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess

from forge_gate import TRAILER, build_token, select_forge_key


def main() -> int:
    secret = select_forge_key(os.getenv("MCRL_FORGE_KEY", ""))
    root = Path(__file__).resolve().parents[1]
    tree_sha = subprocess.check_output(["git", "write-tree"], cwd=root, text=True).strip()
    token = build_token(secret, tree_sha)
    print(f"{TRAILER}: {token}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
