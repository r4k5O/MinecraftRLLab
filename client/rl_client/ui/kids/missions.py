from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLabel
from ...profiles.kids_content import kids_goal_cards
from .widgets import KidsMissionCard


class KidsMissionsScreen(QWidget):
    goal_changed=Signal(str)
    def __init__(self,tr,parent=None)->None:
        super().__init__(parent); self.tr=tr; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(15); title=QLabel("🎯  "+self.tr("kids.pick_mission")); title.setObjectName("KidsTitle"); root.addWidget(title); grid=QGridLayout(); grid.setSpacing(14); self.cards={}; self.specs={item.goal:item for item in kids_goal_cards(tr)}
        for index,item in enumerate(self.specs.values()): card=KidsMissionCard(item.goal,item.emoji,item.title,item.description); card.selected.connect(self.select_goal); self.cards[item.goal]=card; grid.addWidget(card,index//2,index%2)
        root.addLayout(grid,1); self.select_goal("WOODEN_SWORD")
    def select_goal(self,goal:str)->None:
        for key,card in self.cards.items():card.set_checked(key==goal)
        self.goal_changed.emit(goal)
