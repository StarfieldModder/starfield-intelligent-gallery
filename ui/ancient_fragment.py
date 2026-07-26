r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   A N C I E N T _ F R A G M E N T . P Y                                      ║
║   Starfield Intelligent Gallery  ·  2026.07.05                               ║
║   Author  : Mark J. Latsha  (StarfieldModder / Games)                        ║
║   Co-Author: Microsoft Copilot (AI Engineer Colleague)                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Floating curved stone relic fragment.                                       ║
║  Each fragment is a unique organic QPainterPath shape — amber-tinted,        ║
║  semi-transparent so nebula glows through, breathing at its own frequency,   ║
║  orbiting into the ring formation, erupting embers on contact, and           ║
║  responding to hover with scale + brightness surge.                          ║
║                                                                              ║
║  STATE MACHINE                                                               ║
║    DORMANT  → DRIFTING → ORBITING → SETTLING → SETTLED → SELECTED / DIMMED   ║
║                                                                              ║
║  Fragment carries one word of "YOU HAVE ENTERED A NEW WORLD A NEW UNIVERSE"  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import random
from typing import Optional

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QPen, QRadialGradient,
)

from core.diagnostic_reporter import record_error


# ── Fragment base geometry ────────────────────────────────────────────────────
_BASE_W = 210
_BASE_H = 118

# ── Spectral palette — amber / gold family ────────────────────────────────────
_CORE = [
    QColor(200, 128, 18), QColor(212, 162, 42), QColor(188, 98, 14),
    QColor(222, 188, 62), QColor(206, 140, 28), QColor(196, 114, 22),
    QColor(218, 178, 54), QColor(210, 148, 36), QColor(242, 212, 82),
]
_EDGE = [
    QColor(255, 195, 75), QColor(255, 222, 98), QColor(255, 175, 68),
    QColor(255, 238, 118), QColor(255, 204, 82), QColor(255, 188, 72),
    QColor(255, 232, 112), QColor(255, 208, 88), QColor(255, 248, 148),
]
_EMBER_COLS = [
    QColor(255, 175, 38), QColor(255, 128, 18), QColor(255, 242, 95),
]


