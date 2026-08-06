# ============================================================
#  THE CROSSING — CINEMATIC ENTRY PANEL
#  Location: C:\IG\crossing\crossing_panel.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette

class CrossingPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("The Crossing")
        self.resize(900, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.title = QLabel("THE CROSSING")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: cyan; font-size: 42px;")
        layout.addWidget(self.title)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: white; font-size: 22px;")
        layout.addWidget(self.subtitle)

        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)

        self.steps = [
            "Artifact initializing…",
            "Breath cycle engaged…",
            "Temple rings rotating…",
            "Starfield ignition…",
            "Starfield expansion…",
            "Glyph entrance forming…",
            "Crossing alignment complete.",
            "Welcome to the Intelligent Gallery."
        ]

        self.current_step = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(1400)

    def next_step(self):
        if self.current_step < len(self.steps):
            self.subtitle.setText(self.steps[self.current_step])
            self.current_step += 1
        else:
            self.timer.stop()
            self.close()
