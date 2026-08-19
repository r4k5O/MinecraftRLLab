from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile


class PackageValidationError(RuntimeError):
    pass


ProgressCallback = Callable[[int, int | None], None]
_SHA_LINE_RE = re.compile(r"^([0-9a-fA-F]{64})\s+[ *](.+?)\s*$")


def parse_sha256sums(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = _SHA_LINE_RE.match(line)
        if match:
            result[match.group(2)] = match.group(1).lower()
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected: str) -> None:
    expected_normalized = expected.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_normalized):
        raise PackageValidationError("Invalid SHA-256 value")
    actual = sha256_file(Path(path))
    if actual != expected_normalized:
        raise PackageValidationError(f"SHA-256 mismatch for {Path(path).name}")


def _validated_destination(base: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    pure = Path(normalized)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise PackageValidationError(f"Unsafe archive path: {member_name}")
    target = (base / pure).resolve()
    root = base.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PackageValidationError(f"Archive path escapes destination: {member_name}") from exc
    return target


def _single_root(destination: Path) -> Path:
    entries = [p for p in destination.iterdir() if p.name not in {".DS_Store"}]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return destination


def safe_extract_archive(archive: Path, destination: Path) -> Path:
    archive = Path(archive)
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                target = _validated_destination(destination, info.filename)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
        return _single_root(destination)

    try:
        with tarfile.open(archive, "r:*") as tf:
            members = tf.getmembers()
            for member in members:
                _validated_destination(destination, member.name)
                if member.issym() or member.islnk() or member.isdev():
                    raise PackageValidationError(f"Unsupported archive member: {member.name}")
            for member in members:
                target = _validated_destination(destination, member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                source = tf.extractfile(member)
                if source is None:
                    raise PackageValidationError(f"Could not read archive member: {member.name}")
                with source, target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
                try:
                    target.chmod(member.mode & 0o777)
                except OSError:
                    pass
        return _single_root(destination)
    except tarfile.TarError as exc:
        raise PackageValidationError(f"Unsupported or damaged archive: {archive.name}") from exc


def validate_package_root(root: Path, platform: str) -> dict:
    root = Path(root)
    metadata_path = root / "PACKAGE_INFO.json"
    if not metadata_path.is_file():
        raise PackageValidationError("PACKAGE_INFO.json is missing")
    try:
        info = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise PackageValidationError("PACKAGE_INFO.json is invalid") from exc
    if not isinstance(info, dict):
        raise PackageValidationError("PACKAGE_INFO.json must contain an object")
    expected_platform = platform.strip().lower()
    actual_platform = str(info.get("platform", "")).strip().lower()
    if actual_platform != expected_platform:
        raise PackageValidationError(f"Package platform mismatch: {actual_platform or 'unknown'}")
    executable = root / ("MinecraftRLLab.exe" if expected_platform == "windows" else "MinecraftRLLab")
    if not executable.is_file():
        raise PackageValidationError(f"Main executable is missing: {executable.name}")
    return info


def download_to(url: str, destination: Path, progress: ProgressCallback | None = None, timeout: float = 30.0) -> Path:
    if not url.lower().startswith("https://"):
        raise PackageValidationError("Only HTTPS downloads are allowed")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "MinecraftRLLab-Updater"})
    try:
        with urlopen(request, timeout=timeout) as response, destination.open("wb") as handle:
            raw_total = response.headers.get("Content-Length")
            total = int(raw_total) if raw_total and raw_total.isdigit() else None
            downloaded = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                downloaded += len(chunk)
                if progress:
                    progress(downloaded, total)
    except (HTTPError, URLError, OSError, ValueError) as exc:
        try:
            destination.unlink()
        except OSError:
            pass
        raise PackageValidationError(f"Download failed: {exc}") from exc
    return destination
