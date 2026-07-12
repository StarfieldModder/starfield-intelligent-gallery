# ============================================================
# File        : starfield_background.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Description : Cinematic drifting starfield background.
#               Pure black initialization (no flash),
#               smooth drift, subtle parallax.
# ============================================================

from __future__ import annotations

import random
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class StarfieldBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Opaque black background; window itself is translucent
        # so this becomes the "space" behind the relic panel.
        self.star_count = 180
        self.stars = []
        self._rng = random.Random(777)

        self._init_stars()

        # Drift timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_stars)
        self.timer.start(33)  # ~30 FPS

    # --------------------------------------------------------
    # Star initialization
    # --------------------------------------------------------
    def _init_stars(self):
        self.stars = []
        w = max(1, self.width())
        h = max(1, self.height())

        for _ in range(self.star_count):
            x = self._rng.uniform(0, w)
            y = self._rng.uniform(0, h)
            speed = self._rng.uniform(0.15, 0.55)
            size = self._rng.uniform(1.0, 2.2)
            self.stars.append([x, y, speed, size])

    # --------------------------------------------------------
    # Resize handling (fix tiny top-left strip issue)
    # --------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-seed stars to fill the new size instead of staying in the corner
        self._init_stars()

    # --------------------------------------------------------
    # Drift update
    # --------------------------------------------------------
    def _update_stars(self):
        w = self.width()
        h = self.height()

        for star in self.stars:
            star[1] += star[2]  # drift downward
            if star[1] > h:
                star[0] = self._rng.uniform(0, w)
                star[1] = -5

        self.update()

    # --------------------------------------------------------
    # Painting
    # --------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Pure black initialization — eliminates startup flash
        painter.fillRect(self.rect(), QColor(0, 0, 0, 255))

        painter.setPen(Qt.PenStyle.NoPen)

        # Draw stars
        for x, y, speed, size in self.stars:
            alpha = int(120 + speed * 200)
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(int(x), int(y), int(size), int(size))
