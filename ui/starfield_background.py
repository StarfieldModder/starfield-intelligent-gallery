# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: starfield_background.py
# Module: Cinematic Starfield Background Layer
# Version: 2026.06.26 — PySide6 Unified Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# ================================================================

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtWidgets import QWidget


class StarfieldBackground(QWidget):
    """
    Cinematic starfield background layer.
    Provides:
    - Static starfield rendering
    - Jump Cruise animation hook
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        # Starfield color (soft blue-white)
        self.star_color = QColor(200, 220, 255, 180)

        # Opacity effect for jump animation
        self._jump_opacity = 1.0

    # ------------------------------------------------------------
    # Jump Cruise animation (placeholder for Phase 2)
    # ------------------------------------------------------------
    def start_jump_cruise(self):
        """
        Placeholder cinematic effect.
        Future versions will include:
        - Warp streaks
        - Radial distortion
        - Brightness surge
        - Fade-to-white
        """

        anim = QPropertyAnimation(self, b"jumpOpacity")
        anim.setDuration(900)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        # Restore after a delay
        QTimer.singleShot(1000, lambda: self._reset_jump())

    def _reset_jump(self):
        self._jump_opacity = 1.0
        self.update()

    # ------------------------------------------------------------
    # Property for animation
    # ------------------------------------------------------------
    def get_jump_opacity(self):
        return self._jump_opacity

    def set_jump_opacity(self, value):
        self._jump_opacity = value
        self.update()

    jumpOpacity = property(get_jump_opacity, set_jump_opacity)

    # ------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setOpacity(self._jump_opacity)

        # Simple starfield placeholder
        painter.setBrush(QBrush(self.star_color))
        painter.setPen(Qt.NoPen)

        w = self.width()
        h = self.height()

        # Draw scattered stars
        for i in range(120):
            x = (i * 73) % w
            y = (i * 127) % h
            painter.drawEllipse(x, y, 2, 2)
