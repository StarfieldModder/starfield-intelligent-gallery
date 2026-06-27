# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: orientation_panel.py
#
#  Description:
#      Placeholder holographic orientation panel. This module
#      will eventually display creative prompts, navigation
#      glyphs, or user‑guided orientation content.
# ================================================================

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class OrientationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def initialize(self):
        print("[OrientationPanel] initialize() called.")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Simple placeholder hologram rectangle
        painter.setPen(QColor(120, 200, 255, 180))
        painter.drawRect(self.rect().adjusted(10, 10, -10, -10))
