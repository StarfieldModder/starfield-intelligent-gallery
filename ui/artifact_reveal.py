# ================================================================
# File        : artifact_reveal.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (Engineering Assistant)
# Created     : June 2026
# Description : Cinematic Artifact Reveal Sequence for SIG Intro.
# ================================================================

from PySide6.QtCore import (
    Qt, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QColor, QPen
)
from PySide6.QtWidgets import QWidget

from animation_engine import create_fade_in, create_glow_pulse


class ArtifactReveal(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.opacity = 0.0
        self.rotation = 0.0

        self._fade_anim = None
        self._rotate_anim = None
        self._glow_anim = None

        self.hide()

    # ------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setOpacity(self.opacity)

        # Artifact color
        pen = QPen(QColor(200, 220, 255, 180), 3)
        painter.setPen(pen)

        # Centered circle
        rect = QRectF(
            self.width() * 0.25,
            self.height() * 0.25,
            self.width() * 0.50,
            self.height() * 0.50
        )

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.rotation)
        painter.translate(-self.width() / 2, -self.height() / 2)

        painter.drawEllipse(rect)

        painter.restore()

    # ------------------------------------------------------------
    # Cinematic Sequence
    # ------------------------------------------------------------
    def start_reveal(self):
        self.show()

        # Fade-in
        fade = QPropertyAnimation(self, b"opacity")
        fade.setDuration(1500)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.InOutQuad)

        # Rotation
        rotate = QPropertyAnimation(self, b"rotation")
        rotate.setDuration(4000)
        rotate.setStartValue(0)
        rotate.setEndValue(360)
        rotate.setEasingCurve(QEasingCurve.InOutQuad)
        rotate.setLoopCount(2)

        # Glow pulse (using your animation_engine)
        glow = create_glow_pulse(self, color="white", min_radius=10, max_radius=40, duration=2000)

        group = QParallelAnimationGroup()
        group.addAnimation(fade)
        group.addAnimation(rotate)

        self._fade_anim = fade
        self._rotate_anim = rotate
        self._glow_anim = glow

        glow.start()
        group.start()
