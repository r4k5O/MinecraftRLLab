from __future__ import annotations
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QSpinBox
import pyqtgraph as pg
from ..widgets.cards import MetricCard
from ..widgets.section import PageHeader
from ..translate import get_translator


class DashboardScreen(QWidget):
    def __init__(self, parent=None, tr=None) -> None:
        super().__init__(parent); self.tr=get_translator(tr)
        root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(14)
        root.addWidget(PageHeader(self.tr("research.dashboard.title"), self.tr("research.dashboard.subtitle")))
        metrics=QGridLayout(); metrics.setSpacing(10)
        specs=(("episode","dashboard.episode","0","dashboard.current_run"),("reward","dashboard.reward","0.00","dashboard.episode_total"),("epsilon","dashboard.epsilon","1.000","dashboard.exploration"),("loss","dashboard.loss","—","dashboard.latest_update"),("success","dashboard.success_rate","0%","dashboard.session"),("best","dashboard.best_reward","0.00","dashboard.session"))
        self.cards={key:MetricCard(self.tr(label),value,self.tr(sub)) for key,label,value,sub in specs}
        for index,card in enumerate(self.cards.values()): metrics.addWidget(card,index//3,index%3)
        root.addLayout(metrics)
        chart_card=QFrame(); chart_card.setObjectName("Card"); chart_layout=QVBoxLayout(chart_card); chart_layout.setContentsMargins(14,12,14,14); chart_layout.addWidget(QLabel(self.tr("dashboard.chart")))
        self.plot=pg.PlotWidget(); self.plot.setBackground("#0c131c"); self.plot.showGrid(x=True,y=True,alpha=0.14); self.plot.getAxis("left").setTextPen("#71869c"); self.plot.getAxis("bottom").setTextPen("#71869c"); self.curve=self.plot.plot([],[],pen=pg.mkPen("#4b9cff",width=2)); chart_layout.addWidget(self.plot,1); root.addWidget(chart_card,1)
        controls=QHBoxLayout(); controls.addWidget(QLabel(self.tr("dashboard.episodes"))); self.episodes=QSpinBox(); self.episodes.setRange(1,1000000); self.episodes.setValue(100); controls.addWidget(self.episodes); controls.addWidget(QLabel(self.tr("dashboard.offset"))); self.episode_offset=QSpinBox(); self.episode_offset.setRange(0,100000000); controls.addWidget(self.episode_offset); controls.addStretch(1); root.addLayout(controls)
        actions=QHBoxLayout(); self.start_button=QPushButton(self.tr("dashboard.start")); self.start_button.setObjectName("Primary"); self.stop_button=QPushButton(self.tr("dashboard.stop")); self.stop_button.setObjectName("Danger"); self.stop_button.setEnabled(False); self.last_action=QLabel(self.tr("dashboard.last_action",action="NOOP")); self.last_action.setObjectName("Subtitle"); actions.addWidget(self.start_button); actions.addWidget(self.stop_button); actions.addStretch(1); actions.addWidget(self.last_action); root.addLayout(actions)
        self._rewards=[]

    def push_reward(self,value:float)->None:
        self._rewards.append(float(value)); self.curve.setData(list(range(len(self._rewards))),self._rewards)
