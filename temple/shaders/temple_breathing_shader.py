# ============================================================
#  TEMPLE BREATHING SHADER
#  Location: C:\IG\temple\shaders\temple_breathing_shader.py
# ============================================================

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPalette

class TempleBreathingShader:
    def __init__(self, widget):
        self.widget = widget
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(1200)
        self.state = 0

    def _tick(self):
        # Breathing cycle: soft → medium → bright → medium → soft
        cycle = [
            QColor(0, 180, 255, 60),
            QColor(0, 180, 255, 120),
            QColor(0, 180, 255, 200),
            QColor(0, 180, 255, 120),
        ]

        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), cycle[self.state])
        self.widget.setPalette(palette)

        self.state = (self.state + 1) % len(cycle)
