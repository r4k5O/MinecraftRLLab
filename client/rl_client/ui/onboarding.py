from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFrame,QLabel,QComboBox,QLineEdit,QPushButton,QRadioButton,QButtonGroup,QGridLayout
from ..i18n import Translator,SUPPORTED_LOCALES
from ..profiles import ExperienceMode,get_profile


class OnboardingWindow(QMainWindow):
    completed=Signal()
    def __init__(self,settings_store,settings)->None:
        super().__init__(); self.settings_store=settings_store; self.settings=settings; self.tr=Translator(settings.language); self.setMinimumSize(900,650); self.resize(1040,720); self._cards={}; self._build(); self._retranslate()
    def _build(self)->None:
        host=QWidget(); self.setCentralWidget(host); root=QVBoxLayout(host); root.setContentsMargins(70,48,70,48); root.setSpacing(18)
        self.title=QLabel(); self.title.setObjectName("OnboardingTitle"); root.addWidget(self.title); self.subtitle=QLabel(); self.subtitle.setObjectName("OnboardingSubtitle"); self.subtitle.setWordWrap(True); root.addWidget(self.subtitle)
        top=QHBoxLayout(); self.language_label=QLabel(); self.language=QComboBox();
        for code,name in SUPPORTED_LOCALES.items(): self.language.addItem(name,code)
        idx=self.language.findData(self.settings.language); self.language.setCurrentIndex(max(0,idx)); top.addWidget(self.language_label); top.addWidget(self.language); top.addStretch(1); root.addLayout(top)
        self.mode_label=QLabel(); self.mode_label.setObjectName("MetricName"); root.addWidget(self.mode_label); grid=QGridLayout(); grid.setSpacing(12); self.group=QButtonGroup(self); self.group.setExclusive(True)
        for index,mode in enumerate(ExperienceMode):
            frame=QFrame(); frame.setObjectName("ChoiceCard"); layout=QVBoxLayout(frame); radio=QRadioButton(); radio.setProperty("mode",mode.value); self.group.addButton(radio); layout.addWidget(radio); desc=QLabel(); desc.setWordWrap(True); desc.setObjectName("Subtitle"); layout.addWidget(desc); self._cards[mode]=(radio,desc); grid.addWidget(frame,index//2,index%2)
        selected=next((m for m in ExperienceMode if m.value==self.settings.experience_mode),ExperienceMode.RESEARCH); self._cards[selected][0].setChecked(True); root.addLayout(grid)
        name_row=QHBoxLayout(); self.name_label=QLabel(); self.name=QLineEdit(self.settings.kid_name); name_row.addWidget(self.name_label); name_row.addWidget(self.name,1); root.addLayout(name_row); root.addStretch(1)
        actions=QHBoxLayout(); actions.addStretch(1); self.finish=QPushButton(); self.finish.setObjectName("Primary"); actions.addWidget(self.finish); root.addLayout(actions)
        self.language.currentIndexChanged.connect(self._change_language); self.finish.clicked.connect(self._finish)
    def _change_language(self)->None:
        self.tr=Translator(self.language.currentData()); self._retranslate()
    def _retranslate(self)->None:
        self.setWindowTitle(self.tr("onboarding.title")); self.title.setText("🧠  "+self.tr("onboarding.title")); self.subtitle.setText(self.tr("onboarding.subtitle")); self.language_label.setText(self.tr("onboarding.language")); self.mode_label.setText(self.tr("onboarding.mode")); self.name_label.setText(self.tr("onboarding.name")); self.finish.setText(self.tr("onboarding.finish"))
        for mode,(radio,desc) in self._cards.items(): profile=get_profile(mode); radio.setText(self.tr(profile.title_key)); desc.setText(self.tr(profile.description_key))
    def _finish(self)->None:
        button=self.group.checkedButton(); mode=button.property("mode") if button else ExperienceMode.RESEARCH.value; self.settings.language=str(self.language.currentData()); self.settings.experience_mode=str(mode); self.settings.kid_name=self.name.text().strip() or "Explorer"; self.settings.onboarding_complete=True; self.settings_store.save(self.settings); self.completed.emit()
