from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from rl_client.update.install import (
    InstallLayout,
    InstallMetadata,
    UpdateInstallError,
    activate_staged_update,
    allowed_uninstall_paths,
)


class InstallLayoutTest(unittest.TestCase):
    def test_layout_is_confined_to_install_root_and_data_root_is_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "install"
            data = Path(tmp) / "user-data"
            layout = InstallLayout.from_root(root, data_root=data)
            self.assertEqual(layout.app, root.resolve() / "app")
            self.assertEqual(layout.staging, root.resolve() / "update-staging")
            self.assertEqual(layout.data_root, data.resolve())

    def test_metadata_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "install"
            data = Path(tmp) / "user-data"
            layout = InstallLayout.from_root(root, data_root=data)
            metadata = InstallMetadata(root=str(layout.root), data_root=str(layout.data_root), platform="Windows", build="7", executable="MinecraftRLLab.exe")
            metadata.save(layout.metadata)
            self.assertEqual(InstallMetadata.load(layout.metadata), metadata)

    def test_successful_activation_swaps_payload_and_cleans_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "install"
            layout = InstallLayout.from_root(root, data_root=Path(tmp) / "data")
            layout.app.mkdir(parents=True)
            (layout.app / "old.txt").write_text("old", encoding="utf-8")
            staged = layout.staging / "next"
            staged.mkdir(parents=True)
            (staged / "new.txt").write_text("new", encoding="utf-8")
            activate_staged_update(layout, staged, [sys.executable, "-c", "raise SystemExit(0)"], health_timeout=5)
            self.assertTrue((layout.app / "new.txt").is_file())
            self.assertFalse(layout.rollback.exists())

    def test_failed_health_check_restores_old_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "install"
            layout = InstallLayout.from_root(root, data_root=Path(tmp) / "data")
            layout.app.mkdir(parents=True)
            (layout.app / "old.txt").write_text("old", encoding="utf-8")
            staged = layout.staging / "next"
            staged.mkdir(parents=True)
            (staged / "new.txt").write_text("new", encoding="utf-8")
            with self.assertRaises(UpdateInstallError):
                activate_staged_update(layout, staged, [sys.executable, "-c", "raise SystemExit(3)"], health_timeout=5)
            self.assertTrue((layout.app / "old.txt").is_file())
            self.assertFalse((layout.app / "new.txt").exists())

    def test_uninstall_preserves_user_data_by_default(self):
        with tempfile.TemporaryDirectory(dir=Path.home()) as tmp:
            layout = InstallLayout.from_root(Path(tmp) / "install", data_root=Path(tmp) / "data")
            default_paths = allowed_uninstall_paths(layout, remove_user_data=False)
            all_paths = allowed_uninstall_paths(layout, remove_user_data=True)
            self.assertNotIn(layout.data_root, default_paths)
            self.assertIn(layout.data_root, all_paths)
            for path in default_paths:
                path.resolve().relative_to(layout.root.resolve())


if __name__ == "__main__":
    unittest.main()
