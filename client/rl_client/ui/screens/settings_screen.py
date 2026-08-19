from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QGridLayout,QLineEdit,QComboBox,QCheckBox,QPushButton,QLabel
from ..widgets.section import PageHeader
from ..translate import get_translator
from ...i18n import SUPPORTED_LOCALES
from ...profiles import ExperienceMode


class SettingsScreen(QWidget):
    save_requested=Signal(dict)
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("nav.settings"),self.tr("app.restart_required")))
        card=QFrame(); card.setObjectName("Card"); grid=QGridLayout(card); grid.setContentsMargins(18,18,18,18); grid.setSpacing(10)
        self.owner=QLineEdit("r4k5O"); self.repo=QLineEdit("MinecraftRLLab"); self.channel=QComboBox(); self.channel.addItems(["verified","nightly"]); self.auto=QCheckBox(self.tr("settings.auto_updates")); self.auto.setChecked(True)
        self.language=QComboBox(); self.language_codes=list(SUPPORTED_LOCALES); [self.language.addItem(SUPPORTED_LOCALES[c],c) for c in self.language_codes]
        self.mode=QComboBox(); [self.mode.addItem(self.tr(f"mode.{m.value}.title"),m.value) for m in ExperienceMode]
        self.kid_name=QLineEdit("Explorer")
        rows=((self.tr("settings.repository")+" owner",self.owner),(self.tr("settings.repository"),self.repo),(self.tr("settings.update_channel"),self.channel),(self.tr("settings.language"),self.language),(self.tr("settings.experience_mode"),self.mode),(self.tr("settings.kid_name"),self.kid_name))
        for i,(label,widget) in enumerate(rows): grid.addWidget(QLabel(label),i,0); grid.addWidget(widget,i,1)
        grid.addWidget(self.auto,len(rows),0,1,2); self.save=QPushButton(self.tr("common.save")); self.save.setObjectName("Primary"); grid.addWidget(self.save,len(rows)+1,1); root.addWidget(card); root.addStretch(1); self.save.clicked.connect(self._emit)
    def set_language(self,code:str)->None:
        idx=self.language.findData(code)
        if idx>=0:self.language.setCurrentIndex(idx)
    def set_mode(self,mode:str)->None:
        idx=self.mode.findData(mode)
        if idx>=0:self.mode.setCurrentIndex(idx)
    def _emit(self)->None:
        self.save_requested.emit({"github_owner":self.owner.text().strip(),"github_repo":self.repo.text().strip(),"update_channel":self.channel.currentText(),"auto_check_updates":self.auto.isChecked(),"language":self.language.currentData(),"experience_mode":self.mode.currentData(),"kid_name":self.kid_name.text().strip() or "Explorer"})
