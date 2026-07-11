# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║     C I N E M A T I C   C O N T R O L L E R                 ║
# ║     Starfield Intelligent Gallery                            ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  cinematic_controller.py                        ║
# ║  Location  :  C:\SIG\ui\cinematic_controller.py              ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)      ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator)║
# ║  Version   :  2026.07.02 — All Five Panels Live              ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  WHAT THIS FILE DOES                                         ║
# ║                                                              ║
# ║  Routes panel_selected(int) from the Carrier Deck to the     ║
# ║  correct cinematic overlay sequence.                         ║
# ║                                                              ║
# ║  FIVE SEQUENCES                                              ║
# ║    1  Journey       — Star warp: trails streak to infinity   ║
# ║    2  Archive       — Data cascade: glyphs rain, beam scans  ║
# ║    3  Artifacts     — Halo reveal: resonance rings bloom     ║
# ║    4  Companions    — Orbital: crew-dots orbit, pulse rolls  ║
# ║    5  Cosmic Choice — The Threshold: light from nothing      ║
# ║                                                              ║
# ║  EACH OVERLAY                                                ║
# ║    - Full-screen, covers the entire MainWindow               ║
# ║    - ~7 second animated sequence                             ║
# ║    - Space / Escape → return to Carrier Deck immediately     ║
# ║    - Auto-returns when sequence completes                    ║
# ║    - Emits sequence_finished when done                       ║
# ╚══════════════════════════════════════════════════════════════╝
# ================================================================

from __future__ import annotations

import math
import random
import sys
from typing import List, Tuple

from PySide6.QtCore    import Qt, QPointF, QRectF, QTimer, Signal
from PySide6.QtGui     import (QColor, QFont, QKeySequence,
                                QLinearGradient, QPainter,
                                QPainterPath, QPen, QRadialGradient,
                                QShortcut)
from PySide6.QtWidgets import QApplication, QWidget

def play_nebula_pebble_morph(self):
    morph = NebulaPebbleMorph()
    morph.run()

# ══════════════════════════════════════════════════════════════════════════════
#  Base overlay — shared by all five sequences
# ══════════════════════════════════════════════════════════════════════════════

class _PanelOverlay(QWidget):
    """
    Full-screen cinematic overlay.
    Subclasses implement _draw_sequence(p, w, h, t) where t is 0..1.
    """

    sequence_finished = Signal()

    _FPS       = 40
    _DURATION  = 7_000   # ms total sequence length

    # Colours subclasses should override
    _BG_COLOR   = QColor(4, 5, 10, 245)
    _PANEL_NAME = "PANEL"
    _PANEL_SUB  = ""
    _GLOW_COLOR = QColor(100, 160, 255)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: transparent;")

        self._elapsed = 0       # ms since start
        self._done    = False

        self._timer = QTimer(self)
        self._timer.setInterval(1000 // self._FPS)
        self._timer.timeout.connect(self._tick)

        for key in ("Space", "Escape", "Return"):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._finish)

        self.show()
        self.raise_()
        self.setFocus()
        self._timer.start()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        self._elapsed += 1000 // self._FPS
        if self._elapsed >= self._DURATION:
            self._finish()
        else:
            self.update()

    def _finish(self) -> None:
        if self._done:
            return
        self._done = True
        self._timer.stop()
        self.hide()
        self.deleteLater()
        self.sequence_finished.emit()

    def mousePressEvent(self, event) -> None:
        self._finish()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        t = self._elapsed / self._DURATION          # 0..1

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        p.fillRect(self.rect(), self._BG_COLOR)

        # Panel name (top-centre)
        self._draw_title(p, w, h, t)

        # Subclass-specific sequence
        self._draw_sequence(p, w, h, t)

        # Hint (bottom-centre, fades in after 1 s)
        hint_alpha = max(0, min(255, int((t - 0.15) / 0.2 * 255)))
        if hint_alpha > 0:
            p.setOpacity(hint_alpha / 255)
            hint_font = QFont("Segoe UI", 11, QFont.Weight.Thin)
            hint_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
            p.setFont(hint_font)
            p.setPen(QColor(160, 180, 220, hint_alpha))
            p.drawText(QRectF(0, h - 44, w, 30),
                       Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                       "SPACE  ·  ESC  ·  CLICK   to return to Carrier Deck")
            p.setOpacity(1.0)

        p.end()

    def _draw_title(self, p: QPainter, w: int, h: int, t: float) -> None:
        fade = min(1.0, t / 0.12)
        if fade <= 0:
            return
        p.setOpacity(fade)

        name_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        name_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 5)
        p.setFont(name_font)
        gc = self._GLOW_COLOR
        p.setPen(QColor(gc.red(), gc.green(), gc.blue(), 220))
        p.drawText(QRectF(0, 28, w, 44),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._PANEL_NAME)

        sub_font = QFont("Segoe UI", 11, QFont.Weight.Thin)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        p.setFont(sub_font)
        p.setPen(QColor(180, 200, 240, 160))
        p.drawText(QRectF(0, 68, w, 26),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   self._PANEL_SUB)

        p.setOpacity(1.0)

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        pass   # subclasses override this


