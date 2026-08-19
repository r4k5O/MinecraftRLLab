from __future__ import annotations
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLineEdit,QSpinBox,QPushButton,QFrame,QLabel,QFileDialog,QHBoxLayout
from ..widgets.section import PageHeader
from ..widgets.status import StatusChip
from ..translate import get_translator


class ConnectionScreen(QWidget):
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("server.title"),self.tr("connection.subtitle")))
        card=QFrame(); card.setObjectName("Card"); form=QGridLayout(card); form.setContentsMargins(18,18,18,18); form.setSpacing(10)
        self.host=QLineEdit("127.0.0.1"); self.port=QSpinBox(); self.port.setRange(1,65535); self.port.setValue(8765); self.token=QLineEdit(); self.token.setEchoMode(QLineEdit.EchoMode.Password); self.player=QLineEdit(); self.status=StatusChip(self.tr("connection.disconnected"),"muted"); self.connect_button=QPushButton(self.tr("server.connect")); self.connect_button.setObjectName("Primary")
        for i,(label,widget) in enumerate(((self.tr("server.host"),self.host),(self.tr("server.port"),self.port),(self.tr("server.token"),self.token),(self.tr("server.player"),self.player))): form.addWidget(QLabel(label),i,0); form.addWidget(widget,i,1)
        form.addWidget(self.connect_button,4,1); form.addWidget(self.status,4,0); root.addWidget(card)
        install=QFrame(); install.setObjectName("Card"); il=QVBoxLayout(install); il.setContentsMargins(18,18,18,18); il.addWidget(QLabel(self.tr("connection.server_setup"))); self.server_path=QLineEdit(); self.server_path.setPlaceholderText(self.tr("server.choose_folder")); row=QHBoxLayout(); row.addWidget(self.server_path,1); self.browse_button=QPushButton(self.tr("connection.browse")); self.install_button=QPushButton(self.tr("server.install_plugin")); row.addWidget(self.browse_button); row.addWidget(self.install_button); il.addLayout(row); self.install_status=QLabel(self.tr("connection.install_hint")); self.install_status.setObjectName("Subtitle"); il.addWidget(self.install_status); root.addWidget(install); root.addStretch(1); self.browse_button.clicked.connect(self._browse)
    def _browse(self)->None:
        path=QFileDialog.getExistingDirectory(self,self.tr("server.choose_folder"));
        if path:self.server_path.setText(path)
