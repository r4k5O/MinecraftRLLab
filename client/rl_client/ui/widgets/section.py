from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("Subtitle")
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
