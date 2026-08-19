KIDS_STYLESHEET = r"""
QWidget { background: #101827; color: #f7fbff; font-family: "Segoe UI", "Inter", sans-serif; font-size: 15px; }
QMainWindow { background: #0d1523; }
QFrame#KidsSidebar { background: #18243a; border-right: 2px solid #263a5d; }
QFrame#KidsCard { background: #1b2941; border: 2px solid #2c4268; border-radius: 22px; }
QFrame#KidsHero { background: #20365a; border: 2px solid #3b64a0; border-radius: 26px; }
QFrame#MissionCard { background: #1d2d48; border: 2px solid #375783; border-radius: 22px; }
QFrame#MissionCard[checked="true"] { background: #253f68; border: 3px solid #6db2ff; }
QFrame#LessonCard { background: #1c2b45; border: 2px solid #344f78; border-radius: 20px; }
QLabel#KidsTitle { font-size: 32px; font-weight: 800; color: #ffffff; }
QLabel#KidsSubtitle { font-size: 17px; color: #b9cbe5; }
QLabel#KidsBigNumber { font-size: 38px; font-weight: 800; color: #ffd96d; }
QLabel#KidsEmoji { font-size: 42px; }
QLabel#KidsCardTitle { font-size: 21px; font-weight: 750; color: #ffffff; }
QLabel#KidsTiny { font-size: 12px; color: #9cb1cf; }
QPushButton { background: #263a5b; border: 2px solid #3c5b88; border-radius: 14px; padding: 11px 16px; color: #eef6ff; font-weight: 650; }
QPushButton:hover { background: #304b76; border-color: #5d86bf; }
QPushButton:pressed { background: #1e304d; padding-top: 13px; padding-bottom: 9px; }
QPushButton#KidsPrimary { background: #4b94ff; border: 2px solid #77b0ff; border-radius: 17px; font-size: 17px; padding: 14px 20px; color: white; font-weight: 800; }
QPushButton#KidsPrimary:hover { background: #63a3ff; }
QPushButton#KidsStop { background: #713449; border-color: #a6516e; color: #ffd8e4; border-radius: 17px; font-size: 17px; padding: 14px 20px; }
QPushButton#KidsNav { background: transparent; border: 0; text-align: left; padding: 13px 15px; font-size: 16px; color: #b6c9e4; }
QPushButton#KidsNav:hover { background: #223554; color: white; }
QPushButton#KidsNav:checked { background: #2b456e; color: #ffffff; border-left: 5px solid #ffd85f; }
QLineEdit, QSpinBox, QComboBox { background: #152239; border: 2px solid #324d75; border-radius: 13px; padding: 10px; color: white; }
QProgressBar { background: #132036; border: 1px solid #324d75; border-radius: 8px; text-align: center; min-height: 18px; }
QProgressBar::chunk { background: #5aa6ff; border-radius: 7px; }
QScrollArea { border: 0; }
QToolTip { background: #243a5e; color: white; border: 1px solid #5d86bf; padding: 7px; }
"""
