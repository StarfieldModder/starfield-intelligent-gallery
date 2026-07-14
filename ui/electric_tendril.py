r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   E L E C T R I C _ T E N D R I L . P Y                                      ║
║   Starfield Intelligent Gallery  ·  2026.07.05                               ║
║   Author  : Mark J. Latsha  (StarfieldModder / Games)                        ║
║   Co-Author: Microsoft Copilot (AI Engineer Colleague)                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Branching plasma filament between two world-space points.                   ║
║                                                                              ║
║  VISUAL BEHAVIOUR                                                            ║
║    • Main trunk: cubic Bézier whose two control points jitter every frame    ║
║      using seeded sin/cos oscillators — looks alive, never repeats exactly.  ║
║    • Sub-branches: N quadratic arcs forking from random trunk positions,     ║
║      perpendicular-ish to the main direction, also jittered each frame.      ║
║    • Two-pass rendering: fat translucent outer glow + thin bright hot core.  ║
║    • Alpha pulses on a sine wave — the filament breathes and flickers.       ║
║    • Color: cyan #00F0DC → white-hot core, amber #FFB830 branches.           ║
║                                                                              ║
║  USAGE                                                                       ║
║    t = ElectricTendril((sx, sy), (ex, ey), seed=42)                          ║
║    t.update_endpoints((sx, sy), (ex, ey))  # call each frame if pts move     ║
║    t.draw(painter, elapsed_seconds)         # call inside paintEvent         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import math
import random

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui  import QColor, QPainter, QPainterPath, QPen


# ── Default colours ───────────────────────────────────────────────────────────
_CYAN_OUTER = QColor(  0, 240, 220)   # outer glow
_CYAN_CORE  = QColor( 80, 255, 245)   # white-hot inner core
_AMBER      = QColor(255, 185,  48)   # branch tips / amber accent


