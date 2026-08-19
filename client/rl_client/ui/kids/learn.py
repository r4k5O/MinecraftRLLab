from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLabel,QScrollArea,QFrame
from ...learning import default_tutorials,TutorialEngine
from .widgets import LessonCard


class KidsLearnScreen(QWidget):
    tutorial_selected=Signal(str)
    def __init__(self,tr,engine:TutorialEngine,parent=None)->None:
        super().__init__(parent); self.tr=tr; self.engine=engine; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(14); title=QLabel("📚  "+self.tr("learning.title")); title.setObjectName("KidsTitle"); root.addWidget(title); sub=QLabel(self.tr("learning.subtitle")); sub.setObjectName("KidsSubtitle"); root.addWidget(sub); self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.Shape.NoFrame); self.host=QWidget(); self.grid=QGridLayout(self.host); self.grid.setSpacing(13); self.cards={}; self._populate(); self.scroll.setWidget(self.host); root.addWidget(self.scroll,1)
    def _populate(self)->None:
        for index,tutorial in enumerate(default_tutorials()):
            done,total=self.engine.completion(tutorial.tutorial_id); card=LessonCard(tutorial.tutorial_id,tutorial.emoji,self.tr(tutorial.title_key),self.tr(tutorial.description_key),done,total,self.tr("common.continue")); card.opened.connect(self.tutorial_selected); self.cards[tutorial.tutorial_id]=card; self.grid.addWidget(card,index//2,index%2)
    def refresh(self)->None:
        self.engine.progress=self.engine.store.load()
        for tutorial in default_tutorials():
            card=self.cards[tutorial.tutorial_id]; done,total=self.engine.completion(tutorial.tutorial_id); card.progress.setMaximum(max(1,total)); card.progress.setValue(done); card.progress.setFormat(f"{done}/{total}")
