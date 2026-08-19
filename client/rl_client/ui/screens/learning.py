from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QFrame,QLabel,QPushButton,QProgressBar,QScrollArea,QHBoxLayout
from ..widgets.section import PageHeader
from ..translate import get_translator
from ...learning import default_tutorials, TutorialEngine, ProgressStore
from ...learning.glossary import glossary_entries


class LearningScreen(QWidget):
    tutorial_requested=Signal(str)
    demo_requested=Signal(str)
    tutorial_next_requested=Signal()
    def __init__(self,parent=None,tr=None,progress_store:ProgressStore|None=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); self.engine=TutorialEngine(default_tutorials(),progress_store or ProgressStore())
        root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("research.learning.title"),self.tr("research.learning.subtitle")))
        self.coach=QFrame(); self.coach.setObjectName("Card"); coach_layout=QVBoxLayout(self.coach); coach_layout.setContentsMargins(16,14,16,14); self.coach_title=QLabel(); self.coach_title.setObjectName("MetricValue"); self.coach_body=QLabel(); self.coach_body.setObjectName("Subtitle"); self.coach_body.setWordWrap(True); self.coach_progress=QProgressBar(); self.coach_next=QPushButton(self.tr("common.next")); self.coach_next.setObjectName("Primary"); self.coach_next.clicked.connect(self.tutorial_next_requested); coach_layout.addWidget(self.coach_title); coach_layout.addWidget(self.coach_body); coach_layout.addWidget(self.coach_progress); coach_layout.addWidget(self.coach_next); self.coach.hide(); root.addWidget(self.coach)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); host=QWidget(); layout=QVBoxLayout(host); layout.setContentsMargins(0,0,8,0); layout.setSpacing(12)
        grid=QGridLayout(); grid.setSpacing(10); self.tutorial_cards={}
        for index,tutorial in enumerate(default_tutorials()):
            card=QFrame(); card.setObjectName("Card"); cl=QVBoxLayout(card); cl.setContentsMargins(16,16,16,16); title=QLabel(f"{tutorial.emoji}  {self.tr(tutorial.title_key)}"); title.setObjectName("MetricValue"); cl.addWidget(title); desc=QLabel(self.tr(tutorial.description_key)); desc.setObjectName("Subtitle"); desc.setWordWrap(True); cl.addWidget(desc); done,total=self.engine.completion(tutorial.tutorial_id); bar=QProgressBar(); bar.setRange(0,total); bar.setValue(done); bar.setFormat(self.tr("learning.steps",done=done,total=total)); cl.addWidget(bar); row=QHBoxLayout(); open_btn=QPushButton(self.tr("common.continue")); open_btn.setObjectName("Primary"); open_btn.clicked.connect(lambda _=False,tid=tutorial.tutorial_id:self.tutorial_requested.emit(tid)); row.addWidget(open_btn); demo=QPushButton(self.tr("learning.try_demo")); demo.clicked.connect(lambda _=False,tid=tutorial.tutorial_id:self.demo_requested.emit(tid)); row.addWidget(demo); row.addStretch(1); cl.addLayout(row); grid.addWidget(card,index//2,index%2); self.tutorial_cards[tutorial.tutorial_id]=(bar,tutorial)
        layout.addLayout(grid)
        glossary_card=QFrame(); glossary_card.setObjectName("Card"); gl=QVBoxLayout(glossary_card); gl.setContentsMargins(16,16,16,16); heading=QLabel("📖  "+self.tr("learning.glossary")); heading.setObjectName("MetricValue"); gl.addWidget(heading)
        for entry in glossary_entries(self.tr):
            term=QLabel(f"<b>{entry.term}</b> — {entry.explanation}"); term.setWordWrap(True); gl.addWidget(term)
        layout.addWidget(glossary_card); layout.addStretch(1); scroll.setWidget(host); root.addWidget(scroll,1)
    def show_step(self,title:str,body:str,done:int,total:int,manual:bool=True)->None:
        self.coach_title.setText("✨  "+title); self.coach_body.setText(body); self.coach_progress.setRange(0,max(1,total)); self.coach_progress.setValue(done); self.coach_progress.setFormat(self.tr("learning.steps",done=done,total=total)); self.coach_next.setVisible(manual); self.coach.show()
    def clear_step(self)->None:self.coach.hide()
    def refresh(self)->None:
        self.engine.progress=self.engine.store.load()
        for tid,(bar,tutorial) in self.tutorial_cards.items():
            done,total=self.engine.completion(tid); bar.setMaximum(total); bar.setValue(done); bar.setFormat(self.tr("learning.steps",done=done,total=total))
