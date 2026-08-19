from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from installer.bootstrap import install_candidate, select_candidate
from rl_client.update.install import InstallLayout, InstallMetadata
from rl_client.update.models import BuildChannel, ReleaseBuild


class FakeClient:
    def __init__(self, release): self.release=release
    def newest(self, channel): return self.release


def make_release(build=12):
    return ReleaseBuild(
        f"nightly-{build}-abc",f"Build {build}","","2026-08-19",True,"verification:pending",
        (
            {"name":f"MinecraftRLLab-{build}-Windows-x64.zip","browser_download_url":"https://example/archive"},
            {"name":"SHA256SUMS.txt","browser_download_url":"https://example/sums"},
        ),
    )


class BootstrapTest(unittest.TestCase):
    def test_select_candidate_uses_requested_channel_and_platform(self):
        candidate = select_candidate(FakeClient(make_release()), BuildChannel.NIGHTLY, "Windows")
        self.assertEqual(candidate.release.build_number, 12)
        self.assertTrue(candidate.asset["name"].endswith("Windows-x64.zip"))

    def test_install_candidate_creates_managed_layout_and_copies_self_as_maintenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            layout=InstallLayout.from_root(root/"install", data_root=root/"data")
            source_archive=root/"source.zip"
            with zipfile.ZipFile(source_archive,"w") as zf:
                zf.writestr("MinecraftRLLab-12-Windows-x64/PACKAGE_INFO.json",json.dumps({"build":"12","platform":"Windows"}))
                zf.writestr("MinecraftRLLab-12-Windows-x64/MinecraftRLLab.exe",b"new")
            digest=hashlib.sha256(source_archive.read_bytes()).hexdigest()
            sums=root/"sums.txt"; sums.write_text(f"{digest}  MinecraftRLLab-12-Windows-x64.zip\n",encoding="utf-8")
            helper_source=root/"Setup.exe"; helper_source.write_bytes(b"bootstrap")
            def fake_download(url,destination,progress=None):
                shutil.copy2(source_archive if url.endswith("archive") else sums,destination)
                return destination
            candidate=select_candidate(FakeClient(make_release()),BuildChannel.NIGHTLY,"Windows")
            metadata=install_candidate(candidate,layout,helper_source=helper_source,downloader=fake_download,install_integration=False)
            self.assertTrue((layout.app/"MinecraftRLLab.exe").is_file())
            self.assertEqual((layout.updater/"MinecraftRLLab-Maintenance.exe").read_bytes(),b"bootstrap")
            loaded=InstallMetadata.load(layout.metadata)
            self.assertEqual(loaded.build,"12")
            self.assertEqual(metadata,loaded)


if __name__ == "__main__":
    unittest.main()
