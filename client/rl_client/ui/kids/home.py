from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QFrame,QLabel,QPushButton,QGridLayout
from .widgets import CoachBanner


class KidsHomeScreen(QWidget):
    start_requested=Signal(); stop_requested=Signal(); demo_requested=Signal()
    def __init__(self,tr,name:str,parent=None)->None:
        super().__init__(parent); self.tr=tr; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(16); self.hello=QLabel(self.tr("kids.hello",name=name)); self.hello.setObjectName("KidsTitle"); root.addWidget(self.hello); subtitle=QLabel(self.tr("kids.ready")); subtitle.setObjectName("KidsSubtitle"); root.addWidget(subtitle); self.coach=CoachBanner(); root.addWidget(self.coach)
        hero=QFrame(); hero.setObjectName("KidsHero"); hl=QVBoxLayout(hero); hl.setContentsMargins(22,20,22,20); self.connection=QLabel("🔴  "+self.tr("kids.not_connected")); self.connection.setObjectName("KidsCardTitle"); hl.addWidget(self.connection); self.mission=QLabel("🗡️  "+self.tr("kids.goal.sword.title")); self.mission.setObjectName("KidsSubtitle"); hl.addWidget(self.mission); actions=QHBoxLayout(); self.start=QPushButton(self.tr("kids.big_start")); self.start.setObjectName("KidsPrimary"); self.stop=QPushButton(self.tr("kids.big_stop")); self.stop.setObjectName("KidsStop"); self.stop.setEnabled(False); actions.addWidget(self.start); actions.addWidget(self.stop); actions.addStretch(1); hl.addLayout(actions); root.addWidget(hero)
        stats=QGridLayout(); reward=QFrame(); reward.setObjectName("KidsCard"); rl=QVBoxLayout(reward); rl.addWidget(QLabel("⭐ "+self.tr("kids.reward"))); self.reward=QLabel("0.00"); self.reward.setObjectName("KidsBigNumber"); rl.addWidget(self.reward); stars=QFrame(); stars.setObjectName("KidsCard"); sl=QVBoxLayout(stars); sl.addWidget(QLabel("🌟 "+self.tr("kids.stars"))); self.stars=QLabel("0"); self.stars.setObjectName("KidsBigNumber"); sl.addWidget(self.stars); stats.addWidget(reward,0,0); stats.addWidget(stars,0,1); root.addLayout(stats)
        demo=QFrame(); demo.setObjectName("KidsCard"); dl=QHBoxLayout(demo); info=QLabel("🎮  "+self.tr("kids.tip")); info.setWordWrap(True); dl.addWidget(info,1); self.demo=QPushButton(self.tr("kids.demo_start")); dl.addWidget(self.demo); root.addWidget(demo); root.addStretch(1); self.start.clicked.connect(self.start_requested); self.stop.clicked.connect(self.stop_requested); self.demo.clicked.connect(self.demo_requested)
    def set_connected(self,value:bool)->None:self.connection.setText(("🟢  "+self.tr("kids.connected")) if value else ("🔴  "+self.tr("kids.not_connected")))
    def set_goal(self,emoji:str,title:str)->None:self.mission.setText(f"{emoji}  {title}")
    def set_training(self,value:bool)->None:self.start.setEnabled(not value); self.stop.setEnabled(value)
