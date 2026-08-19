#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform as platform_module
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "client"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(CLIENT) not in sys.path:
    sys.path.insert(0, str(CLIENT))

from rl_client.update.github import GitHubReleaseClient
from rl_client.update.install import InstallLayout, InstallMetadata, default_user_data_root
from rl_client.update.models import BuildChannel, VerificationState
from rl_client.update.package import (
    PackageValidationError,
    download_to,
    parse_sha256sums,
    safe_extract_archive,
    validate_package_root,
    verify_file,
)
from rl_client.update.service import UpdateCandidate
from installer.platform_integration import default_install_root, install_platform_integration


class BootstrapError(RuntimeError):
    pass


def select_candidate(client: GitHubReleaseClient, channel: BuildChannel, platform_name: str) -> UpdateCandidate:
    release = client.newest(channel)
    if release is None:
        raise BootstrapError(f"No {channel.value} release is available")
    if release.verification is VerificationState.FAILED:
        raise BootstrapError("Newest matching release failed verification")
    asset = release.asset_for(platform_name)
    sums = release.checksum_asset()
    if asset is None or sums is None:
        raise BootstrapError(f"Release is missing the {platform_name} package or SHA256SUMS.txt")
    return UpdateCandidate(release=release, asset=asset, checksum_asset=sums, platform=platform_name)


def _maintenance_name(platform_name: str) -> str:
    return "MinecraftRLLab-Maintenance.exe" if platform_name.lower() == "windows" else "MinecraftRLLab-Maintenance"


def _app_name(platform_name: str) -> str:
    return "MinecraftRLLab.exe" if platform_name.lower() == "windows" else "MinecraftRLLab"


def install_candidate(
    candidate: UpdateCandidate,
    layout: InstallLayout,
    *,
    helper_source: Path,
    downloader=download_to,
    install_integration: bool = True,
) -> InstallMetadata:
    build = candidate.release.build_number
    if build is None:
        raise BootstrapError("Release build number is missing")
    asset_name = str(candidate.asset.get("name", ""))
    asset_url = str(candidate.asset.get("browser_download_url", ""))
    sums_url = str(candidate.checksum_asset.get("browser_download_url", ""))
    if not asset_name or not asset_url or not sums_url:
        raise BootstrapError("Release asset metadata is incomplete")

    stage = layout.root / ".setup-staging"
    if stage.exists():
        shutil.rmtree(stage)
    downloads = stage / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / asset_name
    sums = downloads / "SHA256SUMS.txt"
    try:
        downloader(sums_url, sums, None)
        downloader(asset_url, archive, None)
        expected = parse_sha256sums(sums.read_text(encoding="utf-8")).get(asset_name)
        if expected is None:
            raise PackageValidationError(f"SHA256SUMS.txt does not contain {asset_name}")
        verify_file(archive, expected)
        package_root = safe_extract_archive(archive, stage / "payload")
        validate_package_root(package_root, candidate.platform)
    except (OSError, PackageValidationError) as exc:
        raise BootstrapError(str(exc)) from exc

    if layout.app.exists():
        shutil.rmtree(layout.app)
    layout.app.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_root, layout.app)
    layout.updater.mkdir(parents=True, exist_ok=True)
    helper = layout.updater / _maintenance_name(candidate.platform)
    shutil.copy2(helper_source, helper)
    try:
        helper.chmod(0o755)
        (layout.app / _app_name(candidate.platform)).chmod(0o755)
    except OSError:
        pass

    metadata = InstallMetadata(
        root=str(layout.root),
        data_root=str(layout.data_root),
        platform=candidate.platform,
        build=str(build),
        executable=_app_name(candidate.platform),
    )
    metadata.save(layout.metadata)
    if install_integration:
        install_platform_integration(layout, metadata, platform_name=candidate.platform)
    shutil.rmtree(stage, ignore_errors=True)
    return metadata


def _delegate_maintenance_if_requested() -> int | None:
    maintenance_flags = {"--apply-plan", "--uninstall", "--uninstall-worker"}
    if not any(flag in sys.argv[1:] for flag in maintenance_flags):
        return None
    from tools.maintenance_helper import main as maintenance_main
    return maintenance_main()


def main() -> int:
    delegated = _delegate_maintenance_if_requested()
    if delegated is not None:
        return delegated

    parser = argparse.ArgumentParser(prog="MinecraftRLLab-Setup")
    parser.add_argument("--channel", choices=[c.value for c in BuildChannel], default=BuildChannel.VERIFIED.value)
    parser.add_argument("--install-root")
    parser.add_argument("--no-launch", action="store_true")
    args = parser.parse_args()

    platform_name = platform_module.system()
    if platform_name not in {"Windows", "Linux"}:
        print(f"Unsupported platform: {platform_name}", file=sys.stderr)
        return 2
    root = Path(args.install_root).expanduser() if args.install_root else default_install_root(platform_name)
    layout = InstallLayout.from_root(root, data_root=default_user_data_root())
    helper_source = Path(sys.argv[0]).resolve()
    try:
        client = GitHubReleaseClient("r4k5O", "MinecraftRLLab")
        candidate = select_candidate(client, BuildChannel(args.channel), platform_name)
        print(f"Installing {candidate.release.name} ({candidate.release.tag})")
        metadata = install_candidate(candidate, layout, helper_source=helper_source)
    except (BootstrapError, OSError) as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        return 2

    print(f"Installed MinecraftRLLab build {metadata.build} to {layout.root}")
    if not args.no_launch:
        try:
            subprocess.Popen([str(layout.app / metadata.executable)], cwd=layout.app, start_new_session=True)
        except OSError as exc:
            print(f"Installed successfully, but launch failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