# ══════════════════════════════════════════════════════════════════════════════
#  Panel 1 — JOURNEY  (Cobalt blue)
#  Star-warp: radial trails streak outward, then a destination star blooms.
# ══════════════════════════════════════════════════════════════════════════════

class _JourneyOverlay(_PanelOverlay):
    _PANEL_NAME = "JOURNEY"
    _PANEL_SUB  = "Exploration  ·  Discovery  ·  The Unknown"
    _GLOW_COLOR = QColor(80, 160, 255)
    _BG_COLOR   = QColor(2, 5, 14, 250)

    _STAR_COUNT = 140

    def __init__(self, parent: QWidget) -> None:
        self._stars = [
            (random.uniform(0, 2 * math.pi),
             random.uniform(0.02, 1.0),
             random.uniform(0.8, 2.2))
            for _ in range(self._STAR_COUNT)
        ]
        super().__init__(parent)

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        cx, cy = w / 2, h / 2

        # Phase 0..0.6 — warp streaks
        warp_t = min(1.0, t / 0.6)
        ease   = warp_t ** 2

        for angle, dist_frac, width in self._stars:
            speed  = 0.18 + dist_frac * 0.82
            trail  = ease * speed
            r_near = dist_frac * 30 * ease
            r_far  = dist_frac * max(w, h) * trail

            dx = math.cos(angle)
            dy = math.sin(angle)

            alpha = int(200 * min(1.0, trail * 3))
            col   = QColor(120, 180, 255, alpha)
            pen   = QPen(col, width)
            p.setPen(pen)
            p.drawLine(QPointF(cx + dx * r_near, cy + dy * r_near),
                       QPointF(cx + dx * r_far,  cy + dy * r_far))

        # Phase 0.6..1.0 — destination star blooms
        if t > 0.6:
            bloom_t   = (t - 0.6) / 0.4
            bloom_ease = bloom_t * bloom_t * (3 - 2 * bloom_t)
            star_r    = bloom_ease * 60
            alpha_star = int(bloom_ease * 255)

            grad = QRadialGradient(cx, cy, star_r * 2)
            grad.setColorAt(0.0, QColor(200, 230, 255, alpha_star))
            grad.setColorAt(0.3, QColor(80, 160, 255, alpha_star // 2))
            grad.setColorAt(1.0, QColor(30, 60, 180, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), star_r * 2, star_r * 2)

            # Coordinate rings
            for ring_r in (star_r * 1.5, star_r * 2.5, star_r * 4.0):
                ring_alpha = int(bloom_ease * 80)
                p.setPen(QPen(QColor(80, 160, 255, ring_alpha), 1))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)


# ══════════════════════════════════════════════════════════════════════════════
#  Panel 2 — ARCHIVE  (Violet)
#  Data cascade: glyphs rain in columns, a gold scan-beam sweeps down.
# ══════════════════════════════════════════════════════════════════════════════

_GLYPHS = list("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω∞∑∏√∂∇∆Ω")


class _ArchiveOverlay(_PanelOverlay):
    _PANEL_NAME = "ARCHIVE"
    _PANEL_SUB  = "Memory  ·  Knowledge  ·  The Record of All Things"
    _GLOW_COLOR = QColor(180, 80, 255)
    _BG_COLOR   = QColor(4, 2, 14, 250)

    _COL_COUNT = 22

    def __init__(self, parent: QWidget) -> None:
        self._cols = [
            (random.uniform(0, 0.5),
             random.uniform(0.6, 1.4),
             [random.choice(_GLYPHS) for _ in range(32)])
            for _ in range(self._COL_COUNT)
        ]
        super().__init__(parent)

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        col_w  = w / self._COL_COUNT
        glyph_h = 26

        glyph_font = QFont("Segoe UI Symbol", 13)
        p.setFont(glyph_font)

        for idx, (offset, speed, glyphs) in enumerate(self._cols):
            x_centre = (idx + 0.5) * col_w
            scroll   = (t * speed + offset) % 1.0
            y_start  = scroll * (h + 200) - 200

            for gi, g in enumerate(glyphs):
                gy = y_start + gi * glyph_h
                if gy < -glyph_h or gy > h + glyph_h:
                    continue
                # Brighter glyphs near the top of the stream
                depth = 1.0 - (gi / len(glyphs))
                alpha = int(depth * 180 + 20)
                col   = QColor(160, 60, 220, alpha)
                p.setPen(col)
                p.drawText(QRectF(x_centre - 10, gy, 22, glyph_h),
                           Qt.AlignmentFlag.AlignCenter, g)

        # Gold scan beam
        beam_y   = t * (h + 60) - 30
        beam_h   = 50
        if -beam_h < beam_y < h + beam_h:
            grad = QLinearGradient(0, beam_y - beam_h, 0, beam_y + beam_h)
            grad.setColorAt(0.0, QColor(200, 160, 20, 0))
            grad.setColorAt(0.5, QColor(255, 210, 60, 90))
            grad.setColorAt(1.0, QColor(200, 160, 20, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(QRectF(0, beam_y - beam_h, w, beam_h * 2))


# ══════════════════════════════════════════════════════════════════════════════
#  Panel 3 — ARTIFACTS  (Gold)
#  Halo reveal: resonance rings bloom from centre, glyph materialises.
# ══════════════════════════════════════════════════════════════════════════════

class _ArtifactsOverlay(_PanelOverlay):
    _PANEL_NAME = "ARTIFACTS"
    _PANEL_SUB  = "Relics  ·  Revelation  ·  The Weight of the Ancient"
    _GLOW_COLOR = QColor(255, 200, 60)
    _BG_COLOR   = QColor(6, 4, 2, 252)

    _RING_COUNT = 7

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        cx, cy = w / 2, h * 0.52

        # Halo gradient
        halo_t = min(1.0, t / 0.5)
        halo_r = halo_t * 200
        if halo_r > 0:
            grad = QRadialGradient(cx, cy, halo_r)
            grad.setColorAt(0.0, QColor(255, 200, 40, int(halo_t * 80)))
            grad.setColorAt(0.5, QColor(200, 130, 20, int(halo_t * 30)))
            grad.setColorAt(1.0, QColor(180, 100, 10, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), halo_r, halo_r)

        # Resonance rings (staggered bloom)
        for ri in range(self._RING_COUNT):
            ring_start = ri * 0.07
            ring_t = max(0, min(1, (t - ring_start) / 0.6))
            if ring_t <= 0:
                continue
            ring_r     = ring_t * (80 + ri * 30)
            ring_alpha = int((1.0 - ring_t) * 180)
            p.setPen(QPen(QColor(255, 180, 40, ring_alpha), 1.5))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

        # Central glyph (materialises after t=0.3)
        if t > 0.3:
            glyph_t = min(1.0, (t - 0.3) / 0.4)
            alpha   = int(glyph_t * 240)
            glyph_font = QFont("Segoe UI Symbol", 64, QFont.Weight.Thin)
            p.setFont(glyph_font)
            p.setPen(QColor(255, 210, 80, alpha))
            p.drawText(QRectF(cx - 60, cy - 60, 120, 120),
                       Qt.AlignmentFlag.AlignCenter, "⬡")

            # Inner dot
            dot_r = 6 * glyph_t
            p.setBrush(QColor(255, 240, 180, alpha))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), dot_r, dot_r)


# ══════════════════════════════════════════════════════════════════════════════
#  Panel 4 — COMPANIONS  (Teal)
#  Orbital formation: crew-dots orbit the centre, a pulse rolls outward.
# ══════════════════════════════════════════════════════════════════════════════

class _CompanionsOverlay(_PanelOverlay):
    _PANEL_NAME = "COMPANIONS"
    _PANEL_SUB  = "Crew  ·  Relationships  ·  Those Who Stand With You"
    _GLOW_COLOR = QColor(60, 220, 210)
    _BG_COLOR   = QColor(2, 10, 12, 250)

    _CREW = [
        (60,  0.0,           QColor(80, 220, 210, 220)),
        (90,  2 * math.pi / 3, QColor(60, 200, 180, 200)),
        (90,  4 * math.pi / 3, QColor(40, 180, 160, 180)),
        (120, math.pi / 4,   QColor(100, 230, 220, 160)),
    ]

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        cx, cy = w / 2, h / 2

        # Orbit speed ramps up then settles
        orbit_speed = 0.8 + math.sin(t * math.pi) * 0.4
        angle_base  = t * orbit_speed * 2 * math.pi

        # Central core
        core_t = min(1.0, t / 0.2)
        core_r = core_t * 14
        core_grad = QRadialGradient(cx, cy, core_r * 2)
        core_grad.setColorAt(0, QColor(80, 240, 220, int(core_t * 255)))
        core_grad.setColorAt(1, QColor(40, 160, 150, 0))
        p.setBrush(core_grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), core_r * 2, core_r * 2)

        # Crew dots
        for orbit_r, phase_offset, colour in self._CREW:
            appear_t = min(1.0, max(0, t / 0.35))
            if appear_t <= 0:
                continue
            angle = angle_base + phase_offset
            dx    = math.cos(angle) * orbit_r
            dy    = math.sin(angle) * orbit_r * 0.55    # slightly elliptical
            px, py = cx + dx, cy + dy

            # Dot glow
            dot_r  = 10 * appear_t
            dgrad  = QRadialGradient(px, py, dot_r * 2.5)
            dgrad.setColorAt(0,   QColor(colour.red(), colour.green(), colour.blue(), 220))
            dgrad.setColorAt(1,   QColor(colour.red(), colour.green(), colour.blue(), 0))
            p.setBrush(dgrad)
            p.drawEllipse(QPointF(px, py), dot_r * 2.5, dot_r * 2.5)

            # Orbit trail (arc behind each dot)
            trail_pen = QPen(QColor(colour.red(), colour.green(), colour.blue(), 50), 1)
            p.setPen(trail_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            arc_rect = QRectF(cx - orbit_r, cy - orbit_r * 0.55,
                              orbit_r * 2, orbit_r * 2 * 0.55)
            p.drawEllipse(arc_rect)

        # Pulse waves
        for pulse_n in range(4):
            pulse_start = pulse_n * 0.18
            pulse_t     = (t - pulse_start) % 1.2
            if 0 < pulse_t < 0.9:
                pulse_r     = pulse_t * 240
                pulse_alpha = int((1 - pulse_t / 0.9) * 120)
                p.setPen(QPen(QColor(60, 220, 210, pulse_alpha), 1.5))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(cx, cy), pulse_r, pulse_r)


