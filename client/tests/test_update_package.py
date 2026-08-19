from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

from rl_client.update.package import (
    PackageValidationError,
    parse_sha256sums,
    safe_extract_archive,
    sha256_file,
    validate_package_root,
    verify_file,
)


class UpdatePackageTest(unittest.TestCase):
    def test_parse_sha256sums(self):
        text = "a" * 64 + "  alpha.zip\n" + "b" * 64 + " *beta.tar.gz\n"
        parsed = parse_sha256sums(text)
        self.assertEqual(parsed["alpha.zip"], "a" * 64)
        self.assertEqual(parsed["beta.tar.gz"], "b" * 64)

    def test_verify_file_accepts_match_and_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.bin"
            path.write_bytes(b"minecraft-rl")
            digest = hashlib.sha256(b"minecraft-rl").hexdigest()
            self.assertEqual(sha256_file(path), digest)
            verify_file(path, digest)
            with self.assertRaises(PackageValidationError):
                verify_file(path, "0" * 64)

    def test_safe_zip_extract_returns_single_package_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "package.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("MinecraftRLLab-7-Windows-x64/PACKAGE_INFO.json", "{}")
                zf.writestr("MinecraftRLLab-7-Windows-x64/MinecraftRLLab.exe", "exe")
            extracted = safe_extract_archive(archive, root / "out")
            self.assertEqual(extracted.name, "MinecraftRLLab-7-Windows-x64")
            self.assertTrue((extracted / "MinecraftRLLab.exe").is_file())

    def test_safe_tar_extract_returns_single_package_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "package.tar.gz"
            with tarfile.open(archive, "w:gz") as tf:
                for name, data in (
                    ("MinecraftRLLab-7-Linux-x64/PACKAGE_INFO.json", b"{}"),
                    ("MinecraftRLLab-7-Linux-x64/MinecraftRLLab", b"bin"),
                ):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    tf.addfile(info, io.BytesIO(data))
            extracted = safe_extract_archive(archive, root / "out")
            self.assertEqual(extracted.name, "MinecraftRLLab-7-Linux-x64")

    def test_zip_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "evil.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("../escape.txt", "bad")
            with self.assertRaises(PackageValidationError):
                safe_extract_archive(archive, root / "out")
            self.assertFalse((root / "escape.txt").exists())

    def test_tar_absolute_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "evil.tar.gz"
            with tarfile.open(archive, "w:gz") as tf:
                info = tarfile.TarInfo("/escape.txt")
                data = b"bad"
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
            with self.assertRaises(PackageValidationError):
                safe_extract_archive(archive, root / "out")

    def test_validate_package_root_checks_platform_and_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PACKAGE_INFO.json").write_text(json.dumps({"build": "7", "platform": "Windows"}), encoding="utf-8")
            (root / "MinecraftRLLab.exe").write_bytes(b"exe")
            info = validate_package_root(root, "Windows")
            self.assertEqual(info["build"], "7")
            with self.assertRaises(PackageValidationError):
                validate_package_root(root, "Linux")


if __name__ == "__main__":
    unittest.main()
