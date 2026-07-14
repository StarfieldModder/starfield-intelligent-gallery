# File: ui/carrier_deck.py
# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║         C A R R I E R   D E C K                              ║
# ║         Starfield Intelligent Gallery                        ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  carrier_deck.py                                ║
# ║  Location  :  C:\SIG\ui\carrier_deck.py                      ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)      ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator)║
# ║  Version   :  2026.07.11 — Pebble Morph to AncientFragment   ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  WHAT THIS FILE IS                                           ║
# ║                                                              ║
# ║  The Carrier Deck — five sovereign panels that materialise   ║
# ║  from particle clouds after The Crossing intro completes.    ║
# ║                                                              ║
# ║  NOTE: Horizontal panels can be hidden and their color       ║
# ║  palette transferred to compact "pebble" widgets which then  ║
# ║  morph into AncientFragment objects for a seamless visual    ║
# ║  transition into the fragment/coalescence system.            ║
# ╚══════════════════════════════════════════════════════════════╝
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from PySide6.QtCore    import (Property, QEasingCurve, QPointF,
                                QPropertyAnimation, QRectF, Qt,
                                QTimer, Signal)
from PySide6.QtGui     import (QColor, QFont, QLinearGradient,
                                QPainter, QPainterPath, QPen,
                                QRadialGradient)
from PySide6.QtWidgets import (QApplication, QHBoxLayout,
                                QSizePolicy, QVBoxLayout, QWidget, QLabel)

# ActiveRandomNebula — graceful fallback if not yet present
try:
    from ui.active_random_nebula import ActiveRandomNebula
    _NEBULA_AVAILABLE = True
except ImportError:
    _NEBULA_AVAILABLE = False
    print("[CarrierDeck]  ActiveRandomNebula not found — deck runs without nebula overlay.")

# AncientFragment — used for morphing pebbles into fragments
try:
    from ui.ancient_fragment import AncientFragment
    _ANCIENT_FRAGMENT_AVAILABLE = True
except Exception:
    _ANCIENT_FRAGMENT_AVAILABLE = False
    print("[CarrierDeck]  AncientFragment not available — pebble morph will use labels fallback.")


@dataclass
class PanelDef:
    panel_id : int
    name     : str
    subtitle : str
    color    : QColor
    accent   : QColor
    delay_ms : int


PANEL_DEFS: List[PanelDef] = [
    PanelDef(1, "JOURNEY", "Exploration & Discovery", QColor(30,90,200), QColor(80,160,255), 0),
    PanelDef(2, "ARCHIVE", "Memory & Knowledge", QColor(110,30,180), QColor(180,80,255), 300),
    PanelDef(3, "ARTIFACTS", "Relics & Revelation", QColor(180,130,20), QColor(255,200,60), 600),
    PanelDef(4, "COMPANIONS", "Relationships & Crew", QColor(20,140,140), QColor(60,220,220), 900),
    PanelDef(5, "COSMIC CHOICE", "The Threshold Awaits", QColor(160,175,200), QColor(220,230,255), 1200),
]


@dataclass
class Particle:
    x   : float
    y   : float
    tx  : float
    ty  : float
    vx  : float = field(default=0.0)
    vy  : float = field(default=0.0)
    age : float = field(default=0.0)
    r   : float = field(default=2.0)


