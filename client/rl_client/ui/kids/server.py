from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QFrame,QGridLayout,QLineEdit,QSpinBox,QLabel,QPushButton,QHBoxLayout,QFileDialog


class KidsServerScreen(QWidget):
    connect_requested=Signal(); install_requested=Signal()
    def __init__(self,tr,parent=None)->None:
        super().__init__(parent); self.tr=tr; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(15); title=QLabel("⛏️  "+self.tr("kids.server")); title.setObjectName("KidsTitle"); root.addWidget(title)
        card=QFrame(); card.setObjectName("KidsCard"); grid=QGridLayout(card); grid.setContentsMargins(18,18,18,18); self.host=QLineEdit("127.0.0.1"); self.port=QSpinBox(); self.port.setRange(1,65535); self.port.setValue(8765); self.player=QLineEdit(); self.token=QLineEdit(); self.token.setEchoMode(QLineEdit.EchoMode.Password)
        for row,(key,widget) in enumerate((("server.host",self.host),("server.port",self.port),("server.player",self.player),("server.token",self.token))): grid.addWidget(QLabel(self.tr(key)),row,0); grid.addWidget(widget,row,1)
        self.connect=QPushButton("🔗  "+self.tr("server.connect")); self.connect.setObjectName("KidsPrimary"); grid.addWidget(self.connect,4,1); self.status=QLabel("🔴  "+self.tr("kids.not_connected")); grid.addWidget(self.status,4,0); root.addWidget(card)
        plugin=QFrame(); plugin.setObjectName("KidsCard"); pl=QVBoxLayout(plugin); pl.addWidget(QLabel("🧩  "+self.tr("server.install_plugin"))); row=QHBoxLayout(); self.server_path=QLineEdit(); self.server_path.setPlaceholderText(self.tr("server.choose_folder")); self.browse=QPushButton("📁"); self.install=QPushButton(self.tr("server.install_plugin")); row.addWidget(self.server_path,1); row.addWidget(self.browse); row.addWidget(self.install); pl.addLayout(row); self.install_status=QLabel(self.tr("connection.install_hint")); self.install_status.setWordWrap(True); self.install_status.setObjectName("KidsSubtitle"); pl.addWidget(self.install_status); root.addWidget(plugin); root.addStretch(1); self.connect.clicked.connect(self.connect_requested); self.install.clicked.connect(self.install_requested); self.browse.clicked.connect(self._browse)
    def _browse(self)->None:
        path=QFileDialog.getExistingDirectory(self,self.tr("server.choose_folder"));
        if path:self.server_path.setText(path)
    def set_connected(self,value:bool)->None:self.status.setText(("🟢  "+self.tr("kids.connected")) if value else ("🔴  "+self.tr("kids.not_connected")))
