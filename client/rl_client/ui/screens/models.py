from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QHBoxLayout,QPushButton,QLabel,QFileDialog
from ..widgets.section import PageHeader
from ..translate import get_translator


class ModelsScreen(QWidget):
    save_requested=Signal(str); load_requested=Signal(str)
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("models.title"),self.tr("models.subtitle"))); card=QFrame(); card.setObjectName("Card"); layout=QVBoxLayout(card); layout.setContentsMargins(18,18,18,18); self.info=QLabel(self.tr("models.none")); self.info.setObjectName("Subtitle"); layout.addWidget(self.info); row=QHBoxLayout(); self.save=QPushButton(self.tr("models.save")); self.load=QPushButton(self.tr("models.load")); self.save.setObjectName("Primary"); row.addWidget(self.save); row.addWidget(self.load); row.addStretch(1); layout.addLayout(row); root.addWidget(card); root.addStretch(1); self.save.clicked.connect(self._save); self.load.clicked.connect(self._load)
    def _save(self)->None:
        path,_=QFileDialog.getSaveFileName(self,self.tr("models.save"),"model.pt","PyTorch checkpoint (*.pt)");
        if path:self.save_requested.emit(path)
    def _load(self)->None:
        path,_=QFileDialog.getOpenFileName(self,self.tr("models.load"),"","PyTorch checkpoint (*.pt)");
        if path:self.load_requested.emit(path)
