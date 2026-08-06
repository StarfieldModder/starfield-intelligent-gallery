# ============================================================
#  TEMPLE STARTUP ANIMATION
#  Location: C:\IG\temple\temple_startup_animation.py
# ============================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette, QFont

class TempleStartupAnimation(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temple — Startup Sequence")
        self.resize(900, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        # Title
        self.title = QLabel("THE TEMPLE AWAKENS")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: cyan; font-size: 40px;")
        layout.addWidget(self.title)

        # Subtitle (changes during animation)
        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: white; font-size: 22px;")
        layout.addWidget(self.subtitle)

        # Background
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(0, 10, 25))
        self.setPalette(palette)

        # Animation script
        self.steps = [
            "Initializing Temple architecture…",
            "Activating resonance conduits…",
            "Calibrating glyph rings…",
            "Synchronizing Memory Chamber…",
            "Aligning Timeline fractures…",
            "Summoning Guardian presence…",
            "Temple integrity confirmed.",
            "The Temple is awake."
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
            self.close()  # End animation


# ------------------------------------------------------------
# SAFE STANDALONE RUNNER
# ------------------------------------------------------------
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    anim = TempleStartupAnimation()
    anim.show()
    sys.exit(app.exec())

