# ============================================================
#  MEMORY CHAMBER VISUALIZATION
#  Location: C:\IG\memory\memory_chamber_visualization.py
# ============================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QColor, QPalette

class MemoryVisualization(QWidget):
    def __init__(self, anomaly_type):
        super().__init__()

        self.setWindowTitle("Memory Chamber — Anomaly Visualization")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        label = QLabel(f"Detected anomaly: {anomaly_type}")
        label.setStyleSheet("color: white; font-size: 24px;")
        self.layout.addWidget(label)

        self._apply_color(anomaly_type)

    def _apply_color(self, anomaly):
        palette = QPalette()

        if "rift" in anomaly.lower():
            palette.setColor(QPalette.Window, QColor(255, 80, 80, 180))
        elif "echo" in anomaly.lower():
            palette.setColor(QPalette.Window, QColor(80, 80, 255, 180))
        else:
            palette.setColor(QPalette.Window, QColor(80, 255, 80, 180))

        self.setPalette(palette)