class CelestialPanel(QWidget):
    clicked = Signal(int)
    _PHASE_IDLE      = 0
    _PHASE_PARTICLES = 1
    _PHASE_SOLIDIFY  = 2
    _PHASE_ALIVE     = 3

    _PARTICLE_COUNT  = 80
    _PARTICLE_FPS    = 40
    _SOLIDIFY_MS     = 1_800
    _BREATH_PERIOD   = 3_000

    def __init__(self, defn: PanelDef, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._defn      = defn
        self._phase     = self._PHASE_IDLE
        self._particles : List[Particle] = []
        self._opacity   = 0.0
        self._breath    = 0.0
        self._hovered   = False
        self._arc_angle = 0.0

        self.setMinimumSize(200, 380)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._timer = QTimer(self)
        self._timer.setInterval(1000 // self._PARTICLE_FPS)
        self._timer.timeout.connect(self._tick)

        self._solidify_timer = QTimer(self)
        self._solidify_timer.setInterval(16)
        self._solidify_elapsed = 0
        self._solidify_timer.timeout.connect(self._solidify_tick)

        self._breath_elapsed = random.randint(0, self._BREATH_PERIOD)

    def start_materialize(self) -> None:
        self._phase = self._PHASE_PARTICLES
        self._spawn_particles()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self._solidify_timer.stop()

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

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if self._phase in (self._PHASE_PARTICLES, self._PHASE_SOLIDIFY):
            self._draw_particles(p, w, h)
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
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), int(60  + breath_val * 60)))
        grad.setColorAt(0.5, QColor(c.red(), c.green(), c.blue(), int(30  + breath_val * 30)))
        grad.setColorAt(1.0, QColor(8, 10, 18, 200))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 12, 12)
        glow_alpha = int(160 + breath_val * 95)
        pen = QPen(QColor(acc.red(), acc.green(), acc.blue(), glow_alpha), 2.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 12, 12)
        arc_rect = QRectF(w - 56, 12, 44, 44)
        arc_pen  = QPen(QColor(acc.red(), acc.green(), acc.blue(), 100), 1.5)
        arc_pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(arc_pen)
        p.drawArc(arc_rect, int(self._arc_angle * 16), 240 * 16)
        name_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        name_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        p.setFont(name_font)
        p.setPen(QColor(acc.red(), acc.green(), acc.blue(), 240))
        p.drawText(QRectF(16, h * 0.48, w - 32, 32),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._defn.name)
        sub_font = QFont("Segoe UI", 9, QFont.Weight.Thin)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        p.setFont(sub_font)
        p.setPen(QColor(200, 215, 240, 160))
        p.drawText(QRectF(16, h * 0.58, w - 32, 28),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._defn.subtitle)
        cx, cy = w / 2, h * 0.36
        dot_r  = 5 + self._breath * 3
        grad2  = QRadialGradient(cx, cy, dot_r * 2)
        grad2.setColorAt(0.0, QColor(acc.red(), acc.green(), acc.blue(), 255))
        grad2.setColorAt(1.0, QColor(acc.red(), acc.green(), acc.blue(), 0))
        p.setBrush(grad2)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), dot_r * 2, dot_r * 2)
        for ring_r in (20, 35):
            ring_alpha = int((0.15 + self._breath * 0.1) * 255)
            ring_pen = QPen(QColor(acc.red(), acc.green(), acc.blue(), ring_alpha), 1)
            p.setPen(ring_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()

    def mousePressEvent(self, event) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and self._phase == self._PHASE_ALIVE):
            self.clicked.emit(self._defn.panel_id)
        super().mousePressEvent(event)


