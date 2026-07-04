# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║         C A R R I E R   D E C K                             ║
# ║         Starfield Intelligent Gallery                        ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  carrier_deck.py                                ║
# ║  Location  :  C:\SIG\ui\carrier_deck.py                      ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)      ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator)║
# ║  Version   :  2026.07.02 — Unicode-Safe Edition              ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  WHAT THIS FILE IS                                           ║
# ║                                                              ║
# ║  The Carrier Deck — five sovereign panels that materialise   ║
# ║  from particle clouds after The Crossing intro completes.    ║
# ║                                                              ║
# ║  Each panel begins as a swarm of scattered light-points.     ║
# ║  Over ~1.8 seconds they condense, solidify, and glow —       ║
# ║  like constellations forming from raw starlight.             ║
# ║                                                              ║
# ║  PANELS (left to right)                                      ║
# ║    1  Journey       — Cobalt blue                            ║
# ║    2  Archive       — Violet                                 ║
# ║    3  Artifacts     — Gold                                   ║
# ║    4  Companions    — Teal                                   ║
# ║    5  Cosmic Choice — White-Silver  (rises 1.2 s last)       ║
# ║                                                              ║
# ║  SIGNALS                                                     ║
# ║    CarrierDeck.panel_selected(int)  — 1..5                   ║
# ║                                                              ║
# ║  PUBLIC METHODS                                              ║
# ║    begin_materialize()  — starts sequential panel appear     ║
# ║    stop_all()           — stops all timers (on close)        ║
# ║                                                              ║
# ║  FIX LOG                                                     ║
# ║  2026.07.02 — Header converted from triple-quote docstring   ║
# ║               to # comments — eliminates unicode escape      ║
# ║               SyntaxError on Python 3.13 (backslash in       ║
# ║               Windows paths inside \"\"\" strings)           ║
# ╚══════════════════════════════════════════════════════════════╝
# ================================================================

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from typing import List

from PySide6.QtCore    import (Property, QEasingCurve, QPointF,
                                QPropertyAnimation, QRectF, Qt,
                                QTimer, Signal)
from PySide6.QtGui     import (QColor, QFont, QLinearGradient,
                                QPainter, QPainterPath, QPen,
                                QRadialGradient)
from PySide6.QtWidgets import (QApplication, QHBoxLayout,
                                QSizePolicy, QVBoxLayout, QWidget)

# ActiveRandomNebula — graceful fallback if not yet present
try:
    from ui.active_random_nebula import ActiveRandomNebula
    _NEBULA_AVAILABLE = True
except ImportError:
    _NEBULA_AVAILABLE = False
    print("[CarrierDeck]  ActiveRandomNebula not found — deck runs without nebula overlay.")


# ──────────────────────────────────────────────────────────────────────────────
#  Panel definitions
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PanelDef:
    panel_id : int
    name     : str
    subtitle : str
    color    : QColor       # dominant glow
    accent   : QColor       # arc / border accent
    delay_ms : int          # ms after begin_materialize() before this panel starts


