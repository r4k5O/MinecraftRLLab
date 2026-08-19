from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QPushButton


class MetricCard(QFrame):
    def __init__(self, name: str, value: str = "—", subtitle: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 13, 15, 13)
        layout.setSpacing(3)
        name_label = QLabel(name.upper())
        name_label.setObjectName("MetricName")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("Subtitle")
        layout.addWidget(name_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

    def set_value(self, value: object, subtitle: str | None = None) -> None:
        self.value_label.setText(str(value))
        if subtitle is not None:
            self.subtitle_label.setText(subtitle)


class GoalCard(QPushButton):
    selected = Signal(str)

    def __init__(self, goal: str, emoji: str, title: str, description: str, parent=None) -> None:
        super().__init__(parent)
        self.goal = goal
        self.setCheckable(True)
        self.setMinimumHeight(88)
        self.setText(f"{emoji}  {title}\n{description}")
        self.setStyleSheet("QPushButton { text-align:left; padding:14px; font-size:13px; } QPushButton:checked { border:2px solid #4b9cff; background:#14263a; }")
        self.clicked.connect(lambda: self.selected.emit(self.goal))
