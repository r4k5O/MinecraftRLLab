from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from rl_client.update.github import GitHubReleaseClient
from rl_client.update.models import BuildChannel, ReleaseBuild, VerificationState
from rl_client.server.detection import detect_server
from rl_client.server.installer import install_plugin


class ReleaseModelTest(unittest.TestCase):
    def test_pending_prerelease_is_nightly(self):
        release=ReleaseBuild("nightly-42","Build 42","", "2026-08-19", True, "verification:pending", ())
        self.assertEqual(release.channel, BuildChannel.NIGHTLY)
        self.assertEqual(release.verification, VerificationState.PENDING)

    def test_failed_marker_overrides_pending(self):
        release=ReleaseBuild("nightly-43","Build 43","", "2026-08-19", True, "verification:failed", ())
        self.assertEqual(release.verification, VerificationState.FAILED)

    def test_non_prerelease_is_verified(self):
        release=ReleaseBuild("build-41","Build 41","", "2026-08-19", False, "verification:passed", ())
        self.assertEqual(release.channel, BuildChannel.VERIFIED)
        self.assertEqual(release.verification, VerificationState.VERIFIED)

    def test_build_number_from_nightly_tag(self):
        release=ReleaseBuild("nightly-57-deadbeef","Build 57","", "2026-08-19", True, "verification:pending", ())
        self.assertEqual(release.build_number, 57)

    def test_platform_asset_selection_is_deterministic(self):
        assets=(
            {"name":"MinecraftRLLab-57-Windows-x64.zip","browser_download_url":"https://example/windows"},
            {"name":"MinecraftRLLab-57-Linux-x64.tar.gz","browser_download_url":"https://example/linux"},
            {"name":"SHA256SUMS.txt","browser_download_url":"https://example/sums"},
        )
        release=ReleaseBuild("nightly-57-deadbeef","Build 57","", "2026-08-19", True, "verification:pending", assets)
        self.assertEqual(release.asset_for("Windows")["browser_download_url"], "https://example/windows")
        self.assertEqual(release.asset_for("Linux")["browser_download_url"], "https://example/linux")
        self.assertEqual(release.checksum_asset()["name"], "SHA256SUMS.txt")

    def test_release_comparison_uses_numeric_build(self):
        client=GitHubReleaseClient("r4k5O","MinecraftRLLab")
        release=ReleaseBuild("nightly-57-deadbeef","Build 57","", "2026-08-19", True, "verification:pending", ())
        self.assertTrue(client.is_newer(release, "56"))
        self.assertFalse(client.is_newer(release, "57"))
        self.assertFalse(client.is_newer(release, "local"))

    def test_newest_ignores_non_app_setup_release(self):
        setup=ReleaseBuild("setup","MinecraftRLLab Setup","", "2026-08-19", False, "", ())
        app=ReleaseBuild("nightly-56-deadbeef","Build 56","", "2026-08-18", False, "verification:passed", ())
        class Client(GitHubReleaseClient):
            def list_releases(self,limit=20):return [setup,app]
        self.assertEqual(Client("r4k5O","MinecraftRLLab").newest(BuildChannel.VERIFIED),app)


class ServerInstallTest(unittest.TestCase):
    def test_detect_and_install_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"plugins").mkdir(); (root/"paper-26.2-111.jar").write_bytes(b"paper")
            source=root/"source-MinecraftRLLab.jar"; source.write_bytes(b"plugin")
            detected=detect_server(root); self.assertTrue(detected.looks_valid)
            result=install_plugin(root,source)
            self.assertEqual(result.destination.read_bytes(),b"plugin")


if __name__ == "__main__":
    unittest.main()
