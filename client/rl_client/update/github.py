from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import BuildChannel, ReleaseBuild


class UpdateError(RuntimeError):
    pass


class GitHubReleaseClient:
    API = "https://api.github.com"

    def __init__(self, owner: str, repo: str, timeout: float = 8.0) -> None:
        self.owner = owner
        self.repo = repo
        self.timeout = timeout

    def list_releases(self, limit: int = 20) -> list[ReleaseBuild]:
        url = f"{self.API}/repos/{self.owner}/{self.repo}/releases?per_page={max(1, min(100, limit))}"
        request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "MinecraftRLLab-Updater"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError) as exc:
            raise UpdateError(f"GitHub update check failed: {exc}") from exc
        if not isinstance(raw, list):
            raise UpdateError("GitHub returned an unexpected release payload")
        result: list[ReleaseBuild] = []
        for item in raw:
            if not isinstance(item, dict) or item.get("draft"):
                continue
            assets = tuple(a for a in item.get("assets", []) if isinstance(a, dict))
            result.append(ReleaseBuild(
                tag=str(item.get("tag_name", "")),
                name=str(item.get("name") or item.get("tag_name") or "Unnamed build"),
                url=str(item.get("html_url", "")),
                published_at=str(item.get("published_at", "")),
                prerelease=bool(item.get("prerelease", False)),
                body=str(item.get("body") or ""),
                assets=assets,
            ))
        return result

    def newest(self, channel: BuildChannel) -> ReleaseBuild | None:
        releases = self.list_releases()
        candidates = [release for release in releases if release.channel is channel and release.build_number is not None]
        return candidates[0] if candidates else None

    @staticmethod
    def is_newer(release: ReleaseBuild, installed_build: str | int) -> bool:
        available = release.build_number
        if available is None:
            return False
        try:
            installed = int(str(installed_build).strip())
        except (TypeError, ValueError):
            return False
        return available > installed
