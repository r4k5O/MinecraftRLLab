from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QComboBox,QLabel
from ..widgets.cards import GoalCard
from ..widgets.section import PageHeader
from ..translate import get_translator


class GoalsScreen(QWidget):
    goal_changed=Signal(str)
    SPECS=(("DIAMOND","💎","goal.diamond.title","goal.diamond.description"),("NETHER_PORTAL","🟪","goal.portal.title","goal.portal.description"),("WOODEN_SWORD","🗡️","goal.sword.title","goal.sword.description"),("KILL_ZOMBIE","🧟","goal.zombie.title","goal.zombie.description"))
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14); root.addWidget(PageHeader(self.tr("research.goals.title"),self.tr("research.goals.subtitle")))
        grid=QGridLayout(); grid.setSpacing(10); self.cards={}
        for i,(goal,emoji,title,description) in enumerate(self.SPECS):
            card=GoalCard(goal,emoji,self.tr(title),self.tr(description)); card.selected.connect(self._select); self.cards[goal]=card; grid.addWidget(card,i//2,i%2)
        root.addLayout(grid); root.addWidget(QLabel(self.tr("goals.profile"))); self.profile=QComboBox(); self.profile.addItems(["CURRICULUM","SURVIVAL"]); root.addWidget(self.profile)
        note=QLabel(self.tr("goals.curriculum_note")); note.setWordWrap(True); note.setObjectName("Subtitle"); root.addWidget(note); root.addStretch(1); self._select("WOODEN_SWORD")
    def _select(self,goal:str)->None:
        for key,card in self.cards.items(): card.setChecked(key==goal)
        self.goal_changed.emit(goal)
