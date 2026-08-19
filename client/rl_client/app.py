from __future__ import annotations

import sys
import threading

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from .i18n import Translator
from .profiles import select_shell
from .settings import SettingsStore
from .ui.kids import KidsMainWindow
from .ui.main_window import MainWindow
from .ui.onboarding import OnboardingWindow
from .ui.theme import DARK_STYLESHEET
from .update.github import GitHubReleaseClient
from .update.service import UpdateError, UpdateService


class DesktopRouter(QObject):
    auto_candidate = Signal(object)
    auto_staged = Signal(object)
    auto_error = Signal(str)

    def __init__(self, app: QApplication, store: SettingsStore) -> None:
        super().__init__()
        self.app = app
        self.store = store
        self.window = None
        self.auto_candidate.connect(self._offer_auto_update)
        self.auto_staged.connect(self._apply_auto_update)
        self.auto_error.connect(self._show_auto_update_error)

    def open_current(self) -> None:
        settings = self.store.load()
        shell = select_shell(
            onboarding_complete=settings.onboarding_complete,
            mode=settings.experience_mode,
        )
        old = self.window
        if shell == "onboarding":
            window = OnboardingWindow(self.store, settings)
            window.completed.connect(self.open_current)
        elif shell == "kids":
            window = KidsMainWindow(self.store, settings)
        else:
            window = MainWindow(self.store, settings)
        self.window = window
        window.show()
        if old is not None and old is not window:
            old.close()
        if shell != "onboarding" and settings.auto_check_updates:
            QTimer.singleShot(1400, lambda s=settings: self._auto_check_updates(s))

    def _auto_check_updates(self, settings) -> None:
        def work() -> None:
            try:
                client = GitHubReleaseClient(settings.github_owner, settings.github_repo)
                service = UpdateService(client)
                candidate = service.check(settings.update_channel)
                if candidate is not None and service.can_apply:
                    self.auto_candidate.emit((service, candidate, settings.language))
            except UpdateError:
                # Automatic checks are intentionally quiet. The manual Updates
                # page still reports network/release errors to the user.
                return

        threading.Thread(target=work, daemon=True, name="auto-update-check").start()

    @Slot(object)
    def _offer_auto_update(self, payload) -> None:
        service, candidate, language = payload
        if self.window is None:
            return
        tr = Translator(language)
        answer = QMessageBox.question(
            self.window,
            tr("updates.title"),
            f"{candidate.release.name}\n\n{tr('updates.subtitle')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        def work() -> None:
            try:
                staged = service.stage(candidate)
                self.auto_staged.emit((service, staged))
            except UpdateError as exc:
                self.auto_error.emit(str(exc))

        threading.Thread(target=work, daemon=True, name="auto-update-stage").start()

    @Slot(object)
    def _apply_auto_update(self, payload) -> None:
        service, staged = payload
        try:
            service.launch_apply(staged)
        except UpdateError as exc:
            self.auto_error.emit(str(exc))
            return
        self.app.quit()

    @Slot(str)
    def _show_auto_update_error(self, message: str) -> None:
        if self.window is None:
            return
        settings = self.store.load()
        tr = Translator(settings.language)
        QMessageBox.warning(
            self.window,
            tr("updates.title"),
            message,
        )


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("MinecraftRLLab")
    app.setOrganizationName("r4k5O")
    app.setStyleSheet(DARK_STYLESHEET)
    router = DesktopRouter(app, SettingsStore())
    app._minecraft_rl_router = router
    router.open_current()
    return app.exec()
