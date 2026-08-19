from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import platform as platform_module
import shutil
import subprocess
import sys
from typing import Callable

from .github import GitHubReleaseClient
from .install import InstallLayout, InstallMetadata, UpdateInstallError, write_apply_plan
from .models import BuildChannel, ReleaseBuild, VerificationState
from .package import (
    PackageValidationError,
    download_to,
    parse_sha256sums,
    safe_extract_archive,
    validate_package_root,
    verify_file,
)
from ..version import load_build_info


class UpdateError(RuntimeError):
    pass


@dataclass(frozen=True)
class UpdateCandidate:
    release: ReleaseBuild
    asset: dict
    checksum_asset: dict
    platform: str


@dataclass(frozen=True)
class StagedUpdate:
    candidate: UpdateCandidate
    package_root: Path
    plan_path: Path
    helper_path: Path


def discover_install_layout(executable: Path | None = None) -> InstallLayout | None:
    exe = Path(executable or sys.executable).resolve()
    candidates = [exe.parent, exe.parent.parent]
    env_root = os.getenv("MCRL_INSTALL_ROOT")
    if env_root:
        candidates.insert(0, Path(env_root).expanduser().resolve())
    for root in candidates:
        metadata_path = root / "install.json"
        if not metadata_path.is_file():
            continue
        try:
            metadata = InstallMetadata.load(metadata_path)
        except UpdateInstallError:
            continue
        return InstallLayout.from_root(Path(metadata.root), data_root=Path(metadata.data_root))
    return None


class UpdateService:
    def __init__(
        self,
        client: GitHubReleaseClient,
        *,
        platform_name: str | None = None,
        installed_build: str | int | None = None,
        layout: InstallLayout | None = None,
        downloader: Callable = download_to,
    ) -> None:
        self.client = client
        self.platform_name = platform_name or platform_module.system()
        self.installed_build = str(installed_build if installed_build is not None else load_build_info().build)
        self.layout = layout if layout is not None else discover_install_layout()
        self.downloader = downloader

    @property
    def can_apply(self) -> bool:
        return self.layout is not None and self.layout.metadata.is_file()

    def check(self, channel: str | BuildChannel) -> UpdateCandidate | None:
        try:
            selected_channel = channel if isinstance(channel, BuildChannel) else BuildChannel(str(channel))
        except ValueError as exc:
            raise UpdateError(f"Unknown update channel: {channel}") from exc
        release = self.client.newest(selected_channel)
        if release is None:
            return None
        if release.verification is VerificationState.FAILED:
            raise UpdateError("Newest release failed verification")
        if not self.client.is_newer(release, self.installed_build):
            return None
        asset = release.asset_for(self.platform_name)
        checksum_asset = release.checksum_asset()
        if asset is None:
            raise UpdateError(f"Release has no unique {self.platform_name} x64 package")
        if checksum_asset is None:
            raise UpdateError("Release has no SHA256SUMS.txt")
        return UpdateCandidate(release=release, asset=asset, checksum_asset=checksum_asset, platform=self.platform_name)

    def _metadata(self) -> InstallMetadata:
        if self.layout is None:
            raise UpdateError("This portable build is not installed with MinecraftRLLab Setup")
        try:
            return InstallMetadata.load(self.layout.metadata)
        except UpdateInstallError as exc:
            raise UpdateError(str(exc)) from exc

    def stage(self, candidate: UpdateCandidate, progress=None) -> StagedUpdate:
        metadata = self._metadata()
        assert self.layout is not None
        build = candidate.release.build_number
        if build is None:
            raise UpdateError("Release build number is missing")
        asset_name = str(candidate.asset.get("name", ""))
        asset_url = str(candidate.asset.get("browser_download_url", ""))
        sums_url = str(candidate.checksum_asset.get("browser_download_url", ""))
        if not asset_name or not asset_url or not sums_url:
            raise UpdateError("Release asset metadata is incomplete")

        stage_root = self.layout.staging / f"build-{build}"
        if stage_root.exists():
            shutil.rmtree(stage_root)
        downloads = stage_root / "downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        archive = downloads / asset_name
        sums = downloads / "SHA256SUMS.txt"
        try:
            self.downloader(sums_url, sums, None)
            self.downloader(asset_url, archive, progress)
            parsed = parse_sha256sums(sums.read_text(encoding="utf-8"))
            expected = parsed.get(asset_name)
            if expected is None:
                raise PackageValidationError(f"SHA256SUMS.txt does not contain {asset_name}")
            verify_file(archive, expected)
            package_root = safe_extract_archive(archive, stage_root / "payload")
            validate_package_root(package_root, candidate.platform)
        except (PackageValidationError, OSError) as exc:
            raise UpdateError(str(exc)) from exc

        executable = self.layout.app / metadata.executable
        helper_name = "MinecraftRLLab-Maintenance.exe" if candidate.platform.lower() == "windows" else "MinecraftRLLab-Maintenance"
        helper = self.layout.updater / helper_name
        plan_path = write_apply_plan(
            stage_root / "apply.json",
            self.layout,
            package_root,
            [str(executable)],
            wait_pid=os.getpid(),
            health_timeout=45.0,
        )
        return StagedUpdate(candidate=candidate, package_root=package_root, plan_path=plan_path, helper_path=helper)

    def launch_apply(self, staged: StagedUpdate) -> subprocess.Popen:
        helper = staged.helper_path
        if not helper.is_file():
            raise UpdateError(f"Update helper is missing: {helper}")
        command = [str(helper), "--apply-plan", str(staged.plan_path)]
        try:
            return subprocess.Popen(command, cwd=helper.parent, start_new_session=True)
        except OSError as exc:
            raise UpdateError(f"Could not launch update helper: {exc}") from exc
