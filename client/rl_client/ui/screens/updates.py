from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QLabel,QPushButton,QHBoxLayout,QComboBox
from ..widgets.section import PageHeader
from ..widgets.status import StatusChip
from ..translate import get_translator


class UpdatesScreen(QWidget):
    check_requested=Signal(str)
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("updates.title"),self.tr("updates.subtitle"))); toolbar=QHBoxLayout(); toolbar.addWidget(QLabel(self.tr("updates.channel"))); self.channel=QComboBox(); self.channel.addItems(["verified","nightly"]); toolbar.addWidget(self.channel); toolbar.addStretch(1); self.check=QPushButton(self.tr("updates.check")); self.check.setObjectName("Primary"); toolbar.addWidget(self.check); root.addLayout(toolbar); card=QFrame(); card.setObjectName("Card"); layout=QVBoxLayout(card); layout.setContentsMargins(18,18,18,18); self.status=StatusChip(self.tr("updates.not_checked"),"muted"); self.name=QLabel("—"); self.name.setObjectName("MetricValue"); self.details=QLabel(self.tr("updates.placeholder")); self.details.setObjectName("Subtitle"); self.details.setWordWrap(True); layout.addWidget(self.status); layout.addWidget(self.name); layout.addWidget(self.details); root.addWidget(card); root.addStretch(1); self.check.clicked.connect(lambda:self.check_requested.emit(self.channel.currentText()))
    def set_release(self,name:str,tag:str,verification:str,published:str)->None:
        state={"verified":"good","pending":"warn","failed":"bad"}.get(verification,"muted"); self.status.set_state(verification.upper(),state); self.name.setText(name); self.details.setText(f"{tag} • {published}")
