from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any


class BuildChannel(str, Enum):
    VERIFIED = "verified"
    NIGHTLY = "nightly"


class VerificationState(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"


_BUILD_RE = re.compile(r"(?:nightly|build)-(\d+)(?:-|$)", re.IGNORECASE)


@dataclass(frozen=True)
class ReleaseBuild:
    tag: str
    name: str
    url: str
    published_at: str
    prerelease: bool
    body: str
    assets: tuple[dict[str, Any], ...]

    @property
    def verification(self) -> VerificationState:
        lower = self.body.lower()
        if "verification:failed" in lower or "verification failed" in lower:
            return VerificationState.FAILED
        if self.prerelease:
            return VerificationState.PENDING
        return VerificationState.VERIFIED

    @property
    def channel(self) -> BuildChannel:
        return BuildChannel.NIGHTLY if self.prerelease else BuildChannel.VERIFIED

    @property
    def build_number(self) -> int | None:
        match = _BUILD_RE.search(self.tag)
        if not match:
            match = re.search(r"\b(?:build\s*#?|#)\s*(\d+)\b", self.name, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def asset_for(self, platform: str) -> dict[str, Any] | None:
        platform_key = platform.strip().lower()
        suffix = {
            "windows": "-Windows-x64.zip",
            "linux": "-Linux-x64.tar.gz",
        }.get(platform_key)
        if suffix is None:
            return None
        matches = [asset for asset in self.assets if str(asset.get("name", "")).endswith(suffix)]
        return matches[0] if len(matches) == 1 else None

    def checksum_asset(self) -> dict[str, Any] | None:
        matches = [asset for asset in self.assets if str(asset.get("name", "")) == "SHA256SUMS.txt"]
        return matches[0] if len(matches) == 1 else None
