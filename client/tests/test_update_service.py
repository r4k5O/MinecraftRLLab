from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from rl_client.update.install import InstallLayout, InstallMetadata
from rl_client.update.models import BuildChannel, ReleaseBuild
from rl_client.update.service import UpdateError, UpdateService


class FakeClient:
    def __init__(self, release: ReleaseBuild | None):
        self.release = release

    def newest(self, channel: BuildChannel):
        return self.release

    @staticmethod
    def is_newer(release: ReleaseBuild, installed_build: str | int) -> bool:
        try:
            return int(release.build_number or -1) > int(installed_build)
        except (TypeError, ValueError):
            return False


def make_release(build: int, archive_url: str = "https://example/archive", sums_url: str = "https://example/sums") -> ReleaseBuild:
    return ReleaseBuild(
        f"nightly-{build}-abc12345",
        f"Build {build}",
        "",
        "2026-08-19",
        True,
        "verification:pending",
        (
            {"name": f"MinecraftRLLab-{build}-Windows-x64.zip", "browser_download_url": archive_url, "size": 123},
            {"name": "SHA256SUMS.txt", "browser_download_url": sums_url},
        ),
    )


class UpdateServiceTest(unittest.TestCase):
    def test_check_only_offers_newer_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            layout = InstallLayout.from_root(Path(tmp) / "install", data_root=Path(tmp) / "data")
            service = UpdateService(FakeClient(make_release(12)), platform_name="Windows", installed_build="11", layout=layout)
            candidate = service.check("nightly")
            self.assertIsNotNone(candidate)
            self.assertEqual(candidate.release.build_number, 12)
            service_same = UpdateService(FakeClient(make_release(11)), platform_name="Windows", installed_build="11", layout=layout)
            self.assertIsNone(service_same.check("nightly"))

    def test_check_requires_platform_and_checksum_assets(self):
        release = ReleaseBuild("nightly-12-x", "Build 12", "", "", True, "verification:pending", ())
        service = UpdateService(FakeClient(release), platform_name="Windows", installed_build="11", layout=None)
        with self.assertRaises(UpdateError):
            service.check("nightly")

    def test_stage_downloads_verifies_extracts_and_writes_apply_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = InstallLayout.from_root(root / "install", data_root=root / "data")
            layout.app.mkdir(parents=True)
            (layout.app / "MinecraftRLLab.exe").write_bytes(b"old")
            layout.updater.mkdir(parents=True)
            (layout.updater / "MinecraftRLLab-Maintenance.exe").write_bytes(b"helper")
            metadata = InstallMetadata(root=str(layout.root), data_root=str(layout.data_root), platform="Windows", build="11", executable="MinecraftRLLab.exe")
            metadata.save(layout.metadata)

            source_archive = root / "source.zip"
            with zipfile.ZipFile(source_archive, "w") as zf:
                zf.writestr("MinecraftRLLab-12-Windows-x64/PACKAGE_INFO.json", json.dumps({"build": "12", "platform": "Windows"}))
                zf.writestr("MinecraftRLLab-12-Windows-x64/MinecraftRLLab.exe", b"new")
            digest = hashlib.sha256(source_archive.read_bytes()).hexdigest()
            source_sums = root / "sums.txt"
            source_sums.write_text(f"{digest}  MinecraftRLLab-12-Windows-x64.zip\n", encoding="utf-8")

            def fake_download(url: str, destination: Path, progress=None):
                source = source_archive if url.endswith("archive") else source_sums
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                if progress:
                    progress(destination.stat().st_size, destination.stat().st_size)
                return destination

            service = UpdateService(FakeClient(make_release(12)), platform_name="Windows", installed_build="11", layout=layout, downloader=fake_download)
            candidate = service.check("nightly")
            staged = service.stage(candidate)
            self.assertTrue((staged.package_root / "MinecraftRLLab.exe").is_file())
            self.assertTrue(staged.plan_path.is_file())
            plan = json.loads(staged.plan_path.read_text(encoding="utf-8"))
            self.assertEqual(Path(plan["staged_app"]), staged.package_root)
            self.assertEqual(plan["launch_command"][0], str(layout.app / "MinecraftRLLab.exe"))


if __name__ == "__main__":
    unittest.main()
