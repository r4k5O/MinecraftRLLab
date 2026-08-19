from __future__ import annotations

from PySide6.QtWidgets import QLabel


class StatusChip(QLabel):
    COLORS = {
        "good": ("#123527", "#6af0ad"),
        "warn": ("#3b3015", "#ffd66b"),
        "bad": ("#3a1e28", "#ff8ea4"),
        "info": ("#152c45", "#7ebcff"),
        "muted": ("#1a222c", "#95a6b8"),
    }

    def __init__(self, text: str = "Offline", state: str = "muted", parent=None) -> None:
        super().__init__(parent)
        self.setContentsMargins(8, 4, 8, 4)
        self.set_state(text, state)

    def set_state(self, text: str, state: str) -> None:
        bg, fg = self.COLORS.get(state, self.COLORS["muted"])
        self.setText(text)
        self.setStyleSheet(f"background:{bg};color:{fg};border-radius:10px;padding:4px 8px;font-weight:600;")