# ══════════════════════════════════════════════════════════════════════════════
class ElectricTendril:
    """
    A living branching plasma arc from one fragment to another.

    Parameters
    ----------
    start, end      : (float, float) world-space endpoints
    alpha_max       : peak alpha for the main trunk (0–255)
    n_branches      : number of sub-arc forks
    seed            : deterministic seed — same seed → same branch layout
    """

    def __init__(
        self,
        start:      tuple[float, float],
        end:        tuple[float, float],
        alpha_max:  int   = 210,
        n_branches: int   = 3,
        seed:       int   = 0,
    ) -> None:
        self.sx, self.sy = start
        self.ex, self.ey = end
        self.alpha_max   = alpha_max
        self.n_branches  = n_branches
        self._seed       = seed

        rng = random.Random(seed + 31337)

        # Phase offset — unique per tendril so they don't pulse in sync
        self._pulse_phase = rng.uniform(0.0, math.tau)
        self._pulse_speed = rng.uniform(3.8, 6.2)

        # Jitter oscillator seeds for control points
        self._js = [rng.uniform(0.0, math.tau) for _ in range(4)]
        self._jw = [rng.uniform(1.6, 3.5)      for _ in range(4)]

        # Branch layout (fixed per seed)
        self._branch_t     = [rng.uniform(0.18, 0.82) for _ in range(n_branches)]
        self._branch_len   = [rng.uniform(18.0, 62.0) for _ in range(n_branches)]
        self._branch_side  = [rng.choice([-1, 1])      for _ in range(n_branches)]
        self._branch_angle = [rng.uniform(25.0, 68.0)  for _ in range(n_branches)]
        # Secondary branch: each branch may have one child
        self._has_child    = [rng.random() < 0.45      for _ in range(n_branches)]
        self._child_len    = [rng.uniform(10.0, 30.0)  for _ in range(n_branches)]
        self._child_angle  = [rng.uniform(-30.0, 30.0) for _ in range(n_branches)]

        # Per-frame jitter seeds for branch tips (make them flicker)
        self._btip_seed = [rng.uniform(0.0, math.tau) for _ in range(n_branches)]
        self._btip_w    = [rng.uniform(4.5, 9.0)      for _ in range(n_branches)]

    # ── Public API ────────────────────────────────────────────────────────────

    def update_endpoints(
        self,
        start: tuple[float, float],
        end:   tuple[float, float],
    ) -> None:
        """Update endpoints each frame when fragments are moving."""
        self.sx, self.sy = start
        self.ex, self.ey = end

    def draw(self, painter: QPainter, t: float, alpha_mult: float = 1.0) -> None:
        """
        Render the tendril at elapsed time t (seconds).
        alpha_mult scales overall visibility (0.0 = invisible, 1.0 = full).
        """
        pulse = 0.55 + 0.45 * math.sin(t * self._pulse_speed + self._pulse_phase)
        trunk_alpha = int(self.alpha_max * pulse * alpha_mult)
        if trunk_alpha < 6:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cp1, cp2 = self._control_points(t)

        # ── Main trunk ────────────────────────────────────────────────────────
        self._draw_trunk(painter, cp1, cp2, trunk_alpha)

        # ── Sub-branches ──────────────────────────────────────────────────────
        branch_alpha = int(trunk_alpha * 0.60)
        if branch_alpha < 6:
            return

        trunk_pts = self._sample_bezier(cp1, cp2, 24)
        for i in range(self.n_branches):
            self._draw_branch(painter, t, trunk_pts, i, branch_alpha)

    # ── Internal geometry ─────────────────────────────────────────────────────

    def _control_points(self, t: float) -> tuple[QPointF, QPointF]:
        """
        Compute two cubic Bézier control points that oscillate each frame.
        The jitter is perpendicular to the trunk direction so the arc
        bows left / right without the endpoints drifting.
        """
        mx = (self.sx + self.ex) * 0.5
        my = (self.sy + self.ey) * 0.5

        dx = self.ex - self.sx
        dy = self.ey - self.sy
        length = math.sqrt(dx * dx + dy * dy) or 1.0

        # Perpendicular unit vector
        px = -dy / length
        py =  dx / length

        jitter_scale = length * 0.22

        # cp1 sits between start and midpoint; cp2 between midpoint and end
        j1 = math.sin(t * self._jw[0] + self._js[0]) * jitter_scale
        j2 = math.cos(t * self._jw[1] + self._js[1]) * jitter_scale
        j3 = math.sin(t * self._jw[2] + self._js[2]) * jitter_scale * 0.55
        j4 = math.cos(t * self._jw[3] + self._js[3]) * jitter_scale * 0.55

        cp1 = QPointF(
            self.sx * 0.55 + mx * 0.45 + px * j1 + py * j3,
            self.sy * 0.55 + my * 0.45 + py * j1 - px * j3,
        )
        cp2 = QPointF(
            self.ex * 0.55 + mx * 0.45 + px * j2 + py * j4,
            self.ey * 0.55 + my * 0.45 + py * j2 - px * j4,
        )
        return cp1, cp2

    def _draw_trunk(
        self,
        painter: QPainter,
        cp1: QPointF,
        cp2: QPointF,
        alpha: int,
    ) -> None:
        path = QPainterPath()
        path.moveTo(self.sx, self.sy)
        path.cubicTo(cp1, cp2, QPointF(self.ex, self.ey))

        # Outer glow — wide, cyan, semi-transparent
        pen = QPen(QColor(_CYAN_OUTER.red(), _CYAN_OUTER.green(),
                          _CYAN_OUTER.blue(), int(alpha * 0.42)))
        pen.setWidthF(5.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        # Mid glow — medium width
        pen2 = QPen(QColor(_CYAN_OUTER.red(), _CYAN_OUTER.green(),
                           _CYAN_OUTER.blue(), int(alpha * 0.68)))
        pen2.setWidthF(2.8)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen2)
        painter.drawPath(path)

        # Hot core — thin, near-white
        pen3 = QPen(QColor(_CYAN_CORE.red(), _CYAN_CORE.green(),
                           _CYAN_CORE.blue(), int(alpha * 0.92)))
        pen3.setWidthF(1.1)
        pen3.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen3)
        painter.drawPath(path)

    def _draw_branch(
        self,
        painter: QPainter,
        t: float,
        trunk_pts: list[tuple[float, float]],
        i: int,
        alpha: int,
    ) -> None:
        # Origin on trunk
        idx = min(int(self._branch_t[i] * len(trunk_pts)), len(trunk_pts) - 1)
        ox, oy = trunk_pts[idx]

        # Direction: perpendicular to trunk direction at that point + angle bias
        if idx + 1 < len(trunk_pts):
            nx, ny = trunk_pts[idx + 1]
        else:
            nx, ny = trunk_pts[idx - 1]
        trunk_angle = math.atan2(ny - oy, nx - ox)
        branch_angle = trunk_angle + math.radians(
            self._branch_side[i] * self._branch_angle[i]
        )

        blen = self._branch_len[i]
        # Tip jitters each frame
        tip_jitter = math.sin(t * self._btip_w[i] + self._btip_seed[i]) * 7.0

        ex = ox + math.cos(branch_angle) * blen + tip_jitter
        ey = oy + math.sin(branch_angle) * blen + tip_jitter * 0.6

        # Midpoint control (slight bow)
        mx = (ox + ex) * 0.5 + math.sin(t * 5.1 + i) * 4.0
        my = (oy + ey) * 0.5 + math.cos(t * 4.3 + i) * 4.0

        path = QPainterPath()
        path.moveTo(ox, oy)
        path.quadTo(mx, my, ex, ey)

        # Outer
        pen = QPen(QColor(_CYAN_OUTER.red(), _CYAN_OUTER.green(),
                          _CYAN_OUTER.blue(), int(alpha * 0.55)))
        pen.setWidthF(2.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        # Core
        pen2 = QPen(QColor(_AMBER.red(), _AMBER.green(),
                           _AMBER.blue(), int(alpha * 0.80)))
        pen2.setWidthF(1.0)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen2)
        painter.drawPath(path)

        # Optional child branch from near the tip
        if self._has_child[i] and blen > 22:
            child_angle = branch_angle + math.radians(self._child_angle[i])
            clen = self._child_len[i]
            cx2  = ex + math.cos(child_angle) * clen
            cy2  = ey + math.sin(child_angle) * clen
            cmx  = (ex + cx2) * 0.5 + math.sin(t * 7.3 + i + 0.5) * 3.0
            cmy  = (ey + cy2) * 0.5 + math.cos(t * 6.1 + i + 0.5) * 3.0

            cpath = QPainterPath()
            cpath.moveTo(ex, ey)
            cpath.quadTo(cmx, cmy, cx2, cy2)

            child_alpha = int(alpha * 0.45)
            cpen = QPen(QColor(_AMBER.red(), _AMBER.green(),
                               _AMBER.blue(), child_alpha))
            cpen.setWidthF(0.8)
            cpen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(cpen)
            painter.drawPath(cpath)

    # ── Bézier sampling ───────────────────────────────────────────────────────

    def _sample_bezier(
        self,
        cp1: QPointF,
        cp2: QPointF,
        n:   int,
    ) -> list[tuple[float, float]]:
        """Sample n+1 points along the cubic Bézier curve."""
        pts: list[tuple[float, float]] = []
        for i in range(n + 1):
            tt = i / n
            tm = 1.0 - tt
            x  = (tm**3 * self.sx
                  + 3 * tm**2 * tt * cp1.x()
                  + 3 * tm * tt**2 * cp2.x()
                  + tt**3 * self.ex)
            y  = (tm**3 * self.sy
                  + 3 * tm**2 * tt * cp1.y()
                  + 3 * tm * tt**2 * cp2.y()
                  + tt**3 * self.ey)
            pts.append((x, y))
        return pts
