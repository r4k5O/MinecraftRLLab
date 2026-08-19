from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class BuildChannel(str, Enum):
    VERIFIED = "verified"
    NIGHTLY = "nightly"


class VerificationState(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    FAILED = "failed"


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
