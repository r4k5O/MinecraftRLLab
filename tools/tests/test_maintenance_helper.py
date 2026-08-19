from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.maintenance_helper import perform_uninstall
from rl_client.update.install import InstallLayout, InstallMetadata


class MaintenanceHelperTest(unittest.TestCase):
    def test_perform_uninstall_preserves_data_by_default(self):
        with tempfile.TemporaryDirectory(dir=Path.home()) as tmp:
            root = Path(tmp) / "install"
            data = Path(tmp) / "data"
            layout = InstallLayout.from_root(root, data_root=data)
            layout.app.mkdir(parents=True)
            layout.updater.mkdir(parents=True)
            data.mkdir(parents=True)
            (layout.app / "app.bin").write_bytes(b"app")
            (data / "settings.json").write_text("{}", encoding="utf-8")
            metadata = InstallMetadata(root=str(root.resolve()), data_root=str(data.resolve()), platform="Linux", build="7", executable="MinecraftRLLab")
            metadata.save(layout.metadata)
            perform_uninstall(layout.metadata, remove_user_data=False)
            self.assertFalse(layout.app.exists())
            self.assertTrue(data.exists())
            self.assertTrue((data / "settings.json").exists())

    def test_perform_uninstall_can_remove_managed_data_explicitly(self):
        with tempfile.TemporaryDirectory(dir=Path.home()) as tmp:
            root = Path(tmp) / "install"
            data = Path(tmp) / "data"
            layout = InstallLayout.from_root(root, data_root=data)
            layout.app.mkdir(parents=True)
            data.mkdir(parents=True)
            (data / "settings.json").write_text("{}", encoding="utf-8")
            metadata = InstallMetadata(root=str(root.resolve()), data_root=str(data.resolve()), platform="Linux", build="7", executable="MinecraftRLLab")
            metadata.save(layout.metadata)
            perform_uninstall(layout.metadata, remove_user_data=True)
            self.assertFalse(data.exists())


if __name__ == "__main__":
    unittest.main()
