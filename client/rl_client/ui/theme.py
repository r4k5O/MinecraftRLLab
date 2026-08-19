from __future__ import annotations

DARK_STYLESHEET = r"""
QWidget { background: #0b0f14; color: #dce7f3; font-family: "Segoe UI", "Inter", sans-serif; font-size: 13px; }
QMainWindow { background: #080b10; }
QFrame#Sidebar { background: #0d131b; border-right: 1px solid #1a2634; }
QFrame#Card { background: #111923; border: 1px solid #1c2b3a; border-radius: 14px; }
QFrame#MetricCard { background: #101923; border: 1px solid #203244; border-radius: 14px; }
QLabel#AppTitle { font-size: 20px; font-weight: 700; color: #f5fbff; }
QLabel#PageTitle { font-size: 26px; font-weight: 700; color: #ffffff; }
QLabel#Subtitle { color: #7f92a8; font-size: 12px; }
QLabel#MetricValue { font-size: 25px; font-weight: 700; color: #f7fbff; }
QLabel#MetricName { color: #7c90a5; font-size: 11px; text-transform: uppercase; }
QLabel#Success { color: #63e6a6; font-weight: 600; }
QLabel#Warning { color: #ffcf70; font-weight: 600; }
QLabel#Danger { color: #ff7a90; font-weight: 600; }
QPushButton { background: #162230; border: 1px solid #263b50; border-radius: 9px; padding: 8px 12px; color: #dce7f3; }
QPushButton:hover { background: #1b2b3c; border-color: #3c5c79; }
QPushButton:pressed { background: #0d1721; padding-top: 9px; padding-bottom: 7px; }
QPushButton#Primary { background: #3e8df7; border-color: #5fa2ff; color: white; font-weight: 650; }
QPushButton#Primary:hover { background: #529cff; }
QPushButton#Danger { background: #42202a; border-color: #6b2e3d; color: #ff9aae; }
QPushButton#Nav { background: transparent; border: 0; text-align: left; padding: 10px 13px; color: #8da0b5; }
QPushButton#Nav:hover { background: #131e2a; color: #e6f0fa; }
QPushButton#Nav:checked { background: #17283a; color: #70aefc; border-left: 3px solid #4b9cff; }
QLineEdit, QSpinBox, QComboBox { background: #0d141d; border: 1px solid #253648; border-radius: 8px; padding: 8px 9px; selection-background-color: #397ed8; }
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border-color: #4a91ed; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView { background: #101821; border: 1px solid #26394c; selection-background-color: #23476c; }
QTextEdit, QPlainTextEdit { background: #091018; border: 1px solid #1c2d3d; border-radius: 10px; font-family: "Cascadia Mono", "Consolas", monospace; }
QTableWidget { background: #0d141d; alternate-background-color: #101925; border: 1px solid #1c2d3d; border-radius: 10px; gridline-color: #192736; }
QHeaderView::section { background: #121d29; color: #8397ac; border: 0; border-bottom: 1px solid #253648; padding: 8px; font-weight: 600; }
QProgressBar { background: #0b1118; border: 1px solid #223448; border-radius: 6px; text-align: center; height: 12px; }
QProgressBar::chunk { background: #4b9cff; border-radius: 5px; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 3px; }
QScrollBar::handle:vertical { background: #25384c; min-height: 25px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip { background: #152130; color: #e8f2fc; border: 1px solid #34506c; padding: 5px; }
"""

DARK_STYLESHEET += r"""
QFrame#ChoiceCard { background: #111923; border: 2px solid #22364a; border-radius: 16px; }
QFrame#ChoiceCard:hover { border-color: #4b79a6; background: #142131; }
QLabel#OnboardingTitle { font-size: 34px; font-weight: 800; color: #ffffff; }
QLabel#OnboardingSubtitle { font-size: 16px; color: #93a8bd; }
QRadioButton { spacing: 9px; font-size: 18px; font-weight: 700; }
QRadioButton::indicator { width: 18px; height: 18px; }
"""
