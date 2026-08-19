from __future__ import annotations

import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.package_release import main as package_main


class PackageReleaseTest(unittest.TestCase):
    def _run_package(self, platform: str, root: Path) -> Path:
        client = root / "client"
        client.mkdir()
        exe = client / ("MinecraftRLLab.exe" if platform == "Windows" else "MinecraftRLLab")
        exe.write_bytes(b"native")
        plugin = root / "MinecraftRLLab-Plugin.jar"
        plugin.write_bytes(b"plugin")
        out = root / "packages"
        argv = [
            "package_release.py",
            "--platform", platform,
            "--client-dist", str(client),
            "--plugin", str(plugin),
            "--build", "77",
            "--output", str(out),
        ]
        with patch.object(sys, "argv", argv):
            self.assertEqual(package_main(), 0)
        return out

    def test_windows_package_contains_self_update_contract(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._run_package("Windows", Path(td))
            archive = out / "MinecraftRLLab-77-Windows-x64.zip"
            with zipfile.ZipFile(archive) as zf:
                metadata_name = next(name for name in zf.namelist() if name.endswith("PACKAGE_INFO.json"))
                info = json.loads(zf.read(metadata_name))
            self.assertEqual(info["build"], "77")
            self.assertEqual(info["platform"], "Windows")
            self.assertEqual(info["package_format"], 2)
            self.assertTrue(info["self_update_payload"])

    def test_linux_package_contains_self_update_contract(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._run_package("Linux", Path(td))
            archive = out / "MinecraftRLLab-77-Linux-x64.tar.gz"
            with tarfile.open(archive) as tf:
                member = next(m for m in tf.getmembers() if m.name.endswith("PACKAGE_INFO.json"))
                extracted = tf.extractfile(member)
                assert extracted is not None
                info = json.load(extracted)
            self.assertEqual(info["platform"], "Linux")
            self.assertEqual(info["package_format"], 2)


if __name__ == "__main__":
    unittest.main()
