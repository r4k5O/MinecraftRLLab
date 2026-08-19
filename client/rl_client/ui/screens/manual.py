from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QHBoxLayout,QComboBox,QPushButton,QLabel
from ..widgets.section import PageHeader
from ..translate import get_translator


class ManualScreen(QWidget):
    step_requested=Signal(str)
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("manual.title"),self.tr("manual.subtitle"))); card=QFrame(); card.setObjectName("Card"); layout=QVBoxLayout(card); layout.setContentsMargins(18,18,18,18); layout.addWidget(QLabel(self.tr("manual.action"))); row=QHBoxLayout(); self.action=QComboBox(); self.step=QPushButton(self.tr("manual.execute")); self.step.setObjectName("Primary"); row.addWidget(self.action,1); row.addWidget(self.step); layout.addLayout(row); self.result=QLabel(self.tr("manual.connect_hint")); self.result.setObjectName("Subtitle"); self.result.setWordWrap(True); layout.addWidget(self.result); root.addWidget(card); root.addStretch(1); self.step.clicked.connect(lambda:self.step_requested.emit(self.action.currentText()))
    def set_actions(self,actions:list[str])->None:
        self.action.clear(); self.action.addItems(actions); self.result.setText(self.tr("manual.actions_count",count=len(actions)))
