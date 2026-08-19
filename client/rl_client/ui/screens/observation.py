from __future__ import annotations
import json
from PySide6.QtWidgets import QWidget,QVBoxLayout,QPlainTextEdit,QFrame,QGridLayout,QLabel
from ..widgets.section import PageHeader
from ..translate import get_translator


class ObservationScreen(QWidget):
    def __init__(self,parent=None,tr=None)->None:
        super().__init__(parent); self.tr=get_translator(tr); root=QVBoxLayout(self); root.setContentsMargins(24,20,24,24); root.setSpacing(12); root.addWidget(PageHeader(self.tr("observation.title"),self.tr("observation.subtitle"))); self.summary=QFrame(); self.summary.setObjectName("Card"); grid=QGridLayout(self.summary); grid.setContentsMargins(15,12,15,12)
        specs=(("Position","observation.position"),("Health","observation.health"),("Food","observation.food"),("Dimension","observation.dimension"),("Nearby zombies","observation.zombies"),("Target","observation.target")); self.labels={key:QLabel("—") for key,_ in specs}
        for i,(key,label_key) in enumerate(specs): grid.addWidget(QLabel(self.tr(label_key)),i//3,(i%3)*2); grid.addWidget(self.labels[key],i//3,(i%3)*2+1)
        root.addWidget(self.summary); self.raw=QPlainTextEdit(); self.raw.setReadOnly(True); root.addWidget(self.raw,1)
    def set_observation(self,observation:dict)->None:
        self.raw.setPlainText(json.dumps(observation,indent=2,sort_keys=True)); self.labels["Position"].setText(f"{observation.get('x','—')}, {observation.get('y','—')}, {observation.get('z','—')}"); self.labels["Health"].setText(str(observation.get("health","—"))); self.labels["Food"].setText(str(observation.get("food","—"))); self.labels["Dimension"].setText(str(observation.get("dimension","—"))); self.labels["Nearby zombies"].setText(str(observation.get("nearby_zombies","—"))); self.labels["Target"].setText(str(observation.get("target_entity_category",observation.get("target_block_category","—"))))
