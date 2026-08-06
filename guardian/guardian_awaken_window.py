# ============================================================
#  GUARDIAN AI — AWAKENING WINDOW
#  Location: C:\IG\guardian\guardian_awaken_window.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtGui import QPalette, QColor
from guardian.guardian_awaken import GuardianAwakening

class GuardianAwakenWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GuardianAI — Awakening")
        self.resize(700, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("GuardianAI Awakening")
        title.setStyleSheet("color: cyan; font-size: 28px;")
        layout.addWidget(title)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet("color: white; font-size: 18px;")
        text.setPlainText(GuardianAwakening().monologue())
        layout.addWidget(text)

        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(0, 20, 40))
        self.setPalette(palette)
