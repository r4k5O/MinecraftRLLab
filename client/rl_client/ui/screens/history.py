from __future__ import annotations
from PySide6.QtWidgets import QWidget,QVBoxLayout,QTableWidget,QTableWidgetItem,QHeaderView
from ..widgets.section import PageHeader
from ..translate import get_translator
from ...core.metrics import EpisodeMetric


class HistoryScreen(QWidget):
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(12); root.addWidget(PageHeader(self.tr("history.title"),self.tr("history.subtitle"))); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels([self.tr(k) for k in ("history.episode","history.steps","history.reward","history.success","history.reason")]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.table.setAlternatingRowColors(True); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); root.addWidget(self.table,1)
    def add_metric(self,metric:EpisodeMetric)->None:
        row=self.table.rowCount(); self.table.insertRow(row); values=(metric.episode,metric.steps,f"{metric.reward:.3f}",self.tr("history.yes") if metric.success else self.tr("history.no"),metric.reason)
        for col,value in enumerate(values): self.table.setItem(row,col,QTableWidgetItem(str(value)))
        self.table.scrollToBottom()
