# ============================================================
#  TEMPLE GLYPH PULSE ANIMATION
#  Location: C:\IG\temple\glyph_pulse_animation.py
# ============================================================

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from sentinel.visual.theme_pack import (
    GLYPH_GLOW_SOFT, GLYPH_GLOW_MEDIUM, GLYPH_GLOW_STRONG
)

class GlyphPulse:
    def __init__(self, glyph_widget, pulse_word):
        self.widget = glyph_widget
        self.pulse_word = pulse_word
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(900)

    def _tick(self):
        if self.pulse_word == "soft":
            color = GLYPH_GLOW_SOFT
        elif self.pulse_word == "medium":
            color = GLYPH_GLOW_MEDIUM
        else:
            color = GLYPH_GLOW_STRONG

        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), color)
        self.widget.setPalette(palette)
