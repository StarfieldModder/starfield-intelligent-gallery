# ============================================================
# File        : relic_button.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Description : Amber invitation glyph button.
#               Particle-like coalescence, soft text reveal,
#               warm hover pulse.
# ============================================================

from __future__ import annotations

import random

from PyQt6.QtCore import (
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPen,
)
from PyQt6.QtWidgets import QPushButton


class RelicButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        self._coalesce: float = 0.0      # 0 → 1: background / frame forming
        self._particle: float = 0.0      # 0 → 1: text + particles reveal

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        # Transparent base; relic panel now provides a solid backing
        self.setStyleSheet("background-color: transparent; border: none;")

        self._rng = random.Random(1337)

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------
    def getCoalesceProgress(self) -> float:
        return self._coalesce

    def setCoalesceProgress(self, v: float) -> None:
        self._coalesce = max(0.0, min(1.0, float(v)))
        self.update()

    coalesceProgress = pyqtProperty(float, fget=getCoalesceProgress, fset=setCoalesceProgress)

    def getParticleProgress(self) -> float:
        return self._particle

    def setParticleProgress(self, v: float) -> None:
        self._particle = max(0.0, min(1.0, float(v)))
        self.update()

    particleProgress = pyqtProperty(float, fget=getParticleProgress, fset=setParticleProgress)

    # --------------------------------------------------------
    # Painting
    # --------------------------------------------------------
    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        rect = self.rect()

        # Background coalescence bar (amber)
        self._paint_coalescence(painter, rect, w, h)

        # Particle-like sparks
        self._paint_particles(painter, rect, w, h)

        # Text reveal
        self._paint_text(painter, rect, w, h)

    def _paint_coalescence(self, painter: QPainter, rect, w: int, h: int) -> None:
        if self._coalesce <= 0.0:
            return

        t = self._coalesce
        eased = t * t * (3 - 2 * t)

        # Amber bar grows from center outward
        bar_width = int(w * eased)
        x = (w - bar_width) // 2

        core = QColor(210, 160, 70, 160)
        edge = QColor(255, 215, 140, 210)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(core)
        painter.drawRoundedRect(x, 0, bar_width, h, 6, 6)

        # Edge outline
        pen = QPen(edge, 1.2)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 6, 6)

    def _paint_particles(self, painter: QPainter, rect, w: int, h: int) -> None:
        if self._particle <= 0.05:
            return

        t = self._particle
        count = int(12 * t)

        base_color = QColor(255, 220, 150)
        base_color.setAlpha(int(80 + 80 * t))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base_color)

        # Deterministic random per frame
        seed = int(t * 10_000)
        self._rng.seed(seed)

        for _ in range(count):
            px = self._rng.uniform(w * 0.15, w * 0.85)
            py = self._rng.uniform(h * 0.2, h * 0.8)
            r = self._rng.uniform(1.0, 2.4)
            painter.drawEllipse(int(px - r), int(py - r), int(2 * r), int(2 * r))

    def _paint_text(self, painter: QPainter, rect, w: int, h: int) -> None:
        t = self._particle
        if t <= 0.0:
            return

        # Soft fade-in
        alpha = int(255 * max(0.0, min(1.0, t)))
        text_color = QColor(255, 235, 210, alpha)

        font = QFont("Segoe UI", 11)
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 103)
        painter.setFont(font)
        painter.setPen(text_color)

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