PANEL_DEFS: List[PanelDef] = [
    PanelDef(
        panel_id = 1,
        name     = "JOURNEY",
        subtitle = "Exploration & Discovery",
        color    = QColor(30,  90, 200),   # cobalt blue
        accent   = QColor(80, 160, 255),
        delay_ms = 0,
    ),
    PanelDef(
        panel_id = 2,
        name     = "ARCHIVE",
        subtitle = "Memory & Knowledge",
        color    = QColor(110, 30, 180),   # violet
        accent   = QColor(180, 80, 255),
        delay_ms = 300,
    ),
    PanelDef(
        panel_id = 3,
        name     = "ARTIFACTS",
        subtitle = "Relics & Revelation",
        color    = QColor(180, 130,  20),  # gold
        accent   = QColor(255, 200,  60),
        delay_ms = 600,
    ),
    PanelDef(
        panel_id = 4,
        name     = "COMPANIONS",
        subtitle = "Relationships & Crew",
        color    = QColor(20, 140, 140),   # teal
        accent   = QColor(60, 220, 220),
        delay_ms = 900,
    ),
    PanelDef(
        panel_id = 5,
        name     = "COSMIC CHOICE",
        subtitle = "The Threshold Awaits",
        color    = QColor(160, 175, 200),  # white-silver
        accent   = QColor(220, 230, 255),
        delay_ms = 1200,                   # rises last
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
#  Particle  (internal data class)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Particle:
    x   : float
    y   : float
    tx  : float   # target x (inside panel bounds)
    ty  : float   # target y (inside panel bounds)
    vx  : float = field(default=0.0)
    vy  : float = field(default=0.0)
    age : float = field(default=0.0)    # 0..1 (0=born, 1=arrived)
    r   : float = field(default=2.0)    # radius


# ──────────────────────────────────────────────────────────────────────────────
#  CelestialPanel
# ──────────────────────────────────────────────────────────────────────────────

class CelestialPanel(QWidget):
    """
    One of the five sovereign panels.
    Materialises from a particle cloud, then breathes and glows.
    """

    clicked = Signal(int)    # emits panel_id when user clicks

    # Animation phases
    _PHASE_IDLE      = 0
    _PHASE_PARTICLES = 1
    _PHASE_SOLIDIFY  = 2
    _PHASE_ALIVE     = 3

    _PARTICLE_COUNT  = 80
    _PARTICLE_FPS    = 40
    _SOLIDIFY_MS     = 1_800
    _BREATH_PERIOD   = 3_000   # ms for one full breath cycle

    def __init__(self, defn: PanelDef, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._defn      = defn
        self._phase     = self._PHASE_IDLE
        self._particles : List[Particle] = []
        self._opacity   = 0.0         # 0..1 solid panel opacity
        self._breath    = 0.0         # 0..1 breath sine value
        self._hovered   = False
        self._arc_angle = 0.0         # rotating arc decoration

        self.setMinimumSize(200, 380)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # Particle / breath timer
        self._timer = QTimer(self)
        self._timer.setInterval(1000 // self._PARTICLE_FPS)
        self._timer.timeout.connect(self._tick)

        # Solidify timer
        self._solidify_timer = QTimer(self)
        self._solidify_timer.setInterval(16)
        self._solidify_elapsed = 0
        self._solidify_timer.timeout.connect(self._solidify_tick)

        # Breath timer (fires only in ALIVE phase)
        self._breath_elapsed = random.randint(0, self._BREATH_PERIOD)

    # ── Public ────────────────────────────────────────────────────────────────

    def start_materialize(self) -> None:
        """Kick off the particle cloud → solid panel animation."""
        self._phase = self._PHASE_PARTICLES
        self._spawn_particles()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self._solidify_timer.stop()

    # ── Internal animation ────────────────────────────────────────────────────

    def _spawn_particles(self) -> None:
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        scatter = max(w, h) * 1.4
        self._particles.clear()
        for _ in range(self._PARTICLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            dist  = random.uniform(scatter * 0.4, scatter)
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            tx = random.uniform(20, w - 20)
            ty = random.uniform(20, h - 20)
            r  = random.uniform(1.5, 3.5)
            self._particles.append(Particle(px, py, tx, ty, r=r))

    def _tick(self) -> None:
        dt = 1.0 / self._PARTICLE_FPS

        if self._phase == self._PHASE_PARTICLES:
            done = True
            for p in self._particles:
                p.age = min(1.0, p.age + dt / 1.2)
                ease = p.age * p.age * (3.0 - 2.0 * p.age)   # smoothstep
                p.x = p.x + (p.tx - p.x) * 0.06
                p.y = p.y + (p.ty - p.y) * 0.06
                if abs(p.x - p.tx) > 2 or abs(p.y - p.ty) > 2:
                    done = False
            if done:
                self._phase = self._PHASE_SOLIDIFY
                self._solidify_elapsed = 0
                self._solidify_timer.start()

        elif self._phase == self._PHASE_ALIVE:
            self._breath_elapsed += 1000 / self._PARTICLE_FPS
            t = (self._breath_elapsed % self._BREATH_PERIOD) / self._BREATH_PERIOD
            self._breath = (math.sin(2 * math.pi * t) + 1) / 2
            self._arc_angle = (self._arc_angle + 0.3) % 360

        self.update()

    def _solidify_tick(self) -> None:
        self._solidify_elapsed += 16
        self._opacity = min(1.0, self._solidify_elapsed / self._SOLIDIFY_MS)
        if self._opacity >= 1.0:
            self._solidify_timer.stop()
            self._phase = self._PHASE_ALIVE
        self.update()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Draw particles
        if self._phase in (self._PHASE_PARTICLES, self._PHASE_SOLIDIFY):
            self._draw_particles(p, w, h)

        # Draw solid panel (fades in during SOLIDIFY, full in ALIVE)
        if self._phase in (self._PHASE_SOLIDIFY, self._PHASE_ALIVE):
            p.setOpacity(self._opacity)
            self._draw_panel(p, w, h)
            p.setOpacity(1.0)

        p.end()

    def _draw_particles(self, p: QPainter, w: int, h: int) -> None:
        c = self._defn.color
        for pt in self._particles:
            alpha = int(180 * pt.age + 40)
            col = QColor(c.red(), c.green(), c.blue(), min(255, alpha))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(col)
            p.drawEllipse(QPointF(pt.x, pt.y), pt.r, pt.r)

    def _draw_panel(self, p: QPainter, w: int, h: int) -> None:
        c     = self._defn.color
        acc   = self._defn.accent
        rect  = QRectF(8, 8, w - 16, h - 16)
        hover_boost = 0.25 if self._hovered else 0.0
        breath_val  = self._breath * 0.12 + hover_boost

        # Background gradient
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), int(60  + breath_val * 60)))
        grad.setColorAt(0.5, QColor(c.red(), c.green(), c.blue(), int(30  + breath_val * 30)))
        grad.setColorAt(1.0, QColor(8, 10, 18, 200))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 12, 12)

        # Border glow
        glow_alpha = int(160 + breath_val * 95)
        pen = QPen(QColor(acc.red(), acc.green(), acc.blue(), glow_alpha), 2.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 12, 12)

        # Rotating arc decoration (top-right corner)
        arc_rect = QRectF(w - 56, 12, 44, 44)
        arc_pen  = QPen(QColor(acc.red(), acc.green(), acc.blue(), 100), 1.5)
        arc_pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(arc_pen)
        p.drawArc(arc_rect, int(self._arc_angle * 16), 240 * 16)

        # Panel name
        name_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        name_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        p.setFont(name_font)
        p.setPen(QColor(acc.red(), acc.green(), acc.blue(), 240))
        p.drawText(QRectF(16, h * 0.48, w - 32, 32),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._defn.name)

        # Subtitle
        sub_font = QFont("Segoe UI", 9, QFont.Weight.Thin)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        p.setFont(sub_font)
        p.setPen(QColor(200, 215, 240, 160))
        p.drawText(QRectF(16, h * 0.58, w - 32, 28),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._defn.subtitle)

        # Central dot — pulse with breath
        cx, cy = w / 2, h * 0.36
        dot_r  = 5 + self._breath * 3
        grad2  = QRadialGradient(cx, cy, dot_r * 2)
        grad2.setColorAt(0.0, QColor(acc.red(), acc.green(), acc.blue(), 255))
        grad2.setColorAt(1.0, QColor(acc.red(), acc.green(), acc.blue(), 0))
        p.setBrush(grad2)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), dot_r * 2, dot_r * 2)

        # Halo rings (two concentric, faint)
        for ring_r in (20, 35):
            ring_alpha = int((0.15 + self._breath * 0.1) * 255)
            ring_pen = QPen(QColor(acc.red(), acc.green(), acc.blue(), ring_alpha), 1)
            p.setPen(ring_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

    # ── Mouse events ──────────────────────────────────────────────────────────

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()

    def mousePressEvent(self, event) -> None:
        if (event.button() == Qt.MouseButton.LeftButton
                and self._phase == self._PHASE_ALIVE):
            self.clicked.emit(self._defn.panel_id)
        super().mousePressEvent(event)


# ──────────────────────────────────────────────────────────────────────────────
#  CarrierDeck
# ──────────────────────────────────────────────────────────────────────────────

class CarrierDeck(QWidget):
    """
    The five-panel sovereign command deck.

    Usage
    ─────
    deck = CarrierDeck(parent=self)
    deck.panel_selected.connect(self._on_panel_selected)
    deck.begin_materialize()   # called by MainWindow after intro
    """

    panel_selected = Signal(int)   # 1..5

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #080a12;")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # ── Ambient star-dust field (120 points) ──────────────────────────
        self._stars: list[tuple[float, float, float]] = []   # x, y, r
        self._stars_seeded = False

        # ── Layout ────────────────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Top spacer
        outer.addStretch(1)

        # Panel row
        panel_row = QHBoxLayout()
        panel_row.setContentsMargins(40, 0, 40, 0)
        panel_row.setSpacing(18)
        outer.addLayout(panel_row, stretch=8)

        # Bottom spacer
        outer.addStretch(1)

        # ── Create five panels ────────────────────────────────────────────
        self._panels: List[CelestialPanel] = []
        for defn in PANEL_DEFS:
            panel = CelestialPanel(defn, parent=self)
            panel.clicked.connect(self._on_panel_clicked)
            self._panels.append(panel)
            panel_row.addWidget(panel)

        # ── Nebula overlay (behind panels, transparent to mouse) ──────────
        if _NEBULA_AVAILABLE:
            self._nebula = ActiveRandomNebula(parent=self, density=7)
            self._nebula.lower()
            self._nebula.start()
        else:
            self._nebula = None

        # ── Ambient star timer ────────────────────────────────────────────
        self._star_timer = QTimer(self)
        self._star_timer.setInterval(50)
        self._star_timer.timeout.connect(self.update)
        self._star_timer.start()

        # ── Materialize timers (one per panel) ────────────────────────────
        self._mat_timers: List[QTimer] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def begin_materialize(self) -> None:
        """
        Fire each panel's materialise animation with its configured delay.
        Called by MainWindow._on_intro_finished() (via QTimer.singleShot).
        """
        for panel in self._panels:
            t = QTimer(self)
            t.setSingleShot(True)
            t.setInterval(panel._defn.delay_ms)
            t.timeout.connect(panel.start_materialize)
            t.start()
            self._mat_timers.append(t)

    def stop_all(self) -> None:
        """Stop all running timers. Called from MainWindow.closeEvent."""
        for t in self._mat_timers:
            t.stop()
        for panel in self._panels:
            panel.stop()
        self._star_timer.stop()
        if self._nebula:
            try:
                self._nebula.stop()
            except AttributeError:
                pass

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_panel_clicked(self, panel_id: int) -> None:
        print(f"[CarrierDeck]  Panel {panel_id} selected.")
        self.panel_selected.emit(panel_id)

    # ── Paint (ambient star-dust) ─────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        if not self._stars_seeded:
            self._seed_stars()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(8, 10, 18))
        for sx, sy, sr in self._stars:
            alpha = random.randint(120, 220)
            p.setBrush(QColor(200, 215, 255, alpha))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(sx, sy), sr, sr)
        p.end()

    def _seed_stars(self) -> None:
        w, h = self.width(), self.height()
        self._stars = [
            (random.uniform(0, w),
             random.uniform(0, h),
             random.uniform(0.4, 1.4))
            for _ in range(120)
        ]
        self._stars_seeded = True

    def resizeEvent(self, event) -> None:
        self._stars_seeded = False   # re-seed on resize
        if self._nebula:
            self._nebula.resize(self.size())
        super().resizeEvent(event)


# ──────────────────────────────────────────────────────────────────────────────
#  Standalone test  —  python ui\carrier_deck.py
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("SIG — Carrier Deck")

    win = QWidget()
    win.setWindowTitle("Starfield Intelligent Gallery — Carrier Deck Test")
    win.resize(1280, 720)
    win.setStyleSheet("background-color: #080a12;")

    layout = QVBoxLayout(win)
    layout.setContentsMargins(0, 0, 0, 0)

    deck = CarrierDeck(win)
    deck.panel_selected.connect(
        lambda pid: print(f"[TEST] Panel {pid} selected!")
    )
    layout.addWidget(deck)

    win.show()

    # Start materialisation after 500 ms
    QTimer.singleShot(500, deck.begin_materialize)

    sys.exit(app.exec())
