from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def health_check() -> int:
    from rl_client.encoder import ObservationEncoder
    from rl_client.update.models import BuildChannel
    payload = {
        "ok": True,
        "app": "MinecraftRLLab",
        "feature_size": ObservationEncoder.FEATURE_SIZE,
        "channels": [c.value for c in BuildChannel],
        "python": sys.version.split()[0],
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


def ui_smoke_check() -> int:
    import tempfile
    from PySide6.QtWidgets import QApplication
    from rl_client.settings import Settings, SettingsStore
    from rl_client.ui.main_window import MainWindow
    from rl_client.ui.kids import KidsMainWindow
    from rl_client.ui.onboarding import OnboardingWindow
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "settings.json"
        store = SettingsStore(path)
        research = Settings(onboarding_complete=True, experience_mode="research", language="en")
        store.save(research)
        windows = [
            MainWindow(store, research),
            KidsMainWindow(store, Settings(onboarding_complete=True, experience_mode="kids", language="de", kid_name="Test")),
            OnboardingWindow(store, Settings(onboarding_complete=False, language="fr")),
        ]
        names = [type(window).__name__ for window in windows]
        for window in windows:
            window.close()
        app.processEvents()
    print(json.dumps({"ok": True, "ui_shells": names}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="MinecraftRLLab")
    parser.add_argument("--health-check", action="store_true")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--ui-smoke", action="store_true")
    args = parser.parse_args()
    if args.health_check:
        return health_check()
    if args.ui_smoke:
        return ui_smoke_check()
    if args.version:
        from rl_client.version import display_version
        print(display_version())
        return 0
    from rl_client.app import launch
    return launch()


if __name__ == "__main__":
    raise SystemExit(main())