# ══════════════════════════════════════════════════════════════════════════════
class AncientFragment:
    """
    A floating curved stone relic fragment.
    """

    DORMANT = 0
    DRIFTING = 1
    ORBITING = 2
    SETTLING = 3
    SETTLED = 4
    SELECTED = 5
    DIMMED = 6

    def __init__(self, word: str, index: int, seed: int) -> None:
        try:
            self.word = word
            self.index = index
            self._seed = seed

            self.x = self.y = 0.0
            self.sx = self.sy = 0.0
            self.tx = self.ty = 0.0

            self._orbit_angle = random.uniform(0.0, math.tau)
            self._orbit_radius = random.uniform(200, 310)
            self._orbit_speed = random.uniform(0.007, 0.018)

            self.rotation = random.uniform(0.0, 360.0)
            self.rot_speed = random.uniform(-1.4, 1.4)

            self.scale = 0.0
            self._target_scale = 1.0

            self.state = self.DORMANT
            self._state_t = 0.0

            rng = random.Random(seed + 7777)
            self._settled_rot = rng.uniform(-24.0, 24.0)
            self._breath_phase = rng.uniform(0.0, math.tau)
            self._breath_speed = rng.uniform(1.1, 1.8)

            self._embers: list[list] = []
            # 0.0 → no inscription, 1.0 → full word visible
            self.inscription: float = 0.0

            self._path: Optional[QPainterPath] = None

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "__init__",
                0,
                type(exc).__name__,
                str(exc),
                "critical",
                exc,
            )

    # ── Shape ─────────────────────────────────────────────────────────────────

    def _get_path(self) -> QPainterPath:
        try:
            if self._path is None:
                self._path = self._build_path()
            return self._path
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_get_path",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )
            return QPainterPath()

    def _build_path(self) -> QPainterPath:
        try:
            rng = random.Random(self._seed + 1337)
            n = rng.randint(5, 8)

            rx = _BASE_W * 0.44 * rng.uniform(0.72, 1.0)
            ry = _BASE_H * 0.46 * rng.uniform(0.68, 1.0)

            base_step = math.tau / n
            angles = []
            for i in range(n):
                jitter = rng.uniform(-base_step * 0.32, base_step * 0.32)
                angles.append(i * base_step + jitter)
            angles.sort()

            verts = []
            for a in angles:
                r_scale = rng.uniform(0.65, 1.0)
                verts.append(
                    QPointF(
                        math.cos(a) * rx * r_scale,
                        math.sin(a) * ry * r_scale,
                    )
                )

            path = QPainterPath()
            n_v = len(verts)
            start = QPointF(
                (verts[-1].x() + verts[0].x()) * 0.5,
                (verts[-1].y() + verts[0].y()) * 0.5,
            )
            path.moveTo(start)

            for i in range(n_v):
                ctrl = verts[i]
                nxt = QPointF(
                    (verts[i].x() + verts[(i + 1) % n_v].x()) * 0.5,
                    (verts[i].y() + verts[(i + 1) % n_v].y()) * 0.5,
                )
                path.quadTo(ctrl, nxt)

            path.closeSubpath()
            return path

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_build_path",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )
            return QPainterPath()

    # ── Placement ─────────────────────────────────────────────────────────────

    def place(self, sx: float, sy: float, tx: float, ty: float) -> None:
        try:
            self.x = self.sx = sx
            self.y = self.sy = sy
            self.tx = tx
            self.ty = ty
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "place",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )

    # ── State transitions ─────────────────────────────────────────────────────

    def begin_drift(self) -> None:
        self.state = self.DRIFTING
        self._state_t = 0.0

    def begin_orbit(self) -> None:
        self.state = self.ORBITING
        self._state_t = 0.0

    def _finalize_settle(self) -> None:
        try:
            self.x = self.tx
            self.y = self.ty
            self.rotation = self._settled_rot
            self.scale = 1.0
            self.state = self.SETTLED
            self._state_t = 0.0
            self._spawn_contact_embers()
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_finalize_settle",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )

    def select(self) -> None:
        if self.state in (self.SETTLED, self.DIMMED):
            self.state = self.SELECTED
            self._target_scale = 1.38
            self._state_t = 0.0

    def deselect(self) -> None:
        if self.state == self.SELECTED:
            self.state = self.SETTLED
            self._target_scale = 1.0

    def dim(self) -> None:
        if self.state == self.SETTLED:
            self.state = self.DIMMED
            self._target_scale = 0.80

    def undim(self) -> None:
        if self.state == self.DIMMED:
            self.state = self.SETTLED
            self._target_scale = 1.0

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def settled(self) -> bool:
        return self.state in (self.SETTLED, self.SELECTED, self.DIMMED)

    @property
    def is_selected(self) -> bool:
        return self.state == self.SELECTED

    # ── Hit test ──────────────────────────────────────────────────────────────

    def hit_test(self, px: float, py: float) -> bool:
        try:
            if not self.settled:
                return False
            dx = px - self.x
            dy = py - self.y
            rad = math.radians(-self.rotation)
            lx = dx * math.cos(rad) - dy * math.sin(rad)
            ly = dx * math.sin(rad) + dy * math.cos(rad)
            s = self.scale if self.scale > 0.01 else 0.01
            lx /= s
            ly /= s
            r = max(_BASE_W, _BASE_H) * 0.50
            return lx * lx + ly * ly <= r * r
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "hit_test",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )
            return False

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, t: float) -> None:
        try:
            dt = 1.0 / 60.0
            self._state_t += dt

            breath = math.sin(t * self._breath_speed + self._breath_phase)
            breath_scl = breath * 0.022
            breath_rot = math.sin(
                t * self._breath_speed * 0.65 + self._breath_phase
            ) * 2.2

            if self.state == self.DORMANT:
                self.scale = 0.0

            elif self.state == self.DRIFTING:
                self.scale = min(1.0, self._state_t / 3.0)
                self.rotation = (self.rotation + self.rot_speed * 0.8) % 360.0
                cx = self.tx + math.cos(self._orbit_angle) * self._orbit_radius
                cy = self.ty + math.sin(self._orbit_angle) * self._orbit_radius
                self.x += (cx - self.x) * 0.010
                self.y += (cy - self.y) * 0.010

            elif self.state == self.ORBITING:
                self._orbit_angle = (
                    self._orbit_angle + self._orbit_speed
                ) % math.tau
                self._orbit_radius = max(0.0, self._orbit_radius - 1.6)
                self.x = self.tx + math.cos(self._orbit_angle) * self._orbit_radius
                self.y = self.ty + math.sin(self._orbit_angle) * self._orbit_radius
                self.rotation = (self.rotation + self.rot_speed * 0.55) % 360.0
                self.rot_speed *= 0.997
                if self._orbit_radius < 6.0:
                    self._finalize_settle()

            elif self.state == self.SETTLING:
                alpha = 0.10
                self.rotation += (self._settled_rot - self.rotation) * alpha
                self.x += (self.tx - self.x) * alpha
                self.y += (self.ty - self.y) * alpha
                if abs(self.x - self.tx) < 1.5 and abs(self.y - self.ty) < 1.5:
                    self._finalize_settle()

            elif self.state == self.SETTLED:
                self.scale = 1.0 + breath_scl
                self.rotation = self._settled_rot + breath_rot

            elif self.state == self.SELECTED:
                deep = math.sin(t * 2.2 + self._breath_phase) * 0.040
                self.scale += (
                    self._target_scale + deep - self.scale
                ) * 0.055
                self.rotation = self._settled_rot + breath_rot * 1.6

            elif self.state == self.DIMMED:
                self.scale += (self._target_scale - self.scale) * 0.055
                self.rotation = self._settled_rot + breath_rot * 0.45

            self._update_embers()

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "update",
                0,
                type(exc).__name__,
                str(exc),
                "critical",
                exc,
            )

    # ── Embers ────────────────────────────────────────────────────────────────

    def _spawn_contact_embers(self) -> None:
        try:
            rng = random.Random(self._seed + 4242)
            for _ in range(34):
                angle = rng.uniform(0.0, math.tau)
                r = rng.uniform(20, 90)
                self._embers.append(
                    [
                        self.tx + math.cos(angle) * r * 0.25,
                        self.ty + math.sin(angle) * r * 0.25,
                        math.cos(angle) * rng.uniform(0.6, 3.0),
                        math.sin(angle) * rng.uniform(0.6, 3.0) - 0.3,
                        rng.randint(190, 255),  # alpha
                        rng.randint(0, 2),      # color index
                    ]
                )
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_spawn_contact_embers",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )

    def _update_embers(self) -> None:
        try:
            alive = []
            for e in self._embers:
                e[0] += e[2]
                e[1] += e[3]
                e[3] += 0.045
                e[4] -= 3.8
                if e[4] > 0:
                    alive.append(e)
            self._embers = alive
        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_update_embers",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, painter: QPainter, t: float) -> None:
        try:
            if self.state == self.DORMANT or self.scale < 0.01:
                return

            core = _CORE[self.index]
            edge = _EDGE[self.index]

            if self.state == self.DIMMED:
                alpha_m = 0.42
            elif self.state == self.SELECTED:
                alpha_m = 1.00
            elif self.state == self.DRIFTING:
                alpha_m = min(0.80, self._state_t / 2.5)
            else:
                alpha_m = 0.82

            painter.save()
            painter.translate(self.x, self.y)
            painter.rotate(self.rotation)
            painter.scale(self.scale, self.scale)

            path = self._get_path()

            dim = max(_BASE_W, _BASE_H) * 0.52
            grad = QRadialGradient(QPointF(0.0, 0.0), dim)
            grad.setColorAt(
                0.0,
                QColor(
                    core.red(),
                    core.green(),
                    core.blue(),
                    int(170 * alpha_m),
                ),
            )
            grad.setColorAt(
                0.50,
                QColor(
                    core.red() // 2,
                    core.green() // 2,
                    core.blue() // 5,
                    int(105 * alpha_m),
                ),
            )
            grad.setColorAt(1.0, QColor(8, 12, 38, int(75 * alpha_m)))
            painter.setBrush(grad)

            gw = 3.5 if self.state != self.SELECTED else 5.5
            pen = QPen(
                QColor(
                    edge.red(),
                    edge.green(),
                    edge.blue(),
                    int(215 * alpha_m),
                )
            )
            pen.setWidthF(gw)
            painter.setPen(pen)
            painter.drawPath(path)

            halo = QPen(
                QColor(
                    edge.red(),
                    edge.green(),
                    edge.blue(),
                    int(48 * alpha_m),
                )
            )
            halo.setWidthF(gw + 8.0)
            painter.setPen(halo)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            painter.restore()

            if self.inscription > 0.01:
                self._draw_inscription(painter, alpha_m)

            self._draw_embers(painter)

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "draw",
                0,
                type(exc).__name__,
                str(exc),
                "critical",
                exc,
            )

    def _draw_inscription(self, painter: QPainter, alpha_m: float) -> None:
        """
        Inscription reveal: driven by self.inscription (0.0–1.0),
        integrated with SIG timing engines.
        """
        try:
            n_show = max(0, int(len(self.word) * self.inscription))
            if n_show == 0:
                return

            visible = self.word[:n_show]

            fs = max(9, int(20 * self.scale))
            font = QFont("Segoe UI", fs, QFont.Weight.Light)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
            painter.setFont(font)
            fm = painter.fontMetrics()

            tw = fm.horizontalAdvance(self.word)
            tx = int(self.x - tw / 2)
            ty = int(self.y + fm.ascent() / 2)

            # Core inscription stroke
            base_alpha = int(235 * alpha_m * self.inscription)
            base_alpha = max(0, min(255, base_alpha))
            painter.setPen(QColor(255, 240, 210, base_alpha))
            painter.drawText(tx, ty, visible)

            # Soft outer glow — tied to inscription progress
            glow_alpha = int(160 * alpha_m * self.inscription)
            glow_alpha = max(0, min(255, glow_alpha))
            glow_pen = QPen(QColor(255, 180, 90, glow_alpha))
            glow_pen.setWidth(2.0)
            painter.setPen(glow_pen)
            painter.drawText(tx, ty, visible)

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_draw_inscription",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )

    def _draw_embers(self, painter: QPainter) -> None:
        """
        Contact embers: small glowing particles emitted when fragment settles,
        synced with SIG cinematic palette.
        """
        try:
            if not self._embers:
                return

            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)

            for e in self._embers:
                x, y, _, _, alpha, col_idx = e
                col = _EMBER_COLS[col_idx % len(_EMBER_COLS)]
                a = max(0, min(255, int(alpha)))
                ember_col = QColor(col.red(), col.green(), col.blue(), a)
                painter.setBrush(ember_col)
                painter.drawEllipse(QPointF(x, y), 3.0, 3.0)

            painter.restore()

        except Exception as exc:
            record_error(
                "ancient_fragment",
                "_draw_embers",
                0,
                type(exc).__name__,
                str(exc),
                "warning",
                exc,
            )
