from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AppUpdateWiringTest(unittest.TestCase):
    def test_auto_update_check_is_centralized_for_all_shells(self):
        app = (ROOT / "rl_client" / "app.py").read_text(encoding="utf-8")
        main = (ROOT / "rl_client" / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("def _auto_check_updates", app)
        self.assertIn("UpdateService", app)
        self.assertIn("GitHubReleaseClient", app)
        self.assertIn("auto_check_updates", app)
        self.assertIn("QTimer.singleShot", app)
        self.assertNotIn("QTimer.singleShot(1200", main)

    def test_auto_update_offer_can_stage_and_apply(self):
        app = (ROOT / "rl_client" / "app.py").read_text(encoding="utf-8")
        self.assertIn("service.stage", app)
        self.assertIn("service.launch_apply", app)
        self.assertIn("QMessageBox.question", app)
        self.assertIn("self.app.quit()", app)


if __name__ == "__main__":
    unittest.main()