class CarrierDeck(QWidget):
    panel_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #080a12;")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._stars: list[tuple[float, float, float]] = []
        self._stars_seeded = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addStretch(1)

        panel_row = QHBoxLayout()
        panel_row.setContentsMargins(40, 0, 40, 0)
        panel_row.setSpacing(18)
        outer.addLayout(panel_row, stretch=8)
        self._panel_row = panel_row
        outer.addStretch(1)

        self._panels: List[CelestialPanel] = []
        for defn in PANEL_DEFS:
            panel = CelestialPanel(defn, parent=self)
            panel.clicked.connect(self._on_panel_clicked)
            self._panels.append(panel)
            panel_row.addWidget(panel)

        if _NEBULA_AVAILABLE:
            self._nebula = ActiveRandomNebula(parent=self, density=7)
            self._nebula.lower()
            self._nebula.start()
        else:
            self._nebula = None

        self._star_timer = QTimer(self)
        self._star_timer.setInterval(50)
        self._star_timer.timeout.connect(self.update)
        self._star_timer.start()

        self._mat_timers: List[QTimer] = []
        self._pebbles: List[QWidget] = []
        self._pebble_targets: List[tuple[float, float]] = []
        self._pebble_starts: List[tuple[float, float]] = []
        self._pebble_anim_timer: Optional[QTimer] = None

        # When pebbles morph, we keep AncientFragment instances here
        self._pebble_fragments: List[AncientFragment] = [] if _ANCIENT_FRAGMENT_AVAILABLE else []

        # Fallback labels if AncientFragment isn't available
        self._coalesce_labels: List[QLabel] = []

    def begin_materialize(self, use_pebbles: bool = True) -> None:
        if use_pebbles:
            for panel in self._panels:
                try:
                    panel.hide()
                except Exception:
                    pass

            # create pebbles and add to layout
            for i, defn in enumerate(PANEL_DEFS):
                peb = QWidget(self)
                peb.setFixedSize(28, 28)
                cr, cg, cb = defn.color.red(), defn.color.green(), defn.color.blue()
                peb.setStyleSheet(
                    f"background-color: rgba({cr},{cg},{cb},255); border-radius: 14px; border: 1px solid rgba(255,255,255,30);"
                )
                peb.hide()
                self._pebbles.append(peb)
                self._panel_row.addWidget(peb)

            # compute start/target positions
            w = self.width()
            h = self.height()
            left = 80
            right = max(300, w - 80)
            span = right - left
            for i in range(len(self._pebbles)):
                tx = left + (i + 0.5) * (span / len(self._pebbles))
                ty = int(h * 0.52)
                self._pebble_targets.append((tx, ty))

            rng = random.Random(42)
            for i in range(len(self._pebbles)):
                side = rng.randint(0, 3)
                if side == 0:
                    sx, sy = rng.uniform(0, w), -80 - rng.uniform(0, 160)
                elif side == 1:
                    sx, sy = rng.uniform(0, w), h + 80 + rng.uniform(0, 160)
                elif side == 2:
                    sx, sy = -80 - rng.uniform(0, 160), rng.uniform(0, h)
                else:
                    sx, sy = w + 80 + rng.uniform(0, 160), rng.uniform(0, h)
                self._pebble_starts.append((sx, sy))

            # place pebbles at starts and show
            for i, peb in enumerate(self._pebbles):
                sx, sy = self._pebble_starts[i]
                peb.move(int(sx), int(sy))
                peb.show()

            # animate into place over 1.2s
            self._pebble_anim_t = 0.0
            self._pebble_anim_dur = 1.2
            self._pebble_anim_timer = QTimer(self)
            self._pebble_anim_timer.setInterval(16)
            self._pebble_anim_timer.timeout.connect(self._pebble_anim_tick)
            self._pebble_anim_timer.start()
            print("[CarrierDeck] pebbles created and animating into place.")
            return

        # fallback: original panel materialization
        for panel in self._panels:
            t = QTimer(self)
            t.setSingleShot(True)
            t.setInterval(panel._defn.delay_ms)
            t.timeout.connect(panel.start_materialize)
            t.start()
            self._mat_timers.append(t)

    def _pebble_anim_tick(self) -> None:
        try:
            self._pebble_anim_t += 0.016
            t = min(1.0, self._pebble_anim_t / self._pebble_anim_dur)
            ease = 1.0 - (1.0 - t) ** 3.0
            for i, peb in enumerate(self._pebbles):
                sx, sy = self._pebble_starts[i]
                tx, ty = self._pebble_targets[i]
                nx = sx + (tx - sx) * ease
                ny = sy + (ty - sy) * ease
                peb.move(int(nx - peb.width() / 2), int(ny - peb.height() / 2))
            if t >= 1.0:
                if self._pebble_anim_timer:
                    self._pebble_anim_timer.stop()
                print("[CarrierDeck] pebbles settled — morphing into fragments.")
                QTimer.singleShot(180, self._morph_pebbles_to_fragments)
        except Exception as exc:
            print(f"[CarrierDeck] pebble animation tick failed: {exc}")

    def _morph_pebbles_to_fragments(self) -> None:
        """
        Replace the visual pebble widgets with AncientFragment objects
        positioned at the pebble targets. If AncientFragment is not
        available, fall back to the coalescence label sequence.
        """
        try:
            if _ANCIENT_FRAGMENT_AVAILABLE:
                # create AncientFragment objects using panel names
                for i, defn in enumerate(PANEL_DEFS):
                    tx, ty = self._pebble_targets[i]
                    # Use the panel name as the fragment 'word' for visual continuity
                    frag = AncientFragment(defn.name, i, seed=i * 997 + 42)
                    # Place fragment exactly at the pebble target (spawn==target)
                    frag.place(tx, ty, tx, ty)
                    # Immediately settle / lock the fragment visually
                    try:
                        frag.begin_orbit()
                    except Exception:
                        # If begin_orbit not appropriate, set state to SETTLED defensively
                        try:
                            frag.state = AncientFragment.SETTLED
                        except Exception:
                            pass
                    # Keep a reference so GC doesn't collect it
                    self._pebble_fragments.append(frag)

                # remove pebble widgets from layout and hide them
                for peb in self._pebbles:
                    try:
                        peb.hide()
                        peb.setParent(None)
                    except Exception:
                        pass
                self._pebbles.clear()
                print("[CarrierDeck] pebbles morphed into AncientFragment objects.")
                # Trigger a short coalescence inscription sequence if desired
                QTimer.singleShot(300, self._trigger_fragment_inscription)
            else:
                # Fallback: run the label coalescence sequence
                print("[CarrierDeck] AncientFragment unavailable — running label coalescence fallback.")
                self._start_coalesce_sequence()
        except Exception as exc:
            print(f"[CarrierDeck] morphing pebbles failed: {exc}")
            # fallback to labels
            self._start_coalesce_sequence()

    def _trigger_fragment_inscription(self) -> None:
        """
        If fragments exist, nudge them to show a short inscription animation.
        We keep this minimal: set inscription progress to 1.0 over a short time
        so the visual reads as 'coalesced'.
        """
        try:
            if not self._pebble_fragments:
                return
            # Step each fragment's inscription in a staggered fashion
            for i, frag in enumerate(self._pebble_fragments):
                QTimer.singleShot(120 * i, lambda frag=frag: self._set_fragment_inscription(frag))
            QTimer.singleShot(120 * len(self._pebble_fragments) + 400, lambda: print("[CarrierDeck] fragment inscription complete."))
        except Exception as exc:
            print(f"[CarrierDeck] trigger_fragment_inscription failed: {exc}")

    def _set_fragment_inscription(self, frag: AncientFragment) -> None:
        try:
            # Best-effort: set inscription to fully visible
            try:
                frag.inscription = 1.0
            except Exception:
                # If direct property not available, attempt a method if present
                if hasattr(frag, "set_inscription"):
                    try:
                        frag.set_inscription(1.0)
                    except Exception:
                        pass
        except Exception:
            pass

    def _start_coalesce_sequence(self) -> None:
        try:
            # create labels for each word fragment and fade them in sequentially
            self._coalesce_labels = []
            w, h = self.width(), self.height()
            rng = random.Random(1234)
            total = len(PANEL_DEFS)
            for i, defn in enumerate(PANEL_DEFS):
                lbl = QLabel(defn.name, self)
                font = QFont("Segoe UI", 28, QFont.Weight.Bold)
                lbl.setFont(font)
                lbl.setStyleSheet("color: rgba(255, 220, 140, 0); background: transparent;")
                x = w * 0.18 + i * (w * 0.64 / max(1, total - 1)) + rng.uniform(-8, 8)
                y = h * 0.62 + rng.uniform(-6, 6)
                lbl.move(int(x), int(y))
                lbl.adjustSize()
                lbl.show()
                self._coalesce_labels.append(lbl)
            for i, lbl in enumerate(self._coalesce_labels):
                QTimer.singleShot(160 * i, lambda lbl=lbl: self._fade_in_label(lbl))
            QTimer.singleShot(160 * len(self._coalesce_labels) + 600, lambda: print("[CarrierDeck] coalescence complete."))
        except Exception as exc:
            print(f"[CarrierDeck] coalesce sequence failed: {exc}")

    def _fade_in_label(self, lbl: QLabel) -> None:
        try:
            steps = 12
            step_ms = 28
            def step(i=0):
                a = int(220 * (i / steps))
                lbl.setStyleSheet(f"color: rgba(255, 220, 140, {a}); background: transparent;")
                if i < steps:
                    QTimer.singleShot(step_ms, lambda i=i+1: step(i))
            step(0)
        except Exception as exc:
            print(f"[CarrierDeck] fade_in_label failed: {exc}")

    def stop_all(self) -> None:
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

    def _on_panel_clicked(self, panel_id: int) -> None:
        print(f"[CarrierDeck]  Panel {panel_id} selected.")
        parent = self.parent()
        if parent is not None and hasattr(parent, "speak_to_throne"):
            try:
                parent.speak_to_throne(f"A sovereign has stepped forward: {panel_id}.")
            except Exception:
                print(f"[CarrierDeck] whisper (fallback): sovereign {panel_id} stepped forward.")
        else:
            print(f"[CarrierDeck] whisper: sovereign {panel_id} stepped forward.")
        self.panel_selected.emit(panel_id)

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

        # If we have AncientFragment objects created from pebbles, draw them
        if _ANCIENT_FRAGMENT_AVAILABLE and self._pebble_fragments:
            try:
                # Use a simple time value for fragment draw calls
                t = 0.0
                for frag in self._pebble_fragments:
                    try:
                        frag.draw(p, t)
                    except Exception:
                        # If draw signature differs, ignore and continue
                        pass
            except Exception:
                pass

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
        self._stars_seeded = False
        if self._nebula:
            self._nebula.resize(self.size())
        super().resizeEvent(event)


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
    deck.panel_selected.connect(lambda pid: print(f"[TEST] Panel {pid} selected!"))
    layout.addWidget(deck)
    win.show()
    QTimer.singleShot(500, lambda: deck.begin_materialize(use_pebbles=True))
    sys.exit(app.exec())
