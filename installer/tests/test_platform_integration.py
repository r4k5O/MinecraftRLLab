from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from installer.platform_integration import default_install_root, linux_desktop_entries, windows_registry_values
from rl_client.update.install import InstallLayout, InstallMetadata


class PlatformIntegrationTest(unittest.TestCase):
    def test_default_install_roots_are_per_user(self):
        win = default_install_root("Windows", env={"LOCALAPPDATA": "C:/Users/Test/AppData/Local"}, home=Path("C:/Users/Test"))
        self.assertTrue(str(win).replace("\\", "/").endswith("AppData/Local/Programs/MinecraftRLLab"))
        linux = default_install_root("Linux", env={}, home=Path("/home/tester"))
        self.assertEqual(linux, Path("/home/tester/.local/share/MinecraftRLLab"))

    def test_windows_registry_values_include_real_uninstall_command(self):
        layout = InstallLayout.from_root(Path("C:/Users/Test/AppData/Local/Programs/MinecraftRLLab"), data_root=Path("C:/Users/Test/.minecraftrllab"))
        metadata = InstallMetadata(root=str(layout.root), data_root=str(layout.data_root), platform="Windows", build="12", executable="MinecraftRLLab.exe")
        values = windows_registry_values(layout, metadata)
        self.assertEqual(values["DisplayName"], "MinecraftRLLab")
        self.assertIn("--uninstall", values["UninstallString"])
        self.assertIn("MinecraftRLLab-Maintenance.exe", values["UninstallString"])
        self.assertNotIn("QuietUninstallString", values)

    def test_linux_desktop_entries_include_app_and_uninstaller(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            layout = InstallLayout.from_root(home / ".local/share/MinecraftRLLab", data_root=home / ".minecraftrllab")
            metadata = InstallMetadata(root=str(layout.root), data_root=str(layout.data_root), platform="Linux", build="12", executable="MinecraftRLLab")
            entries = linux_desktop_entries(layout, metadata, home=home)
            app = entries[home / ".local/share/applications/minecraftrllab.desktop"]
            uninstall = entries[home / ".local/share/applications/minecraftrllab-uninstall.desktop"]
            self.assertIn(f'Exec="{layout.app / "MinecraftRLLab"}"', app)
            self.assertIn("--uninstall", uninstall)


if __name__ == "__main__":
    unittest.main()
