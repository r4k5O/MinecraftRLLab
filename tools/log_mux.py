#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable

IMPORTANT_RE = re.compile(
    r"(?i)(fatal|error:|\berror\b|warning:|\bwarning\b|failed|failure|traceback|undefined reference|exception)"
)
PROGRESS_RE = re.compile(r"^\s*\[\d+[/\\]\d+\]")
COMPILER_RE = re.compile(
    r"(^|\s)"
    r"(?:gcc|g\+\+|clang|clang\+\+|cl(?:\.exe)?|link(?:\.exe)?|ld(?:\.exe)?|ccache)"
    r"(?:\s|$)"
    r"|\b(?:building|linking)\s+(?:c|cxx|rc)?\s*(?:object|static library|shared library|executable)\b"
    r"|[\\/](?:cl|link)\.exe\b"
    r"|^(?:nuitka-scons|scons:)",
    re.IGNORECASE,
)
STATUS_RE = re.compile(
    r"(?i)^(-- |nuitka-progress|generating|installing|building wheel|successfully|finished|completed|built target|\[notice\])"
)


@dataclass
class VisibleLogSampler:
    sample_every: int = 8
    head_lines: int = 80
    progress_every: int = 1
    compiler_every: int = 1

    def __post_init__(self) -> None:
        for name, value in (
            ("sample_every", self.sample_every),
            ("progress_every", self.progress_every),
            ("compiler_every", self.compiler_every),
        ):
            if value < 1:
                raise ValueError(f"{name} must be positive")
        if self.head_lines < 0:
            raise ValueError("head_lines must not be negative")
        self.total = 0
        self.visible = 0
        self.suppressed = 0
        self._progress_seen = 0
        self._compiler_seen = 0
        self._other_seen = 0

    def _record(self, emit: bool) -> bool:
        if emit:
            self.visible += 1
            return True
        self.suppressed += 1
        return False

    def should_emit(self, line: str) -> bool:
        self.total += 1

        if self.total <= self.head_lines or IMPORTANT_RE.search(line):
            return self._record(True)

        if PROGRESS_RE.search(line):
            self._progress_seen += 1
            return self._record(self._progress_seen % self.progress_every == 0)

        if COMPILER_RE.search(line):
            self._compiler_seen += 1
            return self._record(self._compiler_seen % self.compiler_every == 0)

        if STATUS_RE.search(line):
            return self._record(True)

        self._other_seen += 1
        return self._record(self._other_seen % self.sample_every == 0)


def run_logged(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    log_path: Path,
    sample_every: int = 8,
    head_lines: int = 80,
    progress_every: int = 1,
    compiler_every: int = 1,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    sampler = VisibleLogSampler(
        sample_every=sample_every,
        head_lines=head_lines,
        progress_every=progress_every,
        compiler_every=compiler_every,
    )

    if len(cmd) >= 2 and cmd[1] in {"-c", "-m"}:
        preview = f"{cmd[0]} {cmd[1]} <payload>"
        if len(cmd) > 3:
            preview += f" … (+{len(cmd)-3} args)"
    else:
        preview = " ".join(cmd[:3])
        if len(cmd) > 3:
            preview += f" … (+{len(cmd)-3} args)"
    if len(preview) > 240:
        preview = preview[:237] + "..."
    print("+ " + preview, flush=True)

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert process.stdout is not None
    with log_path.open("w", encoding="utf-8", errors="replace") as full_log:
        for raw in process.stdout:
            full_log.write(raw)
            line = raw.rstrip("\r\n")
            if sampler.should_emit(line):
                print(line, flush=True)
    process.stdout.close()
    return_code = process.wait()

    print(
        f"LOGMUX visible={sampler.visible} total={sampler.total} suppressed={sampler.suppressed} "
        f"progress=1/{sampler.progress_every} compiler=1/{sampler.compiler_every} other=1/{sampler.sample_every}",
        flush=True,
    )
    print(f"Full log: {log_path}", flush=True)

    completed = subprocess.CompletedProcess(cmd, return_code)
    if check and return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd)
    return completed


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream useful build output while preserving the complete log")
    parser.add_argument("--log", required=True)
    parser.add_argument("--sample-every", type=int, default=8)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--compiler-every", type=int, default=1)
    parser.add_argument("--head-lines", type=int, default=80)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    return args


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_logged(
        list(args.command),
        log_path=Path(args.log),
        sample_every=args.sample_every,
        progress_every=args.progress_every,
        compiler_every=args.compiler_every,
        head_lines=args.head_lines,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