# ══════════════════════════════════════════════════════════════════════════════
#  Panel 5 — COSMIC CHOICE  (White-Silver)
#  The Threshold: darkness → a single point of light → everything.
# ══════════════════════════════════════════════════════════════════════════════

class _CosmicChoiceOverlay(_PanelOverlay):
    _PANEL_NAME = "COSMIC CHOICE"
    _PANEL_SUB  = "The Threshold  ·  The Decision That Changes Everything"
    _GLOW_COLOR = QColor(220, 230, 255)
    _BG_COLOR   = QColor(0, 0, 0, 255)
    _DURATION   = 9_000   # Cosmic Choice gets the longest sequence

    def __init__(self, parent: QWidget) -> None:
        self._stars = [
            (random.uniform(0, 2 * math.pi),
             random.uniform(10, max(parent.width(), parent.height()) // 2))
            for _ in range(200)
        ]
        super().__init__(parent)

    def _draw_sequence(self, p: QPainter, w: int, h: int, t: float) -> None:
        cx, cy = w / 2, h / 2

        # Act 1 (0..0.3): total darkness — point of light emerges
        if t < 0.35:
            act_t  = t / 0.35
            point_r = act_t * act_t * 30
            alpha  = int(act_t * 255)
            grad   = QRadialGradient(cx, cy, point_r)
            grad.setColorAt(0.0, QColor(255, 255, 255, alpha))
            grad.setColorAt(0.4, QColor(200, 215, 255, alpha // 3))
            grad.setColorAt(1.0, QColor(180, 200, 255, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), point_r * 2, point_r * 2)

        # Act 2 (0.3..0.7): expansion — rings, stars reveal
        elif t < 0.72:
            act_t  = (t - 0.35) / 0.37
            ease   = act_t * act_t * (3 - 2 * act_t)

            # Expanding halo
            halo_r = ease * 380
            grad   = QRadialGradient(cx, cy, halo_r)
            grad.setColorAt(0.0, QColor(240, 245, 255, int(ease * 60)))
            grad.setColorAt(0.6, QColor(180, 200, 255, int(ease * 30)))
            grad.setColorAt(1.0, QColor(140, 165, 220, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), halo_r, halo_r)

            # Temple rings
            for ri in range(6):
                ring_t  = max(0, min(1, (ease - ri * 0.12) / 0.5))
                if ring_t <= 0:
                    continue
                ring_r  = ring_t * (60 + ri * 55)
                ring_a  = int((1 - ring_t * 0.6) * 160)
                p.setPen(QPen(QColor(200, 220, 255, ring_a), 1))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

            # Stars emerging
            for angle, dist in self._stars:
                star_frac = min(1, ease * 1.5)
                if star_frac <= 0:
                    continue
                sx = cx + math.cos(angle) * dist * star_frac
                sy = cy + math.sin(angle) * dist * star_frac
                sa = int(star_frac * 200)
                p.setBrush(QColor(220, 235, 255, sa))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(sx, sy), 1.4, 1.4)

        # Act 3 (0.7..1.0): presence — the cosmos breathes, waiting
        else:
            act_t  = (t - 0.72) / 0.28
            breath = (math.sin(act_t * math.pi * 4) + 1) / 2

            # All stars visible, slowly breathing
            for angle, dist in self._stars:
                sx = cx + math.cos(angle) * dist
                sy = cy + math.sin(angle) * dist
                sa = int(150 + breath * 80)
                sr = 1.0 + breath * 0.6
                p.setBrush(QColor(220, 235, 255, sa))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(sx, sy), sr, sr)

            # Breathing halo
            halo_r = 200 + breath * 60
            grad   = QRadialGradient(cx, cy, halo_r)
            grad.setColorAt(0.0, QColor(220, 235, 255, int(20 + breath * 40)))
            grad.setColorAt(1.0, QColor(180, 200, 255, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), halo_r, halo_r)

            # Central presence
            pres_r = 8 + breath * 6
            p.setBrush(QColor(240, 248, 255, 240))
            p.drawEllipse(QPointF(cx, cy), pres_r, pres_r)


# ══════════════════════════════════════════════════════════════════════════════
#  CinematicController  — the router
# ══════════════════════════════════════════════════════════════════════════════

_OVERLAY_MAP = {
    1: _JourneyOverlay,
    2: _ArchiveOverlay,
    3: _ArtifactsOverlay,
    4: _CompanionsOverlay,
    5: _CosmicChoiceOverlay,
}


class CinematicController:
    """
    Routes panel_selected(int) from the Carrier Deck to the
    correct cinematic overlay.

    Usage in MainWindow
    ───────────────────
    self._cinema = CinematicController(
        parent        = self,
        on_return     = self._on_cinema_finished,
    )

    # In _on_panel_selected:
    self._cinema.play(panel_id)

    # on_return is called when the user exits the sequence.
    """

    def __init__(
        self,
        parent    : QWidget,
        on_return = None,
    ) -> None:
        self._parent    = parent
        self._on_return = on_return
        self._overlay   = None

    def play(self, panel_id: int) -> None:
        print(f"[CinematicController]  Playing sequence for panel {panel_id}")

        # Whisper to the Throne (if present)
        parent = self._parent
        if parent is not None and hasattr(parent, "speak_to_throne"):
            try:
                parent.speak_to_throne(f"A path has been entered: {panel_id}.")
            except Exception:
                print(f"[CinematicController] whisper (fallback): path {panel_id} entered.")
        else:
            print(f"[CinematicController] whisper: path {panel_id} entered.")

        cls = _OVERLAY_MAP.get(panel_id)
        if cls is None:
            print(f"[CinematicController]  No sequence for panel {panel_id}")
            return

        print(f"[CinematicController]  Playing sequence for panel {panel_id}")

        self._overlay = cls(self._parent)
        self._overlay.resize(self._parent.size())
        self._overlay.sequence_finished.connect(self._on_sequence_done)

    def _on_sequence_done(self) -> None:
        self._overlay = None
        print("[CinematicController]  Sequence complete — back to Carrier Deck.")

        # Whisper to the Throne (if present)
        parent = self._parent
        if parent is not None and hasattr(parent, "speak_to_throne"):
            try:
                parent.speak_to_throne("The pilgrim has returned to the Hall.")
            except Exception:
                print("[CinematicController] whisper (fallback): pilgrim returned.")
        else:
            print("[CinematicController] whisper: pilgrim returned.")

        if self._on_return:
            self._on_return()


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone test  —  python ui\cinematic_controller.py
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QWidget()
    win.setWindowTitle("SIG — Cinematic Controller Test")
    win.resize(1280, 720)
    win.setStyleSheet("background-color: #080a12;")
    win.show()

    ctrl = CinematicController(parent=win)

    # Cycle through all 5 panels for testing
    _panel_cycle = iter([1, 2, 3, 4, 5])

    def play_next():
        pid = next(_panel_cycle, None)
        if pid is not None:
            print(f"[TEST]  Launching panel {pid}...")
            ctrl._on_return = play_next
            ctrl.play(pid)
        else:
            print("[TEST]  All sequences complete!")
            app.quit()

    QTimer.singleShot(400, play_next)
    sys.exit(app.exec())
