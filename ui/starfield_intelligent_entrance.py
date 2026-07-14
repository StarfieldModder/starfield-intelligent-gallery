# File: ui/starfield_intelligent_entrance.py
r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      S T A R F I E L D _ I N T E L L I G E N T  ║
║        ██╔════╝ ██║ ██╔════╝      _ E N T R A N C E . P Y                    ║
║        ███████╗ ██║ ██║  ███╗      SIG Starfield Subsystem — Phase Zero      ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "Light gathers before the story begins."   ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""

from __future__ import annotations

import random
from typing import List

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QBrush, Qt

# ─────────────────────────────────────────────────────────────────────────────
# Director’s Cut bounded randomness
# ─────────────────────────────────────────────────────────────────────────────

def dc_rand(low: float, high: float) -> float:
    return random.uniform(low, high)

# ─────────────────────────────────────────────────────────────────────────────
# Starfield constants
# ─────────────────────────────────────────────────────────────────────────────

FOCAL   = 500
Z_FAR   = 1200
Z_NEAR  = 10
N_STARS = 250

STAR_PALETTE = [
    QColor(155, 176, 255),
    QColor(200, 215, 255),
    QColor(200, 215, 255),
    QColor(250, 240, 210),
    QColor(255, 215, 130),
    QColor(255, 175,  80),
    QColor(255, 100,  60),
    QColor(  0, 240, 220),
]

NEBULA_DEFS = [
    (0.18, 0.26, 0.30, (92, 22, 140, 64),  (0, 0, 0, 0)),
    (0.78, 0.68, 0.38, (18, 78, 148, 56),  (0, 0, 0, 0)),
    (0.52, 0.82, 0.28, (148, 58, 18, 48),  (0, 0, 0, 0)),
    (0.38, 0.50, 0.42, (0, 118, 108, 44),  (0, 0, 0, 0)),
    (0.60, 0.30, 0.26, (120, 40, 180, 40), (0, 0, 0, 0)),
    (0.30, 0.72, 0.22, (220, 140, 60, 36), (0, 0, 0, 0)),
]

NEBULA_VX = [0.0010, -0.0006, 0.0005, -0.0005, 0.0007, -0.0004]
NEBULA_VY = [-0.0005, 0.0006,  0.0008,  0.0003, -0.0002, 0.0005]


class Star:
    __slots__ = ("wx", "wy", "z", "vz", "color", "base_r")

    def __init__(self, rng: random.Random) -> None:
        self.wx    = rng.uniform(-1.0, 1.0)
        self.wy    = rng.uniform(-1.0, 1.0)
        self.z     = rng.uniform(Z_NEAR + 1, Z_FAR)
        self.vz    = rng.uniform(0.5, 3.8)
        self.color = rng.choice(STAR_PALETTE)
        self.base_r = rng.uniform(0.8, 2.2)

    def reset(self, rng: random.Random) -> None:
        self.wx    = rng.uniform(-1.0, 1.0)
        self.wy    = rng.uniform(-1.0, 1.0)
        self.z     = float(Z_FAR)
        self.color = rng.choice(STAR_PALETTE)
        self.base_r = rng.uniform(0.8, 2.2)


