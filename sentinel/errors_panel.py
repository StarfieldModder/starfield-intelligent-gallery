# ============================================================
#  SENTINEL ERRORS PANEL
#  Location: C:\IG\sentinel\errors_panel.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtGui import QPalette, QColor

LOG_PATH = r"C:\IG\logs\sentinel.log"

class ErrorsPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sentinel — Errors Panel")
        self.resize(800, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Sentinel Error & Alert Log")
        title.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(title)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(0, 20, 40))
        self.setPalette(palette)

        self._load_log()

    def _load_log(self):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                self.text.setPlainText(f.read())
        except FileNotFoundError:
            self.text.setPlainText("No sentinel.log found.\nRun the Sentinel test harness first.")
