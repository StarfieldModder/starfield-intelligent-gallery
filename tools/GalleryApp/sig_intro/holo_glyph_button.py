# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: holo_glyph_button.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Subsystem: Holographic Intro Panel / Creative Orientation Window
#
#  Description:
#      This module is part of the SIG Introductory Floating Panel,
#      a holographic, Starfield‑inspired UI subsystem that provides
#      users with an open‑ended creative orientation experience.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 1.0
#  Created: May 2026
#
#  Notes:
#      This file is designed to be modular, extensible, and ready
#      for future enhancements including holographic effects,
#      parallax motion, particle dissolves, and sound integration.
# ================================================================
from PyQt6.QtWidgets import QPushButton, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty

class HoloGlyphButton(QPushButton):
    """
    A holographic glyph with hover animations and glow.
    """
    def __init__(self, title: str, sound_bus=None, parent=None):
        super().__init__(parent)
        self.sound_bus = sound_bus
        self._scale = 1.0

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label.setStyleSheet("""
            color: rgba(220, 235, 255, 0.95);
            font-size: 13px;
            letter-spacing: 2px;
        """)
        layout.addWidget(self.label)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.85)

        self.hover_anim = QPropertyAnimation(self, b"scale")
        self.hover_anim.setDuration(180)
        self.hover_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(180)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        if self.sound_bus:
            self.sound_bus.play_hover()

        self.hover_anim.stop()
        self.opacity_anim.stop()

        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.08)

        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(1.0)

        self.hover_anim.start()
        self.opacity_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.opacity_anim.stop()

        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(1.0)

        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(0.85)

        self.hover_anim.start()
        self.opacity_anim.start()

        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self._scale, self._scale)
        painter.translate(-self.width() / 2, -self.height() / 2)
        super().paintEvent(event)

    def getScale(self):
        return self._scale

    def setScale(self, value):
        self._scale = value
        self.update()

    scale = pyqtProperty(float, fget=getScale, fset=setScale)
