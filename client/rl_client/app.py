from __future__ import annotations
import sys
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from .settings import SettingsStore
from .profiles import select_shell
from .ui.main_window import MainWindow
from .ui.kids import KidsMainWindow
from .ui.onboarding import OnboardingWindow
from .ui.theme import DARK_STYLESHEET


class DesktopRouter(QObject):
    def __init__(self,app:QApplication,store:SettingsStore)->None:
        super().__init__(); self.app=app; self.store=store; self.window=None

    def open_current(self)->None:
        settings=self.store.load(); shell=select_shell(onboarding_complete=settings.onboarding_complete,mode=settings.experience_mode)
        old=self.window
        if shell=="onboarding":
            window=OnboardingWindow(self.store,settings); window.completed.connect(self.open_current)
        elif shell=="kids":
            window=KidsMainWindow(self.store,settings)
        else:
            window=MainWindow(self.store,settings)
        self.window=window; window.show()
        if old is not None and old is not window:old.close()


def launch()->int:
    app=QApplication.instance() or QApplication(sys.argv); app.setApplicationName("MinecraftRLLab"); app.setOrganizationName("r4k5O"); app.setStyleSheet(DARK_STYLESHEET); router=DesktopRouter(app,SettingsStore()); app._minecraft_rl_router=router; router.open_current(); return app.exec()
