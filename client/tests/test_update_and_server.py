from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

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