class StarfieldEntrance:
    """
    Pure starfield + nebula subsystem.

    No UI, no phases, no whispers — just motion + draw helpers.
    SpaceFlightWidget calls into this like a rhythm section.
    """

    def __init__(self, seed: int = 20260712) -> None:
        self.rng = random.Random(seed)

        self.stars: List[Star] = [Star(self.rng) for _ in range(N_STARS)]
        self.active_stars: int = 1

        self.neb_ox = [0.0] * len(NEBULA_DEFS)
        self.neb_oy = [0.0] * len(NEBULA_DEFS)

        self.neb_strength: float = dc_rand(0.30, 0.35)
        self.neb_alpha: float = 0.0
        self.star_speed: float = 0.0

    # ─────────────────────────────────────────────────────────────────────
    # Initialization helpers
    # ─────────────────────────────────────────────────────────────────────

    def reset_bloom(self) -> None:
        """Reset to single pinprick bloom."""
        self.active_stars = 1
        for i, s in enumerate(self.stars):
            s.z  = float(Z_FAR)
            s.wx = 0.0
            s.wy = 0.0
            s.vz = self.rng.uniform(0.2, 0.6) if i == 0 else self.rng.uniform(0.1, 0.3)
            s.color = self.rng.choice(STAR_PALETTE)
            s.base_r = self.rng.uniform(0.8, 1.6)

    # ─────────────────────────────────────────────────────────────────────
    # Per‑frame update
    # ─────────────────────────────────────────────────────────────────────

    def advance(self, dt: float, phase2_fraction: float) -> None:
        """
        Advance starfield + nebula one tick.

        phase2_fraction: 0.0 .. 1.0 — how far into AWAKENING bloom we are.
        """
        ph2 = max(0.0, min(1.0, phase2_fraction))
        neb_mul = 1.0 + self.neb_strength
        self.star_speed = 0.35 + ph2 * 1.8 * (1.0 + self.neb_strength * 0.28)

        raw_neb = ph2 * 1.6 * neb_mul
        self.neb_alpha = min(0.78, raw_neb)

        desired_active = max(1, int(ph2 * N_STARS * (1.0 + self.neb_strength * 1.4)))
        if desired_active > self.active_stars:
            for i in range(self.active_stars, desired_active):
                s = self.stars[i]
                spread = 0.01 + ph2 * (0.48 + self.neb_strength * 0.12)
                s.wx = self.rng.uniform(-spread, spread)
                s.wy = self.rng.uniform(-spread, spread)
                s.z  = float(Z_FAR)
                s.vz = self.rng.uniform(0.6, 1.6) * (0.6 + ph2 * 1.6)
                s.color = self.rng.choice(STAR_PALETTE)
                s.base_r = self.rng.uniform(0.8, 2.8)
            self.active_stars = desired_active

        for s in self.stars[:self.active_stars]:
            s.z -= s.vz * self.star_speed
            if s.z < Z_NEAR:
                s.reset(self.rng)

        for k in range(len(self.neb_ox)):
            self.neb_ox[k] += NEBULA_VX[k] * dt * (1.0 + self.neb_strength * 0.28)
            self.neb_oy[k] += NEBULA_VY[k] * dt * (1.0 + self.neb_strength * 0.28)

    # ─────────────────────────────────────────────────────────────────────
    # Draw helpers
    # ─────────────────────────────────────────────────────────────────────

    def paint_nebulae(self, painter: QPainter, w: int, h: int) -> None:
        painter.save()
        try:
            painter.setCompositionMode(QPainter.CompositionMode.Screen)
        except Exception:
            pass
        painter.setOpacity(max(0.12, min(1.0, self.neb_alpha * 0.92)))
        for k, (cfx, cfy, rfrac, inner, outer) in enumerate(NEBULA_DEFS):
            ox  = self.neb_ox[k]
            oy  = self.neb_oy[k]
            px  = (cfx + ox) * w
            py  = (cfy + oy) * h
            rad = rfrac * w * (1.0 + self.neb_strength * 0.22)
            grad = QRadialGradient(QPointF(px, py), rad)
            ri, gi, bi, ai = inner
            ro, go, bo, ao = outer
            scaled_ai = int(ai * (0.55 + 0.45 * min(1.0, self.neb_strength)))
            scaled_ai = max(18, min(220, scaled_ai))
            grad.setColorAt(0.0, QColor(ri, gi, bi, scaled_ai))
            grad.setColorAt(1.0, QColor(ro, go, bo, ao))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), rad, rad)
        try:
            painter.setCompositionMode(QPainter.CompositionMode.SourceOver)
        except Exception:
            pass
        painter.restore()

    def paint_stars(self, painter: QPainter, cx: float, cy: float, elapsed: float, breath_start: float) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        ph2_frac = min(1.0, max(0.08, (elapsed - breath_start) / 8.0))
        neb_bias = 1.0 + self.neb_strength * 0.12
        for s in self.stars[:self.active_stars]:
            sx = cx + FOCAL * (s.wx * cx * 0.9) / s.z
            sy = cy + FOCAL * (s.wy * cy * 0.9) / s.z
            r  = s.base_r * (FOCAL / s.z)
            r  = max(0.5, min(r, 6.0))
            bright = min(1.0, FOCAL / s.z * 0.65 * neb_bias)
            c = s.color
            alpha = int(220 * bright * ph2_frac)
            alpha = max(alpha, 28)
            painter.setBrush(QColor(c.red(), c.green(), c.blue(), alpha))
            painter.drawEllipse(QPointF(sx, sy), r, r)
