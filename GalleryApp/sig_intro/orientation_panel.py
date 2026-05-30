# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: orientation_panel.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Subsystem: Holographic Intro Panel / Creative Orientation Window
#
#  Description:
#      Placeholder holographic orientation panel. This subsystem
#      will eventually display creative prompts, navigation glyphs,
#      or user‑guided orientation content. For now, it provides a
#      visible holographic frame so the SIG engine can activate it.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 1.0
#  Created: May 2026
#
#  Notes:
#      - Required by IntroPanelWidget.
#      - Provides a simple holographic border for visibility.
#      - Ready for future expansion (glyphs, text, parallax).
# ================================================================

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class OrientationPanel(QWidget):
    """
    Simple placeholder holographic orientation panel.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def initialize(self):
        print("[OrientationPanel] initialize() called.")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Soft holographic border
        painter.setPen(QColor(120, 200, 255, 180))
        painter.drawRect(self.rect().adjusted(12, 12, -12, -12))
