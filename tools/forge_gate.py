#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import os
from pathlib import Path
import re
import subprocess

TRAILER = "X-MCRL-Forge"
DEFAULT_FORGE_KEY = "MinecraftRLLab-Forge-26.2"
_TOKEN_RE = re.compile(rf"(?im)^{re.escape(TRAILER)}:\s*([0-9a-f]{{64}})\s*$")
_DOMAIN = b"MinecraftRLLab/full-source/v1\0"


def select_forge_key(configured_secret: str | None) -> str:
    """Use the repository secret when configured, otherwise the built-in Easteregg key."""
    secret = (configured_secret or "").strip()
    return secret if secret else DEFAULT_FORGE_KEY


def build_token(secret: str, tree_sha: str) -> str:
    if not secret:
        raise ValueError("secret must not be empty")
    tree = tree_sha.strip().lower()
    if not tree:
        raise ValueError("tree_sha must not be empty")
    return hmac.new(secret.encode("utf-8"), _DOMAIN + tree.encode("ascii"), hashlib.sha256).hexdigest()


def extract_token(message: str) -> str | None:
    match = _TOKEN_RE.search(message or "")
    return match.group(1).lower() if match else None


def resolve_mode(message: str, secret: str, tree_sha: str) -> str:
    if not secret:
        return "normal"
    supplied = extract_token(message)
    if not supplied:
        return "normal"
    expected = build_token(secret, tree_sha)
    return "full-source" if hmac.compare_digest(supplied, expected) else "normal"


def _git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def detect_repository_mode(repo: Path, secret: str) -> tuple[str, str]:
    message = _git("log", "-1", "--pretty=%B", cwd=repo)
    tree_sha = _git("rev-parse", "HEAD^{tree}", cwd=repo)
    return resolve_mode(message, secret, tree_sha), tree_sha


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve MinecraftRLLab GitHub build mode without exposing the forge secret.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--secret-env", default="MCRL_FORGE_KEY")
    parser.add_argument("--github-output", default=os.getenv("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    secret = select_forge_key(os.getenv(args.secret_env, ""))
    mode, tree_sha = detect_repository_mode(Path(args.repo).resolve(), secret)
    forge = "true" if mode == "full-source" else "false"

    # Never print the secret or expected token. Only the resolved mode is public.
    print(f"mode={mode}")
    print(f"forge={forge}")
    print(f"tree={tree_sha}")

    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write(f"mode={mode}\n")
            handle.write(f"forge={forge}\n")
            handle.write(f"tree={tree_sha}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
