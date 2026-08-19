from __future__ import annotations
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QFrame,QLabel,QProgressBar


class KidsProgressScreen(QWidget):
    ACHIEVEMENT_EMOJI={"first_tutorial":"🌱","first_episode":"🚀","first_success":"🎉","diamond_mind":"💎","portal_master":"🟪","zombie_hunter":"🧟","model_keeper":"💾","scientist":"🧪"}
    def __init__(self,tr,progress_store,parent=None)->None:
        super().__init__(parent); self.tr=tr; self.store=progress_store; root=QVBoxLayout(self); root.setContentsMargins(28,24,28,28); root.setSpacing(14); title=QLabel("🏆  "+self.tr("kids.progress")); title.setObjectName("KidsTitle"); root.addWidget(title); stats=QGridLayout(); self.stars_card=self._stat("🌟 "+self.tr("kids.stars"),"0"); self.lessons_card=self._stat("📚 "+self.tr("learning.completed"),"0"); stats.addWidget(self.stars_card[0],0,0); stats.addWidget(self.lessons_card[0],0,1); root.addLayout(stats); self.badges=QFrame(); self.badges.setObjectName("KidsCard"); self.badge_layout=QVBoxLayout(self.badges); root.addWidget(self.badges); root.addStretch(1); self.refresh()
    def _stat(self,label:str,value:str):
        card=QFrame(); card.setObjectName("KidsCard"); layout=QVBoxLayout(card); layout.addWidget(QLabel(label)); number=QLabel(value); number.setObjectName("KidsBigNumber"); layout.addWidget(number); return card,number
    def refresh(self)->None:
        p=self.store.load(); self.stars_card[1].setText(str(p.stars)); self.lessons_card[1].setText(str(len(p.completed_tutorials)))
        while self.badge_layout.count():
            item=self.badge_layout.takeAt(0); widget=item.widget();
            if widget:widget.deleteLater()
        heading=QLabel("🏅  "+self.tr("learning.achievements")); heading.setObjectName("KidsCardTitle"); self.badge_layout.addWidget(heading)
        if not p.unlocked_achievements:
            empty=QLabel(self.tr("kids.tip")); empty.setObjectName("KidsSubtitle"); empty.setWordWrap(True); self.badge_layout.addWidget(empty)
        for aid in p.unlocked_achievements:
            label=QLabel(f"{self.ACHIEVEMENT_EMOJI.get(aid,'⭐')}  {self.tr('achievement.'+aid,default=aid)}"); label.setObjectName("KidsSubtitle"); self.badge_layout.addWidget(label)
