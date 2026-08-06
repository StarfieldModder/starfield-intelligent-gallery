# ============================================================
#  TEMPLE RESONANCE DASHBOARD
#  Location: C:\IG\temple\temple_resonance_dashboard.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import QTimer

from temple.temple_resonance_engine import TempleResonanceEngine

class TempleResonanceDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.engine = TempleResonanceEngine()

        self.setWindowTitle("Temple Resonance Dashboard")
        self.resize(500, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("Temple Resonance")
        self.title.setStyleSheet("color: white; font-size: 26px;")
        layout.addWidget(self.title)

        self.status_label = QLabel("Status: Low resonance")
        self.status_label.setStyleSheet("color: white; font-size: 18px;")
        layout.addWidget(self.status_label)

        self.bar = QProgressBar()
        self.bar.setRange(0, 10)
        self.bar.setValue(0)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #001428;
                color: white;
                border: 2px solid #00b4ff;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00b4ff;
            }
        """)
        layout.addWidget(self.bar)

        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(0, 20, 40))
        self.setPalette(palette)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    def update_display(self):
        level = self.engine.resonance_level
        self.bar.setValue(level)
        self.status_label.setText(f"Status: {self.engine.status()}")

    def register_event(self, source, description):
        self.engine.register_event(source, description)
