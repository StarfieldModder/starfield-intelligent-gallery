
r"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      S P A C E _ F L I G H T _ W I D G E T . P Y     ║
║        ██╔════╝ ██║ ██╔════╝      Ancient Intelligence Awakening Sequence         ║
║        ███████╗ ██║ ██║  ███╗      — 8‑Phase Orchestrator                         ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery                   ║
║        ███████║ ██║ ╚██████╔╝                                                     ║
║        ╚══════╝ ╚═╝  ╚═════╝      "Stars remember you. Fragments speak your name."║
╠═══════════════════════════════════════════════════════════════════════════════════╣
"""

from __future__ import annotations

from .starfield_intelligent_entrance import StarfieldEntrance

import math
import random
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    Qt, QPointF, QRectF, QTimer, Signal,
)
from PySide6.QtGui import (
    QColor, QFont, QKeySequence,
    QPainter, QPainterPath,
    QShortcut,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget, QApplication, QLabel

try:
    from .ancient_fragment import AncientFragment
    from .electric_tendril  import ElectricTendril
except ImportError:
    from ancient_fragment import AncientFragment   # type: ignore
    from electric_tendril  import ElectricTendril  # type: ignore

# ─────────────────────────────────────────────────────────────────────────────
# Director’s Cut: Controlled Randomness
# Nebula strength is now fully cinematic — no slider, no UI, no N-key toggle.
# Variation is allowed, chaos is not.
# ─────────────────────────────────────────────────────────────────────────────

def _dc_rand(low: float, high: float) -> float:
    """Director’s Cut bounded randomness — stable, cinematic, intentional."""
    return random.uniform(low, high)

# ─────────────────────────────────────────────────────────────────────────────
# Phase timing (cumulative seconds)
# ─────────────────────────────────────────────────────────────────────────────

_T_VOID      = 0.0
_T_BREATH    = _T_VOID      + 2.5
_T_AWAKENING = _T_BREATH    + 8.0
_T_WANDERING = _T_AWAKENING + 6.0
_T_RECOGN    = _T_WANDERING + 5.0
_T_ASSEMBLY  = _T_RECOGN    + 6.0
_T_INSCRIPT  = _T_ASSEMBLY  + 4.0
_T_REVEAL    = _T_INSCRIPT  + 2.5

_PHASE_ENDS = [
    _T_VOID, _T_BREATH, _T_AWAKENING, _T_WANDERING,
    _T_RECOGN, _T_ASSEMBLY, _T_INSCRIPT, _T_REVEAL,
]

# ─────────────────────────────────────────────────────────────────────────────
# Fragment Words
# ─────────────────────────────────────────────────────────────────────────────

_WORDS = ["YOU", "HAVE", "ENTERED", "A", "NEW", "WORLD", "A", "NEW", "UNIVERSE"]

# ─────────────────────────────────────────────────────────────────────────────
# Glyph Assets
# ─────────────────────────────────────────────────────────────────────────────

_GLYPH_DIR  = Path(__file__).resolve().parent.parent / "intro" / "assets" / "glyphs"
_GLYPH_FILES = [
    "glyph_hex.svg", "glyph_eye.svg", "glyph_sigma.svg",
    "glyph_diamond.svg", "glyph_arrow.svg", "glyph_cross.svg",
]

_VOID_COL = QColor(2, 4, 10)

# ─────────────────────────────────────────────────────────────────────────────
# Glyph (Va’ruun tumbling SVG)
# ─────────────────────────────────────────────────────────────────────────────

class _Glyph:
    """One tumbling Va’ruun SVG glyph."""
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
        self.renderer     = renderer
        self.x            = x
        self.y            = y
        self.vx           = vx
        self.vy           = vy
        self.angle        = random.uniform(0.0, 360.0)
        self.spin         = spin
        self.scale        = 1.0
        self.alpha        = 0.0
        self.target_alpha = 1.0
        self.size         = size


# ══════════════════════════════════════════════════════════════════════════════
# SpaceFlightWidget — Ancient Intelligence Awakening Sequence
# ══════════════════════════════════════════════════════════════════════════════

class SpaceFlightWidget(QWidget):
    """
    Eight-phase Ancient Intelligence Awakening Sequence.

    Drop this into IntroPanelWidget after The Crossing video ends.
    Connect ``flight_finished`` to whatever follows (CarrierDeck etc.).
    """

    flight_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # ────────────────────────────────────────────────────────────────────
        # Director’s Cut: No slider, no N-key, pure cinematic control
        # ────────────────────────────────────────────────────────────────────

        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Timing
        self._elapsed: float = 0.0
        self._phase: int = 0
        self._last_phase: int = -1
        self._finished: bool = False

        # Random generator (stable seed for cinematic consistency)
        self._rng = random.Random(20260712)

        # ────────────────────────────────────────────────────────────────────
        # NEW Starfield Subsystem (your first original SIG module!)
        # ────────────────────────────────────────────────────────────────────

        self._starfield = StarfieldEntrance()
        self._starfield.reset_bloom()


        # ────────────────────────────────────────────────────────────────────
        # Glyphs
        # ────────────────────────────────────────────────────────────────────

        self._glyphs: list[_Glyph] = []
        self._glyph_alpha: float = 0.0
        self._glyph_fade: float = 1.0
        self._load_glyphs()

        # Tendrils (glyph ↔ glyph)
        self._tendrils_gg: list[ElectricTendril] = []

        # ────────────────────────────────────────────────────────────────────
        # Fragments (Va’ruun stone words)
        # ────────────────────────────────────────────────────────────────────

        self._fragments: list[AncientFragment] = [
            AncientFragment(word, i, seed=i * 997 + 42)
            for i, word in enumerate(_WORDS)
        ]

        self._frag_final: list[tuple[float, float]] = []
        self._frag_launched: list[bool] = [False] * len(self._fragments)
        self._assembly_started: bool = False

        # Tendrils (glyph → fragment)
        self._tendrils_gf: list[ElectricTendril] = []

        # Inscription progress
        self._inscript_t: float = 0.0

        # Scanline flicker
        self._scan_alpha: float = 0.55

        # Mouse hover
        self._mx: float = -9999.0
        self._my: float = -9999.0

        # ────────────────────────────────────────────────────────────────────
        # Timer — 60 fps
        # ────────────────────────────────────────────────────────────────────

        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        # ────────────────────────────────────────────────────────────────────
        # Skip shortcuts — Space / Enter / Escape
        # (No N-key, no nebula slider — Director’s Cut)
        # ────────────────────────────────────────────────────────────────────

        for key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Escape):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._skip)

    # ----------------------------------------------------------------------
    # Public helper: start / show the flight sequence
    # ----------------------------------------------------------------------
    def show_flight(self) -> None:
        """
        Make the SpaceFlightWidget visible and ensure the sequence runs
        from the beginning. This mirrors the expectation in sig_launcher.py.

        NOTE: starts the sequence at AWAKENING so the starfield appears
        immediately after the intro hands off.
        """
        try:
            # Start at BREATH→AWAKENING boundary
            self._elapsed = _T_BREATH
            self._phase = 2
            self._last_phase = -1
            self._finished = False

            # Reset starfield activation so bloom restarts
            self._active_stars = 1
            for i, s in enumerate(self._stars):
                s.z = float(_Z_FAR)
                s.wx = 0.0
                s.wy = 0.0
                s.vz = self._rng.uniform(0.2, 0.6) if i == 0 else self._rng.uniform(0.1, 0.3)

            # Reset glyph/fragment state defensively
            try:
                self._glyph_alpha = 0.0
                self._glyph_fade = 1.0
                self._inscript_t = 0.0
                self._frag_launched = [False] * len(self._frag_launched)
            except Exception:
                pass

            # Ensure the timer is running
            if not self._timer.isActive():
                self._timer.start()

            # Show fullscreen and take focus so key events (ESC) are caught
            self.showFullScreen()
            self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

            print("[SpaceFlightWidget] show_flight() invoked — sequence starting at AWAKENING.")
        except Exception as exc:
            print(f"[SpaceFlightWidget] show_flight() failed: {exc}")

    # ───────────────────────────────────────────────────────────────────────
    # Whispering Chambers helper
    # ───────────────────────────────────────────────────────────────────────

    def _whisper(self, text: str) -> None:
        parent = self.parent()
        if parent is not None and hasattr(parent, "throne_speaks"):
            try:
                parent.throne_speaks(text)  # type: ignore[attr-defined]
            except Exception:
                print(f"[SpaceFlightWidget] whisper (fallback): {text}")
        else:
            print(f"[SpaceFlightWidget] whisper: {text}")

    # ───────────────────────────────────────────────────────────────────────
    # Asset loading — Va’ruun glyphs
    # ───────────────────────────────────────────────────────────────────────

    def _load_glyphs(self) -> None:
        rng = random.Random(77)
        for i, fname in enumerate(_GLYPH_FILES):
            path = _GLYPH_DIR / fname
            if not path.exists():
                continue
            renderer = QSvgRenderer(str(path))
            size  = rng.uniform(52, 84)
            x  = rng.uniform(0.12, 0.88)
            y  = rng.uniform(0.18, 0.72)
            vx = rng.uniform(-0.008, 0.008)
            vy = rng.uniform(-0.006, 0.006)
            sp = rng.uniform(-1.2, 1.2)
            self._glyphs.append(
                _Glyph(renderer, x, y, vx, vy, sp, size)
            )

    # ───────────────────────────────────────────────────────────────────────
    # Geometry helpers — fragment final positions + spawn positions
    # ───────────────────────────────────────────────────────────────────────

    def _ensure_final_positions(self) -> None:
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
            t   = (i / (n - 1)) - 0.5
            x   = cx + t * w * 0.74
            arc = cy * 0.08 * (1.0 - (2 * t) ** 2)
            y   = cy + arc + rng.uniform(-22, 22)
            positions.append((x, y))
        self._frag_final = positions

    def _spawn_pos(self, i: int) -> tuple[float, float]:
        w, h  = self.width(), self.height()
        rng   = random.Random(i * 13 + 5)
        edge  = rng.randint(0, 3)
        if edge == 0:
            return rng.uniform(0, w), -160.0
        if edge == 1:
            return rng.uniform(0, w), h + 160.0
        if edge == 2:
            return -160.0, rng.uniform(0, h)
        return w + 160.0, rng.uniform(0, h)
    # ───────────────────────────────────────────────────────────────────────
    # Main tick — phase machine + motion
    # ───────────────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if self._finished:
            return

        dt = 0.016
        self._elapsed += dt
        t = self._elapsed

        # Phase selection
        phase = self._phase
        for i, end_t in enumerate(_PHASE_ENDS):
            if t < end_t:
                phase = i
                break
        else:
            phase = 7
        self._phase = phase

        # Whisper on phase transitions (Whispering Chambers)
        if phase != self._last_phase:
            try:
                print(f"[SpaceFlightWidget] Phase transition: {self._last_phase} -> {phase} at t={t:.3f}s")
            except Exception:
                pass
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
            phase2_fraction = min(1.0, max(0.0, (t - _T_BREATH) / 8.0))
            self._starfield.advance(dt, phase2_fraction)

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

    # ───────────────────────────────────────────────────────────────────────
    # Tendril builders
    # ───────────────────────────────────────────────────────────────────────

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

    # ───────────────────────────────────────────────────────────────────────
    # Skip — Space / Enter / Escape
    # ───────────────────────────────────────────────────────────────────────

    def _skip(self) -> None:
        if not self._finished:
            self._finished = True
            self._elapsed  = _T_REVEAL + 0.1
            for frag in self._fragments:
                frag.inscription = 1.0
            self._whisper("The sequence was skipped — the chamber closes its eyes gently.")
            self.flight_finished.emit()

    # ───────────────────────────────────────────────────────────────────────
    # Mouse hover — only active during Phase 7 (REVELATION)
    # ───────────────────────────────────────────────────────────────────────

    def mouseMoveEvent(self, event) -> None:
        self._mx = float(event.position().x())
        self._my = float(event.position().y())
        super().mouseMoveEvent(event)

    def _update_hover(self) -> None:
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

    # ───────────────────────────────────────────────────────────────────────
    # PaintEvent — full cinematic chain
    # ───────────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        t     = self._elapsed
        phase = self._phase
        w, h  = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0

        painter.fillRect(self.rect(), _VOID_COL)

        if phase == 1:
            self._paint_breath(painter, cx, cy, t)


        if phase >= 3:
            self._paint_glyphs(painter, w, h, t)

        if phase == 4:
            ph4_frac = min(1.0, (t - _T_WANDERING) / 1.5)
            for tendril in self._tendrils_gg:
                tendril.draw(painter, t, ph4_frac)

        if phase >= 5:
            self._update_hover()
            for frag in self._fragments:
                frag.draw(painter, t)

        if self._scan_alpha > 0.01:
            self._paint_scanlines(painter, w, h)

        painter.end()

    # ───────────────────────────────────────────────────────────────────────
    # Sub‑painters
    # ───────────────────────────────────────────────────────────────────────

    def _paint_breath(self, painter: QPainter, cx: float, cy: float, t: float) -> None:
        period = 1.1
        tp = (t - _T_VOID) % period
        b1 = max(0.0, 1.0 - abs(tp - 0.10) / 0.10)
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


    def _paint_glyphs(self, painter: QPainter, w: int, h: int, t: float) -> None:
        effective_alpha = self._glyph_alpha * self._glyph_fade
        if effective_alpha < 0.01:
            return
        cobalt = QColor(59, 120, 231)
        for g in self._glyphs:
            px = g.x * w
            py = g.y * h
            sz = g.size
            painter.save()
            painter.translate(px, py)
            painter.rotate(g.angle)
            painter.setOpacity(effective_alpha * 0.82)
            rect = QRectF(-sz / 2, -sz / 2, sz, sz)
            painter.setBrush(QBrush(QColor(cobalt.red(), cobalt.green(), cobalt.blue(), 35)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect.adjusted(-8, -8, 8, 8))
            g.renderer.render(painter, rect)
            painter.restore()

    def _paint_scanlines(self, painter: QPainter, w: int, h: int) -> None:
        painter.save()
        painter.setOpacity(self._scan_alpha)
        col = QColor(0, 0, 0, 70)
        painter.fillRect(0, 0, w, h, _VOID_COL)
        painter.setPen(QPen(col, 1.0))
        y = 0
        while y < h:
            painter.drawLine(0, y, w, y)
            y += 4
        painter.restore()

    def resizeEvent(self, event) -> None:
        self._frag_final = []
        self._ensure_final_positions()
        super().resizeEvent(event)
