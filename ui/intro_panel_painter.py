# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: intro_panel_painter.py
# Module: Intro Panel — Painter
# ================================================================

from PySide6.QtGui import QPainter, QColor, QBrush


class IntroPanelPainter:

    def __init__(self, panel):
        self.panel = panel

    def paint(self, event):
        painter = QPainter(self.panel)
        painter.setRenderHint(QPainter.Antialiasing)

        r, g, b, a = self.panel.panel_color
        panel_color = QColor(r, g, b, a)

        br, bg, bb, ba = self.panel.border_color
        border_color = QColor(br, bg, bb, ba)

        painter.setBrush(QBrush(panel_color))
        painter.setPen(border_color)
        painter.drawRoundedRect(self.panel.rect(), 18, 18)
