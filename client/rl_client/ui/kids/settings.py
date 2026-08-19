from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QGridLayout,QLabel,QComboBox,QLineEdit,QPushButton
from ...i18n import SUPPORTED_LOCALES
from ...profiles import ExperienceMode


class KidsSettingsScreen(QWidget):
    save_requested=Signal(dict)
    def __init__(self,tr,settings,parent=None)->None:
        super().__init__(parent); self.tr=tr; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(15); title=QLabel("⚙️  "+self.tr("nav.settings")); title.setObjectName("KidsTitle"); root.addWidget(title); note=QLabel(self.tr("app.restart_required")); note.setObjectName("KidsSubtitle"); note.setWordWrap(True); root.addWidget(note)
        card=QFrame(); card.setObjectName("KidsCard"); grid=QGridLayout(card); grid.setContentsMargins(20,20,20,20); grid.setSpacing(13); self.language=QComboBox();
        for code,name in SUPPORTED_LOCALES.items():self.language.addItem(name,code)
        self.mode=QComboBox();
        for mode in ExperienceMode:self.mode.addItem(self.tr(f"mode.{mode.value}.title"),mode.value)
        self.name=QLineEdit(settings.kid_name); rows=((self.tr("settings.language"),self.language),(self.tr("settings.experience_mode"),self.mode),(self.tr("settings.kid_name"),self.name))
        for row,(label,widget) in enumerate(rows):grid.addWidget(QLabel(label),row,0); grid.addWidget(widget,row,1)
        self.save=QPushButton(self.tr("common.save")); self.save.setObjectName("KidsPrimary"); grid.addWidget(self.save,len(rows),1); root.addWidget(card); root.addStretch(1); self.set_values(settings.language,settings.experience_mode,settings.kid_name); self.save.clicked.connect(self._emit)
    def set_values(self,language:str,mode:str,name:str)->None:
        idx=self.language.findData(language); self.language.setCurrentIndex(max(0,idx)); idx=self.mode.findData(mode); self.mode.setCurrentIndex(max(0,idx)); self.name.setText(name)
    def _emit(self)->None:self.save_requested.emit({"language":self.language.currentData(),"experience_mode":self.mode.currentData(),"kid_name":self.name.text().strip() or "Explorer"})
