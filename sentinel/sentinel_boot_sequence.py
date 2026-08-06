# ============================================================
#  SENTINEL BOOT SEQUENCE
#  Location: C:\IG\sentinel\sentinel_boot_sequence.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette

class SentinelBootSequence(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sentinel — Boot Sequence")
        self.resize(900, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        # Title
        self.title = QLabel("SENTINEL ONLINE")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: #ff4444; font-size: 40px;")
        layout.addWidget(self.title)

        # Subtitle (changes during boot)
        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: white; font-size: 22px;")
        layout.addWidget(self.subtitle)

        # Background
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(20, 0, 0))
        self.setPalette(palette)

        # Boot script
        self.steps = [
            "Routing alert channels…",
            "Calibrating severity engine…",
            "Synchronizing pulse engine…",
            "Linking Guardian bridge…",
            "Activating anomaly detectors…",
            "Establishing Temple uplink…",
            "Sentinel integrity confirmed.",
            "Sentinel is now watching."
        ]

        self.current_step = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(1200)

    def next_step(self):
        if self.current_step < len(self.steps):
            self.subtitle.setText(self.steps[self.current_step])
            self.current_step += 1
        else:
            self.timer.stop()
            self.close()  # End boot sequence
