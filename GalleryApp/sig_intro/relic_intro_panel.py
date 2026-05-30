# ============================================================
# File        : relic_intro_panel.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Description : Golden-amber relic awakening panel.
#               Floating arc segments, Va'ruun-like glyph flicker,
#               sleeping intelligence, temple resonance hooks.
# ============================================================

from __future__ import annotations

import math
import random
from typing import List, Tuple

from PyQt6.QtCore import (
    Qt,
    QPointF,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QPainterPath,
)
from PyQt6.QtWidgets import QWidget


class RelicIntroPanel(QWidget):
    """
    Cinematic relic panel:
        - floating golden-amber arc segments
        - Va'ruun-like curved glyph flicker
        - breathing glow
        - micro-drift
        - awareness pulse hooks
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Core animation state
        self._frame_progress: float = 0.0      # 0 → 1: arc coalescence
        self._glow_intensity: float = 0.0      # 0 → 1: inner glow / awareness
        self._offset: QPointF = QPointF(0.0, 0.0)

        # Internal random seed for glyph flicker
        self._rng = random.Random(42)

        # Micro-drift animation (breathing)
        self._drift_anim = QPropertyAnimation(self, b"offset", self)
        self._drift_anim.setDuration(9000)
        self._drift_anim.setStartValue(QPointF(-3.0, -2.0))
        self._drift_anim.setEndValue(QPointF(3.0, 2.0))
        self._drift_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._drift_anim.setLoopCount(-1)

        # Soft awareness pulse (glow breathing)
        self._pulse_anim = QPropertyAnimation(self, b"glowIntensity", self)
        self._pulse_anim.setDuration(5200)
        self._pulse_anim.setStartValue(0.55)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------
    def getFrameProgress(self) -> float:
        return self._frame_progress

    def setFrameProgress(self, v: float) -> None:
        self._frame_progress = max(0.0, min(1.0, float(v)))
        self.update()

    frameProgress = pyqtProperty(float, fget=getFrameProgress, fset=setFrameProgress)

    def getGlowIntensity(self) -> float:
        return self._glow_intensity

    def setGlowIntensity(self, v: float) -> None:
        self._glow_intensity = max(0.0, min(1.0, float(v)))
        self.update()

    glowIntensity = pyqtProperty(float, fget=getGlowIntensity, fset=setGlowIntensity)

    def getOffset(self) -> QPointF:
        return self._offset

    def setOffset(self, v: QPointF) -> None:
        self._offset = v
        self.update()

    offset = pyqtProperty(QPointF, fget=getOffset, fset=setOffset)

    # --------------------------------------------------------
    # Public control hooks
    # --------------------------------------------------------
    def startHumPulse(self) -> None:
        """Called when awakening finishes; starts breathing glow."""
        self._pulse_anim.start()

    def startDrift(self) -> None:
        """Starts micro-drift of the relic arcs."""
        self._drift_anim.start()

    # --------------------------------------------------------
    # Painting
    # --------------------------------------------------------
    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.translate(self._offset)

        rect = self._panel_rect()

        # Base dark panel so starfield never shows "through" the relic
        painter.setPen(Qt.PenStyle.NoPen)
        base = QColor(5, 5, 10, 230)
        painter.setBrush(base)
        painter.drawRoundedRect(rect, 28, 28)

        # If nothing has awakened yet, stop after drawing the base
        if self._frame_progress <= 0.001 and self._glow_intensity <= 0.001:
            return

        # Inner warm glow
        self._paint_inner_glow(painter, rect)

        # Floating arc segments (primary relic shape)
        self._paint_arc_segments(painter, rect)

        # Va'ruun-like curved glyph flicker
        self._paint_glyph_flicker(painter, rect)

    def _panel_rect(self) -> QRectF:
        margin_x = self.width() * 0.18
        margin_y = self.height() * 0.18
        return QRectF(
            margin_x,
            margin_y,
            self.width() - 2 * margin_x,
            self.height() - 2 * margin_y,
        )

    # --------------------------------------------------------
    # Inner glow
    # --------------------------------------------------------
    def _paint_inner_glow(self, painter: QPainter, rect: QRectF) -> None:
        # Golden amber core, soft breathing
        base_alpha = 30 + int(80 * self._glow_intensity)
        base_alpha = max(0, min(base_alpha, 255))

        core = QColor(210, 160, 70, base_alpha)   # amber core
        halo = QColor(255, 210, 120, int(base_alpha * 0.7))

        painter.setPen(Qt.PenStyle.NoPen)

        # Core
        painter.setBrush(core)
        inner = rect.adjusted(rect.width() * 0.08,
                              rect.height() * 0.08,
                              -rect.width() * 0.08,
                              -rect.height() * 0.08)
        painter.drawRoundedRect(inner, 24, 24)

        # Soft halo
        painter.setBrush(halo)
        halo_rect = rect.adjusted(rect.width() * 0.02,
                                  rect.height() * 0.02,
                                  -rect.width() * 0.02,
                                  -rect.height() * 0.02)
        painter.drawRoundedRect(halo_rect, 32, 32)

    # --------------------------------------------------------
    # Floating arc segments
    # --------------------------------------------------------
    def _arc_segments(self, rect: QRectF) -> List[Tuple[float, float, float]]:
        """
        Returns a list of (start_angle_deg, span_deg, radius_scale)
        describing floating arc segments around the panel.
        """
        return [
            (-18, 70, 1.05),    # upper-left arc
            (110, 80, 1.08),    # upper-right arc
            (205, 75, 1.02),    # lower-right arc
            (300, 65, 1.06),    # lower-left arc
        ]

    def _paint_arc_segments(self, painter: QPainter, rect: QRectF) -> None:
        # Golden amber line color
        edge_color = QColor(255, 215, 140)
        edge_color.setAlpha(180 + int(60 * self._glow_intensity))
        pen = QPen(edge_color, 2.0)
        pen.setCosmetic(True)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = rect.center().x()
        cy = rect.center().y()
        base_radius = min(rect.width(), rect.height()) * 0.62

        # Coalescence: arcs grow in length and opacity with frame_progress
        progress = self._frame_progress

        for idx, (start_deg, span_deg, r_scale) in enumerate(self._arc_segments(rect)):
            # Each arc wakes slightly offset in time
            local_start = idx * 0.12
            local_end = local_start + 0.65
            t = (progress - local_start) / max(0.0001, (local_end - local_start))
            t = max(0.0, min(1.0, t))

            if t <= 0.0:
                continue

            # Ease-in for arc growth
            eased = t * t * (3 - 2 * t)

            # Arc bounding rect
            radius = base_radius * r_scale
            arc_rect = QRectF(
                cx - radius,
                cy - radius,
                2 * radius,
                2 * radius,
            )

            # Span grows with eased progress
            span = span_deg * eased

            # Slight floating offset based on glow + index
            float_phase = self._glow_intensity + idx * 0.37
            float_offset = math.sin(float_phase * math.pi * 2.0) * 3.0
            painter.save()
            painter.translate(0, float_offset)

            painter.drawArc(
                arc_rect,
                int(start_deg * 16),
                int(span * 16),
            )

            painter.restore()

    # --------------------------------------------------------
    # Va'ruun-like glyph flicker
    # --------------------------------------------------------
    def _paint_glyph_flicker(self, painter: QPainter, rect: QRectF) -> None:
        # Glyphs mostly appear during early/mid coalescence
        if self._frame_progress < 0.15 or self._frame_progress > 0.75:
            return

        # Flicker intensity
        flicker_strength = 1.0 - abs(self._frame_progress - 0.45) / 0.3
        flicker_strength = max(0.0, min(1.0, flicker_strength))

        if flicker_strength <= 0.01:
            return

        # Use deterministic random based on progress so it feels alive but stable
        seed = int(self._frame_progress * 10_000)
        self._rng.seed(seed)

        glyph_color = QColor(255, 220, 150)
        base_alpha = int(40 + 80 * flicker_strength)
        glyph_color.setAlpha(base_alpha)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glyph_color)

        cx = rect.center().x()
        cy = rect.center().y()
        radius = min(rect.width(), rect.height()) * 0.52

        # Draw a few curved crescent glyphs along an invisible orbit
        for _ in range(6):
            angle = self._rng.uniform(0, 360)
            rad = math.radians(angle)
            r = radius * self._rng.uniform(0.78, 1.05)

            gx = cx + math.cos(rad) * r
            gy = cy + math.sin(rad) * r

            size = self._rng.uniform(10, 22)
            thickness = size * 0.45

            # Crescent: two overlapping circles
            outer = QRectF(gx - size / 2, gy - size / 2, size, size)
            inner = QRectF(
                gx - size / 2 + thickness,
                gy - size / 2,
                size,
                size,
            )

            path = QPainterPath()
            path.addEllipse(outer)
            cut = QPainterPath()
            cut.addEllipse(inner)
            crescent = path.subtracted(cut)

            painter.save()
            painter.translate(0, self._rng.uniform(-2.0, 2.0))
            painter.drawPath(crescent)
            painter.restore()
