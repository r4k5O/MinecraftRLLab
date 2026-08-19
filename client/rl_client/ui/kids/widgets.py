from __future__ import annotations
from PySide6.QtCore import Signal,Qt
from PySide6.QtWidgets import QFrame,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QProgressBar


class KidsMissionCard(QFrame):
    selected=Signal(str)
    def __init__(self,goal:str,emoji:str,title:str,description:str,parent=None)->None:
        super().__init__(parent); self.goal=goal; self.setObjectName("MissionCard"); self.setProperty("checked",False); self.setCursor(Qt.CursorShape.PointingHandCursor); root=QVBoxLayout(self); root.setContentsMargins(18,18,18,18); row=QHBoxLayout(); icon=QLabel(emoji); icon.setObjectName("KidsEmoji"); row.addWidget(icon); row.addStretch(1); root.addLayout(row); label=QLabel(title); label.setObjectName("KidsCardTitle"); label.setWordWrap(True); root.addWidget(label); desc=QLabel(description); desc.setObjectName("KidsSubtitle"); desc.setWordWrap(True); root.addWidget(desc); root.addStretch(1)
    def mousePressEvent(self,event)->None:
        self.selected.emit(self.goal); super().mousePressEvent(event)
    def set_checked(self,value:bool)->None:
        self.setProperty("checked",bool(value)); self.style().unpolish(self); self.style().polish(self); self.update()


class LessonCard(QFrame):
    opened=Signal(str)
    def __init__(self,tutorial_id:str,emoji:str,title:str,description:str,done:int,total:int,button_text:str,parent=None)->None:
        super().__init__(parent); self.tutorial_id=tutorial_id; self.setObjectName("LessonCard"); root=QVBoxLayout(self); root.setContentsMargins(17,17,17,17); row=QHBoxLayout(); icon=QLabel(emoji); icon.setObjectName("KidsEmoji"); title_label=QLabel(title); title_label.setObjectName("KidsCardTitle"); title_label.setWordWrap(True); row.addWidget(icon); row.addWidget(title_label,1); root.addLayout(row); desc=QLabel(description); desc.setObjectName("KidsSubtitle"); desc.setWordWrap(True); root.addWidget(desc); self.progress=QProgressBar(); self.progress.setRange(0,max(1,total)); self.progress.setValue(done); self.progress.setFormat(f"{done}/{total}"); root.addWidget(self.progress); button=QPushButton(button_text); button.clicked.connect(lambda:self.opened.emit(self.tutorial_id)); root.addWidget(button)


class CoachBanner(QFrame):
    next_requested=Signal()
    def __init__(self,parent=None)->None:
        super().__init__(parent); self.setObjectName("KidsHero"); root=QVBoxLayout(self); root.setContentsMargins(17,14,17,14); self.title=QLabel("✨ Tutorial"); self.title.setObjectName("KidsCardTitle"); self.text=QLabel(); self.text.setWordWrap(True); self.text.setObjectName("KidsSubtitle"); root.addWidget(self.title); root.addWidget(self.text); self.next_button=QPushButton("Next"); self.next_button.setObjectName("KidsPrimary"); self.next_button.clicked.connect(self.next_requested); root.addWidget(self.next_button); self.hide()
    def show_step(self,title:str,text:str,manual:bool=False,next_text:str="Next")->None:
        self.title.setText("✨  "+title); self.text.setText(text); self.next_button.setText(next_text); self.next_button.setVisible(manual); self.show()
    def clear_step(self)->None:self.hide()
