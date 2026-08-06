# ============================================================
#  TIMELINE FRACTURE MAP
#  Location: C:\IG\timeline\timeline_fracture_map.py
# ============================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QColor, QPalette

class TimelineFractureMap(QWidget):
    def __init__(self, anomaly):
        super().__init__()

        self.setWindowTitle("Timeline Fracture Map")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label = QLabel(f"Timeline anomaly detected: {anomaly}")
        label.setStyleSheet("color: white; font-size: 24px;")
        self.layout.addWidget(label)

        self._apply_color(anomaly)

    def _apply_color(self, anomaly):
        palette = QPalette()

        if "fracture" in anomaly.lower():
            palette.setColor(QPalette.Window, QColor(255, 50, 50, 200))
        elif "loop" in anomaly.lower():
            palette.setColor(QPalette.Window, QColor(255, 200, 50, 200))
        elif "desync" in anomaly.lower():
            palette.setColor(QPalette.Window, QColor(50, 200, 255, 200))
        else:
            palette.setColor(QPalette.Window, QColor(200, 50, 255, 200))

        self.setPalette(palette)
