# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: glyph_button.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Subsystem: Holographic Intro Panel / Creative Orientation Window
#
#  Description:
#      Placeholder holographic glyph button. This subsystem will
#      eventually provide interactive glyph-based navigation or
#      creative prompts. For now, it provides a visible holographic
#      element so the SIG engine can activate it.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 1.0
#  Created: May 2026
#
#  Notes:
#      - Required by IntroPanelWidget.
#      - Provides a simple glowing glyph placeholder.
#      - Ready for future expansion (animations, pulses, actions).
# ================================================================

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt


class GlyphButton(QWidget):
    """
    Simple placeholder holographic glyph button.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def initialize(self):
        print("[GlyphButton] initialize() called.")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Soft glowing circle glyph
        pen = QPen(QColor(120, 200, 255, 200), 4)
        painter.setPen(pen)

        radius = min(self.width(), self.height()) // 3
        center = self.rect().center()

        painter.drawEllipse(center, radius, radius)
