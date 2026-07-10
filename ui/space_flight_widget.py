r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   S P A C E _ F L I G H T _ W I D G E T . P Y                               ║
║   Ancient Intelligence Awakening Sequence — 8-Phase Orchestrator            ║
║   Starfield Intelligent Gallery  ·  2026.07.06 — Whispering Chambers        ║
║   Author  : Mark J. Latsha  (StarfieldModder / Games)                       ║
║   Co-Author: Microsoft Copilot (AI Engineer Colleague)                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PHASES                                                                     ║
║    0  VOID        2.5 s   absolute black after The Crossing ends            ║
║    1  BREATH      4.0 s   single pulsing pinpoint — heartbeat               ║
║    2  AWAKENING   8.0 s   3-D stars bloom; four nebulae drift in            ║
║    3  WANDERING   6.0 s   Va'ruun glyphs appear, tumble playfully           ║
║    4  RECOGNITION 5.0 s   electric tendrils arc glyph-to-glyph              ║
║    5  ASSEMBLY    6.0 s   stone fragments orbit → lock; embers burst        ║
║    6  INSCRIPTION 4.0 s   letters carved on fragments by lightning          ║
║    7  REVELATION  2.5 s   everything stills — message complete              ║
║                                                                             ║
║  SIGNALS                                                                    ║
║    flight_finished — emitted when REVELATION phase ends or user skips       ║
║                                                                             ║
║  WHISPERING CHAMBERS                                                        ║
║    Soft hooks that speak through TempleConsole.throne_speaks(text)         ║
║    if present on the parent — otherwise they whisper to stdout.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    Qt, QPointF, QRectF, QTimer, Signal,
)
from PySide6.QtGui import (
    QBrush, QColor, QFont, QKeySequence,
    QPainter, QPainterPath, QPen,
    QRadialGradient, QShortcut,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget, QApplication

try:
    from .ancient_fragment import AncientFragment
    from .electric_tendril  import ElectricTendril
except ImportError:
    from ancient_fragment import AncientFragment   # type: ignore
    from electric_tendril  import ElectricTendril  # type: ignore

# ── Phase timing (cumulative seconds) ────────────────────────────────────────
_T_VOID      = 2.5
_T_BREATH    = _T_VOID      + 4.0    #  6.5
_T_AWAKENING = _T_BREATH    + 8.0    # 14.5
_T_WANDERING = _T_AWAKENING + 6.0    # 20.5
_T_RECOGN    = _T_WANDERING + 5.0    # 25.5
_T_ASSEMBLY  = _T_RECOGN    + 6.0    # 31.5
_T_INSCRIPT  = _T_ASSEMBLY  + 4.0    # 35.5
_T_REVEAL    = _T_INSCRIPT  + 2.5    # 38.0

_PHASE_ENDS = [
    _T_VOID, _T_BREATH, _T_AWAKENING, _T_WANDERING,
    _T_RECOGN, _T_ASSEMBLY, _T_INSCRIPT, _T_REVEAL,
]

# ── 3-D starfield constants ────────────────────────────────────────────────
_FOCAL   = 500
_Z_FAR   = 1200
_Z_NEAR  = 10
_N_STARS = 250

_STAR_PALETTE = [
    QColor(155, 176, 255),   # O/B  blue-white
    QColor(200, 215, 255),   # A    white       (×2 weight)
    QColor(200, 215, 255),   # A    white
    QColor(250, 240, 210),   # F    yellow-white
    QColor(255, 215, 130),   # G    gold
    QColor(255, 175,  80),   # K    orange
    QColor(255, 100,  60),   # M    deep red
    QColor(  0, 240, 220),   # Varuun cyan
]

# ── Nebula configs: (cx_frac, cy_frac, r_frac, inner RGBA, outer RGBA) ────
_NEBULA_DEFS = [
    (0.20, 0.28, 0.32, (82, 18, 130, 52),  (0, 0, 0, 0)),
    (0.78, 0.68, 0.38, (18, 78, 148, 46),  (0, 0, 0, 0)),
    (0.52, 0.82, 0.28, (148, 58, 18, 42),  (0, 0, 0, 0)),
    (0.38, 0.50, 0.42, (0, 118, 108, 38),  (0, 0, 0, 0)),   # cyan fly-through
]
# Nebula drift velocities (fraction of width per second)
_NEBULA_VX = [0.0008,  -0.0006, 0.0004, -0.0005]
_NEBULA_VY = [-0.0004,  0.0005, 0.0007,  0.0003]

# ── Fragment words ─────────────────────────────────────────────────────────
_WORDS = ["YOU", "HAVE", "ENTERED", "A", "NEW", "WORLD", "A", "NEW", "UNIVERSE"]

# ── Glyph asset path ──────────────────────────────────────────────────────
_GLYPH_DIR  = Path(__file__).resolve().parent.parent / "intro" / "assets" / "glyphs"
_GLYPH_FILES = [
    "glyph_hex.svg", "glyph_eye.svg", "glyph_sigma.svg",
    "glyph_diamond.svg", "glyph_arrow.svg", "glyph_cross.svg",
]

# ── Deep space void colour ────────────────────────────────────────────────
_VOID_COL = QColor(2, 4, 10)


# ══════════════════════════════════════════════════════════════════════════════
# Internal data holders
# ══════════════════════════════════════════════════════════════════════════════

class _Star:
    """One perspective-projected star in 3-D space."""
    __slots__ = ("wx", "wy", "z", "vz", "color", "base_r")

    def __init__(self, rng: random.Random) -> None:
        self.wx    = rng.uniform(-1.0, 1.0)
        self.wy    = rng.uniform(-1.0, 1.0)
        self.z     = rng.uniform(_Z_NEAR + 1, _Z_FAR)
        self.vz    = rng.uniform(0.5, 3.8)
        self.color = rng.choice(_STAR_PALETTE)
        self.base_r = rng.uniform(0.8, 2.2)

    def reset(self, rng: random.Random) -> None:
        self.wx    = rng.uniform(-1.0, 1.0)
        self.wy    = rng.uniform(-1.0, 1.0)
        self.z     = float(_Z_FAR)
        self.color = rng.choice(_STAR_PALETTE)
        self.base_r = rng.uniform(0.8, 2.2)


class _Glyph:
    """One tumbling Va'ruun SVG glyph."""
    __slots__ = (
        "renderer", "x", "y", "vx", "vy",
        "angle", "spin", "scale", "alpha",
        "target_alpha", "size",
    )

    def __init__(
        self,
        renderer: QSvgRenderer,
        x: float, y: float,
        vx: float, vy: float,
        spin: float, size: float,
    ) -> None:
        self.renderer    = renderer
        self.x           = x
        self.y           = y
        self.vx          = vx
        self.vy          = vy
        self.angle       = random.uniform(0.0, 360.0)
        self.spin        = spin
        self.scale       = 1.0
        self.alpha       = 0.0        # fades in
        self.target_alpha = 1.0
        self.size        = size


# ══════════════════════════════════════════════════════════════════════════════
class SpaceFlightWidget(QWidget):
    """
    Eight-phase Ancient Intelligence Awakening Sequence.

    Drop this into IntroPanelWidget after The Crossing video ends.
    Connect ``flight_finished`` to whatever follows (CarrierDeck etc.).

    Whispering Chambers:
    Soft phase-change whispers routed to TempleConsole.throne_speaks(text)
    if present on the parent; otherwise printed to stdout.
    """

    flight_finished = Signal()

    # ── Initialisation ───────────────────────────────────────────────────────

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # ── Timing ───────────────────────────────────────────────────────────
        self._elapsed:  float = 0.0
        self._phase:    int   = 0
        self._last_phase: int = -1
        self._finished: bool  = False

        # ── 3-D starfield ─────────────────────────────────────────────────────
        self._rng   = random.Random(20260705)
        self._stars = [_Star(self._rng) for _ in range(_N_STARS)]
        # Speed multiplier — ramps up over Phase 2
        self._star_speed: float = 0.0

        # ── Nebulae (drift offsets in fraction-of-width) ──────────────────────
        self._neb_ox = [0.0] * 4
        self._neb_oy = [0.0] * 4
        self._neb_alpha = 0.0   # 0 → 1 during Phase 2

        # ── Va'ruun glyphs ────────────────────────────────────────────────────
        self._glyphs: list[_Glyph] = []
        self._glyph_alpha: float   = 0.0    # master fade-in 0→1 Phase 3
        self._glyph_fade:  float   = 1.0    # master fade-out 1→0 Phase 5+
        self._load_glyphs()

        # ── Electric tendrils (Phase 4: glyph↔glyph) ──────────────────────
        self._tendrils_gg: list[ElectricTendril] = []

        # ── Stone fragments (Phase 5+) ─────────────────────────────────────
        self._fragments: list[AncientFragment] = [
            AncientFragment(word, i, seed=i * 997 + 42)
            for i, word in enumerate(_WORDS)
        ]
        self._frag_final: list[tuple[float, float]] = []   # computed on resize
        self._frag_launched: list[bool] = [False] * 9
        self._assembly_started: bool = False

        # ── Tendrils from glyph→fragment (Phase 6 lead-in) ────────────────
        self._tendrils_gf: list[ElectricTendril] = []

        # ── Inscription progress ────────────────────────────────────────────
        self._inscript_t: float = 0.0   # 0→1 across Phase 6

        # ── Scanline flicker ────────────────────────────────────────────────
        self._scan_alpha: float = 0.55   # starts heavy, eases down

        # ── Mouse position (for hover) ──────────────────────────────────────
        self._mx: float = -9999.0
        self._my: float = -9999.0

        # ── Timer — ~60 fps ────────────────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        # ── Skip shortcuts ─────────────────────────────────────────────────
        for key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Escape):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._skip)

    # ── Whispering Chambers helper ────────────────────────────────────────────

    def _whisper(self, text: str) -> None:
        """
        Send a soft whisper to TempleConsole.throne_speaks(text) if available,
        otherwise print to stdout. Never raises — whispers fail silently.
        """
        parent = self.parent()
        if parent is not None and hasattr(parent, "throne_speaks"):
            try:
                parent.throne_speaks(text)  # type: ignore[attr-defined]
            except Exception:
                print(f"[SpaceFlightWidget] whisper (fallback): {text}")
        else:
            print(f"[SpaceFlightWidget] whisper: {text}")

    # ── Asset loading ─────────────────────────────────────────────────────────

    def _load_glyphs(self) -> None:
        """Load SVG renderers; create _Glyph objects with random placement."""
        rng = random.Random(77)
        for i, fname in enumerate(_GLYPH_FILES):
            path = _GLYPH_DIR / fname
            if not path.exists():
                continue
            renderer = QSvgRenderer(str(path))
            size  = rng.uniform(52, 84)
            # Spread across 70 % of the screen area — actual px computed in _tick
            # We store fractional positions; convert to px in _tick / paintEvent
            x  = rng.uniform(0.12, 0.88)
            y  = rng.uniform(0.18, 0.72)
            vx = rng.uniform(-0.008, 0.008)
            vy = rng.uniform(-0.006, 0.006)
            sp = rng.uniform(-1.2, 1.2)
            self._glyphs.append(
                _Glyph(renderer, x, y, vx, vy, sp, size)
            )

    # ── Geometry helpers ──────────────────────────────────────────────────────

    def _ensure_final_positions(self) -> None:
        """Compute fragment ring positions once we know the widget size."""
        if self._frag_final:
            return
        w, h = self.width(), self.height()
        if w < 2 or h < 2:
            return
        cx, cy = w / 2.0, h / 2.0
        n   = len(_WORDS)
        rng = random.Random(999)
        positions: list[tuple[float, float]] = []
        for i in range(n):
            t   = (i / (n - 1)) - 0.5           # -0.5 … +0.5
            # Gentle catenary-like arc
            x   = cx + t * w * 0.74
            arc = cy * 0.08 * (1.0 - (2 * t) ** 2)   # bows upward at centre
            y   = cy + arc + rng.uniform(-22, 22)
            positions.append((x, y))
        self._frag_final = positions

    def _spawn_pos(self, i: int) -> tuple[float, float]:
        """Off-screen spawn point for fragment i."""
        w, h  = self.width(), self.height()
        rng   = random.Random(i * 13 + 5)
        edge  = rng.randint(0, 3)
        if edge == 0:
            return rng.uniform(0, w), -160.0           # top
        if edge == 1:
            return rng.uniform(0, w), h + 160.0        # bottom
        if edge == 2:
            return -160.0, rng.uniform(0, h)           # left
        return w + 160.0, rng.uniform(0, h)            # right

    # ── Main tick ─────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        dt = 0.016    # 16 ms
        self._elapsed += dt
        t = self._elapsed

        phase = 0
        for p, end in enumerate(_PHASE_ENDS):
            if t <= end:
                phase = p
                break
        else:
            phase = 7
        self._phase = phase

        # Whisper on phase transitions (Whispering Chambers)
        if phase != self._last_phase:
            if phase == 1:
                self._whisper("In the void, a single heartbeat remembers you.")
            elif phase == 2:
                self._whisper("Stars awaken — the chamber opens its eyes.")
            elif phase == 5:
                self._whisper("Fragments gather; a new sentence of the universe is being written.")
            elif phase == 7:
                self._whisper("The message is complete. The ancient intelligence is listening.")
            self._last_phase = phase

        # ── Phase 2: advance starfield + nebula ────────────────────────────
        if phase >= 2:
            ph2_frac = min(1.0, (t - _T_BREATH) / 8.0)
            self._star_speed  = 0.35 + ph2_frac * 1.8
            self._neb_alpha   = min(1.0, ph2_frac * 1.4)
            self._scan_alpha  = max(0.04, 0.55 - ph2_frac * 0.51)

            for star in self._stars:
                star.z -= star.vz * self._star_speed
                if star.z < _Z_NEAR:
                    star.reset(self._rng)

            # Nebula drift
            for k in range(4):
                self._neb_ox[k] += _NEBULA_VX[k] * dt
                self._neb_oy[k] += _NEBULA_VY[k] * dt

        # ── Phase 3: glyph tumble ──────────────────────────────────────────
        if phase == 3:
            ph3_frac = min(1.0, (t - _T_AWAKENING) / 2.5)
            self._glyph_alpha = ph3_frac
        elif phase >= 4:
            self._glyph_alpha = 1.0

        if phase == 5:
            self._glyph_fade = max(0.0, 1.0 - (t - _T_RECOGN) / 1.8)
        elif phase >= 6:
            self._glyph_fade = 0.0

        for g in self._glyphs:
            w, h = self.width(), self.height()
            g.x += g.vx * dt
            g.y += g.vy * dt
            # Bounce gently within [0.05, 0.95]
            if not 0.05 < g.x < 0.95:
                g.vx = -g.vx
            if not 0.05 < g.y < 0.95:
                g.vy = -g.vy
            if phase <= 4:
                g.angle = (g.angle + g.spin) % 360.0

        # ── Phase 4: spawn / update glyph↔glyph tendrils ──────────────────
        if phase == 4 and not self._tendrils_gg:
            self._build_glyph_tendrils()

        # ── Phase 5: launch fragments one by one ─────────────────────────
        if phase == 5:
            self._ensure_final_positions()
            ph5_frac = (t - _T_RECOGN) / 6.0
            for i, frag in enumerate(self._fragments):
                launch_frac = i / (len(self._fragments) - 1)
                if ph5_frac >= launch_frac * 0.6 and not self._frag_launched[i]:
                    if self._frag_final:
                        sx, sy = self._spawn_pos(i)
                        tx, ty = self._frag_final[i]
                        frag.place(sx, sy, tx, ty)
                        frag.begin_drift()
                        self._frag_launched[i] = True

        # Transition drifting → orbiting after 1 second
        if phase >= 5:
            for frag in self._fragments:
                if frag.state == AncientFragment.DRIFTING and frag._state_t > 1.0:
                    frag.begin_orbit()

        # ── Phase 6: inscription ───────────────────────────────────────────
        if phase == 6:
            self._inscript_t = min(1.0, (t - _T_ASSEMBLY) / 4.0)
            for i, frag in enumerate(self._fragments):
                frag.inscription = min(1.0, self._inscript_t * len(_WORDS) - i) if self._inscript_t > 0 else 0.0
                # Clamp
                frag.inscription = max(0.0, min(1.0, frag.inscription))

        # ── Phase 7: everything stills — emit finished when done ──────────
        if phase == 7:
            self._inscript_t = 1.0
            for frag in self._fragments:
                frag.inscription = 1.0
            if not self._finished and t >= _T_REVEAL:
                self._finished = True
                self.flight_finished.emit()

        # ── Update all fragment state machines ─────────────────────────────
        if phase >= 5:
            for frag in self._fragments:
                frag.update(t)

        self.update()   # schedule repaint

    # ── Tendril builders ──────────────────────────────────────────────────────

    def _build_glyph_tendrils(self) -> None:
        """Create ElectricTendril between adjacent glyphs."""
        n = len(self._glyphs)
        for i in range(n - 1):
            g1 = self._glyphs[i]
            g2 = self._glyphs[(i + 1) % n]
            w, h = self.width(), self.height()
            start = (g1.x * w, g1.y * h)
            end   = (g2.x * w, g2.y * h)
            self._tendrils_gg.append(
                ElectricTendril(start, end, n_branches=3, seed=i * 71 + 13)
            )

    # ── Skip ──────────────────────────────────────────────────────────────────

    def _skip(self) -> None:
        if not self._finished:
            self._finished = True
            self._elapsed  = _T_REVEAL + 0.1
            for frag in self._fragments:
                frag.inscription = 1.0
            self._whisper("The sequence was skipped — the chamber closes its eyes gently.")
            self.flight_finished.emit()

    # ── Mouse hover ───────────────────────────────────────────────────────────

    def mouseMoveEvent(self, event) -> None:
        self._mx = float(event.position().x())
        self._my = float(event.position().y())
        super().mouseMoveEvent(event)

    def _update_hover(self) -> None:
        """Only active during Phase 7 (REVELATION) after fragments settled."""
        if self._phase < 7:
            return
        hovered_idx = -1
        for i, frag in enumerate(self._fragments):
            if frag.hit_test(self._mx, self._my):
                hovered_idx = i
                break
        for i, frag in enumerate(self._fragments):
            if i == hovered_idx:
                if not frag.is_selected:
                    frag.select()
            else:
                if frag.is_selected:
                    frag.deselect()
                    frag.dim()
                elif frag.state == AncientFragment.SETTLED and hovered_idx >= 0:
                    frag.dim()
                elif frag.state == AncientFragment.DIMMED and hovered_idx < 0:
                    frag.undim()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        t     = self._elapsed
        phase = self._phase
        w, h  = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0

        # 0. Deep space background
        painter.fillRect(self.rect(), _VOID_COL)

        # 1. BREATH — heartbeat pinpoint
        if phase == 1:
            self._paint_breath(painter, cx, cy, t)

        # 2+. Stars and nebulae
        if phase >= 2:
            self._paint_nebulae(painter, w, h, t)
            self._paint_stars(painter, cx, cy, t)

        # 3+. Glyphs
        if phase >= 3:
            self._paint_glyphs(painter, w, h, t)

        # 4. Glyph↔glyph tendrils
        if phase == 4:
            ph4_frac = min(1.0, (t - _T_WANDERING) / 1.5)
            for tendril in self._tendrils_gg:
                w2, h2 = self.width(), self.height()
                # keep endpoints live
                tendril.draw(painter, t, ph4_frac)

        # 5+. Fragments
        if phase >= 5:
            self._update_hover()
            for frag in self._fragments:
                frag.draw(painter, t)

        # Scanline flicker
        if self._scan_alpha > 0.01:
            self._paint_scanlines(painter, w, h)

        painter.end()

    # ── Sub-painters ──────────────────────────────────────────────────────────

    def _paint_breath(self, painter: QPainter, cx: float, cy: float, t: float) -> None:
        """
        Heartbeat pulse — fast double-beat then silence.
        Period ≈ 1.1 s, two quick peaks separated by 0.22 s.
        """
        period = 1.1
        tp = (t - _T_VOID) % period
        # First beat: ramp up/down in 0.18 s
        b1 = max(0.0, 1.0 - abs(tp - 0.10) / 0.10)
        # Second beat: slightly softer
        b2 = max(0.0, 0.78 * (1.0 - abs(tp - 0.32) / 0.10))
        pulse = max(b1, b2)

        if pulse < 0.005:
            return

        radius = 2.0 + pulse * 28.0
        grad   = QRadialGradient(QPointF(cx, cy), radius)
        grad.setColorAt(0.0, QColor(255, 240, 210, int(240 * pulse)))
        grad.setColorAt(0.4, QColor(200, 180, 120, int(130 * pulse)))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _paint_nebulae(self, painter: QPainter, w: int, h: int, t: float) -> None:
        painter.save()
        painter.setOpacity(self._neb_alpha)
        for k, (cfx, cfy, rfrac, inner, outer) in enumerate(_NEBULA_DEFS):
            ox  = self._neb_ox[k]
            oy  = self._neb_oy[k]
            px  = (cfx + ox) * w
            py  = (cfy + oy) * h
            rad = rfrac * w
            grad = QRadialGradient(QPointF(px, py), rad)
            ri, gi, bi, ai = inner
            ro, go, bo, ao = outer
            grad.setColorAt(0.0, QColor(ri, gi, bi, ai))
            grad.setColorAt(1.0, QColor(ro, go, bo, ao))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), rad, rad)
        painter.restore()

    def _paint_stars(self, painter: QPainter, cx: float, cy: float, t: float) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        ph2_frac = min(1.0, (self._elapsed - _T_BREATH) / 8.0)
        for star in self._stars:
            sx = cx + _FOCAL * (star.wx * cx * 0.9) / star.z
            sy = cy + _FOCAL * (star.wy * cy * 0.9) / star.z
            # Size grows as z decreases
            r  = star.base_r * (_FOCAL / star.z)
            r  = max(0.5, min(r, 6.0))
            # Brightness proportional to proximity
            bright = min(1.0, _FOCAL / star.z * 0.65)
            c = star.color
            painter.setBrush(
                QColor(c.red(), c.green(), c.blue(), int(200 * bright * ph2_frac))
            )
            painter.drawEllipse(QPointF(sx, sy), r, r)

    def _paint_glyphs(self, painter: QPainter, w: int, h: int, t: float) -> None:
        effective_alpha = self._glyph_alpha * self._glyph_fade
        if effective_alpha < 0.01:
            return

        cobalt = QColor(59, 120, 231)   # #3B78E7

        for g in self._glyphs:
            px = g.x * w
            py = g.y * h
            sz = g.size

            painter.save()
            painter.translate(px, py)
            painter.rotate(g.angle)
            painter.setOpacity(effective_alpha * 0.82)

            # Render SVG into a rect; tint cyan-cobalt via CompositionMode
            rect = QRectF(-sz / 2, -sz / 2, sz, sz)

            # Two-pass: glow halo first
            painter.setBrush(QBrush(QColor(cobalt.red(), cobalt.green(),
                                          cobalt.blue(), 35)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect.adjusted(-8, -8, 8, 8))

            g.renderer.render(painter, rect)
            painter.restore()

    def _paint_scanlines(self, painter: QPainter, w: int, h: int) -> None:
        painter.save()
        painter.setOpacity(self._scan_alpha)
        col = QColor(0, 0, 0, 70)
        painter.fillRect(0, 0, w, h, _VOID_COL)   # don't double-fill; skip
        painter.setPen(QPen(col, 1.0))
        y = 0
        while y < h:
            painter.drawLine(0, y, w, y)
            y += 4
        painter.restore()

    # ── Resize ────────────────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        # Invalidate cached positions so they recompute at new size
        self._frag_final = []
        super().resizeEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
# Standalone test harness
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    win = SpaceFlightWidget()
    win.setWindowTitle("SIG — Ancient Intelligence Awakening (standalone test)")
    win.resize(1280, 720)
    win.show()
    win.raise_()

    # Print a confirmation when the sequence finishes
    win.flight_finished.connect(
        lambda: print("[SpaceFlightWidget] flight_finished emitted — sequence complete.")
    )

    sys.exit(app.exec())
