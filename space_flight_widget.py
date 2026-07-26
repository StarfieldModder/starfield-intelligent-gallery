r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗                                                 ║
║        ██╔════╝ ██║ ██╔════╝   S P A C E _ F L I G H T _ W I D G E T . P Y   ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "Through the dark between the stars."         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  space_flight_widget.py                                        ║
║  Location   :  C:\SIG\ui\space_flight_widget.py                              ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.05 — True 3D Perspective Starfield Edition            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CINEMATIC SEQUENCE  (~22 seconds total)                                     ║
║                                                                              ║
║  Phase 0  BLACK     (2.5 s)  Pure black — The Crossing just ended.           ║
║  Phase 1  PINPOINT  (1.5 s)  One star appears at screen center, grows.       ║
║  Phase 2  WARP      (10 s)   250-star rush outward. 4 nebulae sweep past.    ║
║                               Cyan nebula #3 — we FLY THROUGH IT.            ║
║  Phase 3  APPROACH  (3 s)    JOURNEY panel grows from a distant pinpoint.    ║
║                               Stars decelerate — we are arriving.            ║
║  Phase 4  GLYPH     (3.5 s)  6 Varuun SVG glyphs dart in from deep space.    ║
║                               Each tumbles (rotating) then LANDS on panel.   ║
║                               "JOURNEY" coalesces letter-by-letter from      ║
║                               the energy of the settled glyphs.              ║
║  Phase 5  HOLD      (1.5 s)  Panel glows. flight_finished emitted.           ║
║                                                                              ║
║  3D STARFIELD ENGINE                                                         ║
║    True perspective projection: screen_pos = focal * world_pos / z           ║
║    Each star has its OWN z-velocity — true parallax depth, not a painted     ║
║    canvas scrolling by. Closer stars rush past; distant ones drift slowly.   ║
║    Spectral color palette (real stellar temperature classes):                ║
║      O/B class  — Blue-white  #B8D4FF  (Rigel, Spica)                        ║
║      A class    — Pure white  #FFFFFF  (Sirius, Vega)  weighted x2           ║
║      F class    — Yel-white   #FFF4D6  (Procyon)                             ║
║      G class    — Gold        #FFD97D  (Sun-like)                            ║
║      K class    — Orange      #FFAA55  (Arcturus)                            ║
║      M class    — Deep red    #FF4422  (Betelgeuse)                          ║
║      Varuun     — Cyan        #44FFEE  (rare O-type accent)                  ║
║    Trail length grows with proximity AND individual star speed.              ║
║    Stars range 1 px pinpoints to 4 px bright orbs.                           ║
║                                                                              ║
║  TECHNICAL CREDITS                                                           ║
║    3D perspective starfield engine designed by Microsoft Copilot             ║
║    (AI Engineer Colleague) — the only starfield where even Star Trek         ║
║    captains would grab a railing.                                            ║
║                                                                              ║
║  VARUUN GLYPH FILES  (C:\SIG\intro\assets\glyphs\)                           ║
║    glyph_hex.svg     glyph_eye.svg     glyph_sigma.svg                       ║
║    glyph_diamond.svg glyph_arrow.svg   glyph_cross.svg                       ║
║    Tinted cobalt #3B78E7 via SourceIn. Fallback: procedural hexagons.        ║
║                                                                              ║
║  KEYBOARD   Space / Enter / Escape — skip to flight_finished immediately     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import List, Optional

# ── Verified PySide6 v6.11.1 imports ─────────────────────────────────────────
#    QShortcut lives in QtGui (NOT QtWidgets) in PySide6 >= 6.4
#    QPoint, QPolygon also live in QtGui in PySide6 6.11.1
# ─────────────────────────────────────────────────────────────────────────────
from PySide6.QtCore    import Qt, QElapsedTimer, QTimer, Signal
from PySide6.QtGui     import (QColor, QFont, QKeySequence, QPainter,
                               QPen, QPixmap, QPoint, QPolygon,
                               QRadialGradient, QShortcut)
from PySide6.QtWidgets import QApplication, QWidget

# ── Optional SVG support ──────────────────────────────────────────────────────
try:
    from PySide6.QtSvg import QSvgRenderer
    _SVG_OK = True
except ImportError:
    _SVG_OK = False
    print("[SpaceFlight]  PySide6.QtSvg not available — using fallback shapes.")


# ══════════════════════════════════════════════════════════════════════════════
#  P H A S E   C O N S T A N T S
# ══════════════════════════════════════════════════════════════════════════════

_P_BLACK    = 0
_P_PINPOINT = 1
_P_WARP     = 2
_P_APPROACH = 3
_P_GLYPH    = 4
_P_HOLD     = 5

_PHASE_MS: list[int] = [2_500, 1_500, 10_000, 3_000, 3_500, 1_500]  # 22 000 ms

_PHASE_START: list[int] = []
_acc = 0
for _d in _PHASE_MS:
    _PHASE_START.append(_acc)
    _acc += _d
_TOTAL_MS = _acc   # 22 000 ms


# ══════════════════════════════════════════════════════════════════════════════
#  3 D   S T A R F I E L D   C O N S T A N T S
# ══════════════════════════════════════════════════════════════════════════════

_FOCAL   = 500      # perspective focal length (pixels)
_Z_FAR   = 1_200    # spawn / reset depth (deep space)
_Z_NEAR  = 10       # threshold: star has passed the viewer — reset it
_N_STARS = 250      # total star count

# Spectral color palette — real stellar temperature classes.
# Pure white (A-class: Sirius, Vega) appears at double weight — most common.
_STAR_COLORS: list[QColor] = [
    QColor(184, 212, 255),  # O/B  Blue-white   (Rigel, Spica)
    QColor(255, 255, 255),  # A    Pure white    (Sirius, Vega)   -+- x2
    QColor(255, 255, 255),  # A    Pure white    (weight repeat)  -+-
    QColor(255, 244, 214),  # F    Yellow-white  (Procyon)
    QColor(255, 217, 125),  # G    Gold          (Sun-like)
    QColor(255, 170,  85),  # K    Orange        (Arcturus)
    QColor(255,  68,  34),  # M    Deep red      (Betelgeuse)
    QColor( 68, 255, 238),  # Varuun  Cyan       (rare O-type accent)
]


# ══════════════════════════════════════════════════════════════════════════════
#  V A R U U N   G L Y P H   A S S E T S
# ══════════════════════════════════════════════════════════════════════════════

_GLYPH_DIR   = Path(r"C:\SIG\intro\assets\glyphs")
_GLYPH_NAMES = [
    "glyph_hex.svg",
    "glyph_eye.svg",
    "glyph_sigma.svg",
    "glyph_diamond.svg",
    "glyph_arrow.svg",
    "glyph_cross.svg",
]


# ══════════════════════════════════════════════════════════════════════════════
#  N E B U L A E
# ══════════════════════════════════════════════════════════════════════════════

# [x_frac, y_frac, R, G, B, rx_frac, ry_frac, drift_per_ms, alpha_max, appear_warp_t]
_NEBULAE = [
    [-0.18,  0.22,  80,  40, 200, 0.42, 0.26, -1.4e-5, 0.55, 0.08],  # violet-blue
    [ 0.22, -0.28, 200,  65,  35, 0.48, 0.24,  1.0e-5, 0.48, 0.25],  # red-amber
    [-0.04, -0.02,  20, 155, 185, 0.40, 0.24, -0.5e-5, 0.40, 0.46],  # CYAN fly-through
    [ 0.18,  0.38, 130,  35, 165, 0.36, 0.30,  1.2e-5, 0.42, 0.68],  # violet
]
_FLYTHROUGH_IDX = 2   # cyan nebula — we pass THROUGH this one


# ══════════════════════════════════════════════════════════════════════════════
#  G L Y P H   S P R I T E
# ══════════════════════════════════════════════════════════════════════════════

class GlyphSprite:
    """
    One Varuun ancient glyph tumbling through space toward the JOURNEY panel.
    States: FLYING -> SETTLING -> SETTLED
    """

    FLYING   = 0
    SETTLING = 1
    SETTLED  = 2

    def __init__(self, renderer, name, sx, sy, tx, ty, size, rot_speed):
        self.renderer  = renderer
        self.name      = name
        self.x         = float(sx)
        self.y         = float(sy)
        self.tx        = float(tx)
        self.ty        = float(ty)
        self.size      = size
        self.rotation  = random.uniform(0.0, 360.0)
        self.rot_speed = rot_speed
        self.speed     = random.uniform(10.0, 24.0)
        self.state     = self.FLYING
        self._pulse    = random.uniform(0.0, math.pi * 2)

    def update(self):
        dx   = self.tx - self.x
        dy   = self.ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if self.state == self.FLYING:
            if dist < self.size * 0.9:
                self.state = self.SETTLING
            else:
                move = min(dist * 0.13, self.speed)
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
                self.rotation = (self.rotation + self.rot_speed) % 360.0

        elif self.state == self.SETTLING:
            self.rotation *= 0.78
            if dist > 1.0:
                move = min(dist * 0.22, self.speed * 0.5)
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
            if abs(self.rotation) < 1.0 and dist < 2.0:
                self.rotation  = 0.0
                self.x, self.y = self.tx, self.ty
                self.state     = self.SETTLED

        if self.state == self.SETTLED:
            self._pulse = (self._pulse + 0.055) % (math.pi * 2)

    @property
    def settled(self):
        return self.state == self.SETTLED

    def draw(self, painter: QPainter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)
        h = self.size // 2

        # Cobalt glow halo
        glow_a = int(55 + 45 * math.sin(self._pulse)) if self.settled else 35
        grad = QRadialGradient(0, 0, self.size + 10)
        grad.setColorAt(0, QColor(59, 120, 231, glow_a))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        r = self.size + 10
        painter.drawEllipse(-r, -r, r * 2, r * 2)

        if self.renderer is not None and _SVG_OK:
            self._draw_svg(painter, h)
        else:
            self._draw_fallback(painter, h)

        painter.restore()

    def _draw_svg(self, painter: QPainter, h: int):
        sz = self.size
        px = QPixmap(sz, sz)
        px.fill(Qt.GlobalColor.transparent)

        p2 = QPainter(px)
        self.renderer.render(p2)
        p2.end()

        p2 = QPainter(px)
        p2.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p2.fillRect(px.rect(), QColor(100, 165, 255, 215))
        p2.end()

        painter.setOpacity(0.92 if self.settled else 0.72)
        painter.drawPixmap(-h, -h, px)
        painter.setOpacity(1.0)

    def _draw_fallback(self, painter: QPainter, h: int):
        """Procedural cobalt hexagon when SVG unavailable."""
        pen = QPen(QColor(100, 165, 255, 200 if self.settled else 155))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QColor(25, 55, 130, 70))
        pts = [
            QPoint(
                int(h * math.cos(math.radians(60 * i))),
                int(h * math.sin(math.radians(60 * i))),
            )
            for i in range(6)
        ]
        painter.drawPolygon(QPolygon(pts))


# ══════════════════════════════════════════════════════════════════════════════
#  S P A C E   F L I G H T   W I D G E T
# ══════════════════════════════════════════════════════════════════════════════

class SpaceFlightWidget(QWidget):
    """
    22-second cinematic deep-space transition with true 3D perspective starfield.

    Each star occupies a point (x, y, z) in 3D space and advances toward the
    viewer at its own individual velocity.  Screen coordinates are computed via
    perspective projection (x * FOCAL / z, y * FOCAL / z).  Trail length grows
    with both proximity and per-star speed — no two stars behave identically.

    Call show_flight() once after showFullScreen().
    Emits flight_finished when complete or skipped.
    """

    flight_finished = Signal()

    # ─────────────────────────────────────────────────────────────────────────
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._done           = False
        self._elapsed        = QElapsedTimer()
        self._speed_mult     = 0.0
        self._warp_frozen_ms = 0

        # ── 3D star field ────────────────────────────────────────────────────
        # Each star is a dict with world-space coords and its OWN z-velocity.
        # Initialise spread across the full depth range so the field looks
        # populated the instant the cinematic starts.
        self._stars: list[dict] = []
        for _ in range(_N_STARS):
            self._stars.append(self._make_star(z_override=None))

        self._sprites         : List[GlyphSprite] = []
        self._sprites_built   : bool              = False
        self._panel_rect      : Optional[tuple]   = None
        self._text             = "JOURNEY"
        self._letter_t         = [0.0] * len(self._text)
        self._coalesce_started = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        for key in ("Space", "Return", "Escape"):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._skip)

    # ── Star factory ─────────────────────────────────────────────────────────

    @staticmethod
    def _make_star(z_override: Optional[float] = None) -> dict:
        """
        Create a single star at a random position in 3D space.

        x, y — world-space lateral spread (centred on viewer axis).
        z     — depth; decreases each frame as star rushes toward viewer.
        vz    — THIS star's individual z-velocity; the core of the 3D effect.
        base_size — 1-4 px; grows further as z decreases (perspective scale).
        color — drawn from the spectral palette.
        """
        z = z_override if z_override is not None else random.uniform(_Z_NEAR + 1, _Z_FAR)
        return {
            "x":         random.uniform(-700, 700),
            "y":         random.uniform(-500, 500),
            "z":         float(z),
            "vz":        random.uniform(0.6, 9.0),     # <- each star's own speed
            "base_size": random.uniform(1.0, 4.0),
            "color":     random.choice(_STAR_COLORS),
            "trail":     random.uniform(0.2, 1.0),      # trail length factor
        }

    # ── Public ────────────────────────────────────────────────────────────────

    def show_flight(self):
        """Begin cinematic. Call once after showFullScreen()."""
        self._elapsed.start()
        self._timer.start(16)

    # ── Phase helper ──────────────────────────────────────────────────────────

    def _phase_info(self):
        ms = self._elapsed.elapsed()
        for i in range(len(_PHASE_START) - 1, -1, -1):
            if ms >= _PHASE_START[i]:
                inn = ms - _PHASE_START[i]
                return i, inn, min(1.0, inn / _PHASE_MS[i])
        return 0, ms, min(1.0, ms / _PHASE_MS[0])

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        ms              = self._elapsed.elapsed()
        phase, in_ms, t = self._phase_info()

        # Speed multiplier drives the 3D star engine the same way it drove
        # the old 2D radial engine — everything else is per-star velocity.
        if phase == _P_WARP:
            accel            = min(1.0, in_ms / 3_000)
            self._speed_mult = self._ease_in(accel) * 12 + 0.5
            self._warp_frozen_ms = in_ms
        elif phase == _P_APPROACH:
            # Decelerate smoothly — we are arriving at the JOURNEY panel
            self._speed_mult = (1.0 - self._ease_in_out(t)) * 9 + 0.1
        elif phase in (_P_GLYPH, _P_HOLD):
            self._speed_mult = 0.08    # gentle drift while glyphs land
        else:
            self._speed_mult = 0.0

        if self._speed_mult > 0.0:
            self._update_stars()

        if phase == _P_GLYPH:
            if not self._sprites_built:
                self._build_sprites()
            for sprite in self._sprites:
                sprite.update()
            settled = sum(1 for s in self._sprites if s.settled)
            if not self._coalesce_started and settled >= max(1, len(self._sprites) // 2):
                self._coalesce_started = True
            if self._coalesce_started:
                self._update_coalesce(t)

        elif phase == _P_HOLD:
            for sprite in self._sprites:
                sprite.update()
            self._letter_t = [1.0] * len(self._text)

        self.update()

        if ms >= _TOTAL_MS and not self._done:
            self._done = True
            self._timer.stop()
            self.flight_finished.emit()

    # ── 3D star advancement ───────────────────────────────────────────────────

    def _update_stars(self):
        """
        Advance every star along the Z axis by its OWN velocity scaled by the
        global speed multiplier.  When a star passes the viewer (z <= _Z_NEAR)
        it is reborn at the far end of the tunnel with a fresh random position.
        """
        for s in self._stars:
            s["z"] -= s["vz"] * self._speed_mult
            if s["z"] <= _Z_NEAR:
                # Star has flown past — recycle it far away
                new = self._make_star(z_override=float(_Z_FAR))
                s.update(new)

    # ── Build sprites ─────────────────────────────────────────────────────────

    def _build_sprites(self):
        self._sprites_built = True
        if self._panel_rect is None:
            return

        px, py, pw, ph = self._panel_rect
        w = self.width()  or 1920
        h = self.height() or 1080

        targets = [
            (px + pw * 0.18, py + ph * 0.38),
            (px + pw * 0.82, py + ph * 0.38),
            (px + pw * 0.50, py + ph * 0.22),
            (px + pw * 0.50, py + ph * 0.80),
            (px + pw * 0.28, py + ph * 0.68),
            (px + pw * 0.72, py + ph * 0.68),
        ]

        renderers = []
        for name in _GLYPH_NAMES:
            path = _GLYPH_DIR / name
            if _SVG_OK and path.exists():
                renderers.append(QSvgRenderer(str(path)))
            else:
                renderers.append(None)

        sizes      = [52, 44, 62, 40, 56, 48]
        rot_speeds = [-3.8, 4.2, -2.9, 3.5, -4.5, 3.0]

        for i, (renderer, (tx, ty)) in enumerate(zip(renderers, targets)):
            edge = i % 4
            if edge == 0:
                sx, sy = random.uniform(w * 0.2, w * 0.8), -100.0
            elif edge == 1:
                sx, sy = float(w + 100), random.uniform(h * 0.1, h * 0.9)
            elif edge == 2:
                sx, sy = random.uniform(w * 0.2, w * 0.8), float(h + 100)
            else:
                sx, sy = -100.0, random.uniform(h * 0.1, h * 0.9)

            self._sprites.append(GlyphSprite(
                renderer  = renderer,
                name      = _GLYPH_NAMES[i],
                sx        = sx,
                sy        = sy,
                tx        = tx,
                ty        = ty,
                size      = sizes[i],
                rot_speed = rot_speeds[i],
            ))

    # ── Coalesce text ─────────────────────────────────────────────────────────

    def _update_coalesce(self, phase_t: float):
        n = len(self._text)
        for i in range(n):
            start = (i / n) * 0.65
            if phase_t >= start:
                self._letter_t[i] = min(1.0, (phase_t - start) / 0.22)

    # ── Paint event ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        if not self._elapsed.isValid():
            return

        phase, in_ms, t = self._phase_info()
        cx      = self.width()  // 2
        cy      = self.height() // 2
        w       = self.width()
        h       = self.height()
        warp_ms = self._warp_frozen_ms if phase > _P_WARP else in_ms

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        if phase == _P_BLACK:
            pass   # pure black — The Crossing has just ended

        elif phase == _P_PINPOINT:
            self._draw_pinpoint(painter, cx, cy, t)

        elif phase == _P_WARP:
            self._draw_stars(painter, cx, cy)
            self._draw_nebulae(painter, cx, cy, w, h, t, in_ms)

        elif phase == _P_APPROACH:
            self._draw_stars(painter, cx, cy)
            self._draw_nebulae(painter, cx, cy, w, h, 1.0, warp_ms)
            self._draw_approach(painter, cx, cy, w, h, t)

        elif phase == _P_GLYPH:
            self._draw_stars(painter, cx, cy)
            self._draw_nebulae(painter, cx, cy, w, h, 1.0, warp_ms)
            self._draw_approach(painter, cx, cy, w, h, 1.0)
            self._draw_glyphs(painter)
            self._draw_coalescing_text(painter)

        elif phase == _P_HOLD:
            self._draw_stars(painter, cx, cy)
            self._draw_nebulae(painter, cx, cy, w, h, 1.0, warp_ms)
            self._draw_approach(painter, cx, cy, w, h, 1.0)
            self._draw_glyphs(painter)
            self._draw_coalescing_text(painter)

        painter.end()

    # ── Draw: pinpoint ────────────────────────────────────────────────────────

    def _draw_pinpoint(self, p: QPainter, cx: int, cy: int, t: float):
        a    = int(255 * self._ease_in(t))
        size = 1 + t * 3
        grad = QRadialGradient(cx, cy, size * 12)
        grad.setColorAt(0, QColor(210, 225, 255, a))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        r = int(size * 12)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        p.setBrush(QColor(255, 255, 255, a))
        sr = max(1, int(size))
        p.drawEllipse(cx - sr, cy - sr, sr * 2, sr * 2)

    # ── Draw: 3D perspective stars ────────────────────────────────────────────

    def _draw_stars(self, p: QPainter, cx: int, cy: int):
        """
        Project each star from 3D world space onto the 2D screen.

        screen_x = cx + star.x * FOCAL / star.z
        screen_y = cy + star.y * FOCAL / star.z
        pixel_r  = star.base_size * FOCAL / star.z   (grows as z->0)

        The trail is drawn from the star's PREVIOUS projected position
        (z + vz*speed_mult, i.e. where it was last frame) to the current one.
        Trail length is naturally longer for fast/close stars — no faking needed.
        """
        sm = self._speed_mult
        w  = self.width()
        h  = self.height()

        p.setPen(Qt.PenStyle.NoPen)

        for s in self._stars:
            z = s["z"]
            if z <= 0:
                continue

            # ── Perspective projection ──
            scale = _FOCAL / z
            sx    = cx + s["x"] * scale
            sy    = cy + s["y"] * scale

            # Cull stars outside the visible region (with margin)
            if sx < -60 or sx > w + 60 or sy < -60 or sy > h + 60:
                continue

            # ── Pixel size: 1 px pinpoint at depth -> up to 8 px close-up ──
            pix_r = s["base_size"] * scale
            pix_r = max(0.5, min(pix_r, 8.0))

            # ── Brightness: ramp up as star approaches ──
            proximity = 1.0 - (z / _Z_FAR)          # 0.0 (far) -> ~1.0 (near)
            alpha     = int(min(255, 55 + 200 * proximity))

            col      = s["color"]
            draw_col = QColor(col.red(), col.green(), col.blue(), alpha)

            # ── Speed trail ──
            # Project where the star WAS one frame ago (higher z = further away)
            z_prev = z + s["vz"] * sm
            if sm > 1.2 and z_prev < _Z_FAR and z_prev > 0:
                scale_prev = _FOCAL / z_prev
                px_prev    = cx + s["x"] * scale_prev
                py_prev    = cy + s["y"] * scale_prev

                # Trail alpha: fast/close stars burn bright streaks
                trail_strength = min(1.0, sm / 8.0) * s["trail"] * proximity
                trail_alpha    = int(alpha * 0.55 * trail_strength)

                if trail_alpha > 6:
                    trail_col = QColor(col.red(), col.green(), col.blue(), trail_alpha)
                    pen       = QPen(trail_col)
                    pen.setWidthF(max(0.3, pix_r * 0.45))
                    p.setPen(pen)
                    p.drawLine(int(px_prev), int(py_prev), int(sx), int(sy))
                    p.setPen(Qt.PenStyle.NoPen)

            # ── Draw star disc ──
            p.setBrush(draw_col)
            sr = max(1, int(pix_r))
            p.drawEllipse(int(sx) - sr, int(sy) - sr, sr * 2, sr * 2)

    # ── Draw: nebulae ─────────────────────────────────────────────────────────

    def _draw_nebulae(
        self, p: QPainter,
        cx: int, cy: int, w: int, h: int,
        warp_t: float, warp_ms: float,
    ):
        for idx, neb in enumerate(_NEBULAE):
            xf, yf, nr, ng, nb, rxf, ryf, drift, amax, appear_at = neb

            neb_t = max(0.0, (warp_t - appear_at) / max(0.001, 1.0 - appear_at))
            neb_a = int(255 * amax * min(1.0, neb_t * 2.5))
            if neb_a < 4:
                continue

            nx = int((0.5 + xf + drift * warp_ms) * w)
            ny = int((0.5 + yf) * h)
            rx = int(rxf * w)
            ry = int(ryf * h)

            grad = QRadialGradient(nx, ny, max(rx, ry))
            grad.setColorAt(0,   QColor(nr, ng, nb, neb_a))
            grad.setColorAt(0.5, QColor(nr, ng, nb, neb_a // 3))
            grad.setColorAt(1,   QColor(0, 0, 0, 0))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(nx - rx, ny - ry, rx * 2, ry * 2)

            # Cyan fly-through: tint the whole screen as we pass through #2
            if idx == _FLYTHROUGH_IDX:
                dist = abs(nx - cx)
                if dist < rx * 0.5:
                    tint_a = int(30 * (1.0 - dist / (rx * 0.5)))
                    p.fillRect(self.rect(), QColor(20, 155, 185, tint_a))

    # ── Draw: approach ────────────────────────────────────────────────────────

    def _draw_approach(
        self, p: QPainter,
        cx: int, cy: int, w: int, h: int, t: float,
    ):
        scale = math.sqrt(self._ease_in_out(t))
        pw    = int(8  + scale * (460 - 8))
        ph    = int(5  + scale * (290 - 5))
        px    = cx - pw // 2
        py    = cy - ph // 2

        self._panel_rect = (px, py, pw, ph)
        alpha = int(255 * min(1.0, t * 1.8))

        gr   = max(pw, ph) + 90
        grad = QRadialGradient(cx, cy, gr)
        grad.setColorAt(0, QColor(59, 120, 231, int(alpha * 0.30)))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - gr, cy - gr, gr * 2, gr * 2)

        p.setBrush(QColor(8, 18, 50, int(alpha * 0.88)))
        pen = QPen(QColor(59, 120, 231, alpha))
        pen.setWidth(2)
        p.setPen(pen)
        p.drawRect(px, py, pw, ph)

    # ── Draw: glyphs ──────────────────────────────────────────────────────────

    def _draw_glyphs(self, p: QPainter):
        for sprite in self._sprites:
            sprite.draw(p)

    # ── Draw: coalescing text ─────────────────────────────────────────────────

    def _draw_coalescing_text(self, p: QPainter):
        """
        "JOURNEY" letters scale 200%->100% and fade in one by one,
        coalescing from the energy of the settled Varuun glyphs.
        """
        if self._panel_rect is None:
            return

        px, py, pw, ph = self._panel_rect
        n       = len(self._text)
        font_sz = max(10, int(pw / (n + 2.0)))
        font    = QFont("Segoe UI", font_sz, QFont.Weight.Thin)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
        p.setFont(font)

        fm      = p.fontMetrics()
        char_w  = fm.horizontalAdvance("M") + 6
        total   = char_w * n
        x_start = px + (pw - total) // 2
        y_base  = py + ph // 2 + fm.ascent() // 2

        for i, (ch, lt) in enumerate(zip(self._text, self._letter_t)):
            if lt <= 0.0:
                continue

            scale = 2.0 - lt
            alpha = int(255 * lt)
            cx_l  = x_start + char_w * i + char_w // 2

            p.save()
            p.translate(cx_l, y_base - fm.ascent() // 2)
            p.scale(scale, scale)

            # Cobalt energy glow pass
            p.setPen(QColor(59, 120, 231, int(alpha * 0.45)))
            p.drawText(-char_w // 2, fm.ascent() // 2, ch)

            # Main letter — transitions cobalt -> bright white as it settles
            rr = int(155 + 100 * lt)
            gg = int(180 +  75 * lt)
            p.setPen(QColor(rr, gg, 255, alpha))
            p.drawText(-char_w // 2, fm.ascent() // 2, ch)

            p.restore()

    # ── Easing ────────────────────────────────────────────────────────────────

    @staticmethod
    def _ease_in(t: float) -> float:
        return t * t

    @staticmethod
    def _ease_in_out(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

    # ── Skip ──────────────────────────────────────────────────────────────────

    def _skip(self):
        if not self._done:
            self._done = True
            self._timer.stop()
            self.flight_finished.emit()

    def keyPressEvent(self, event):
        skip_keys = (
            Qt.Key.Key_Space, Qt.Key.Key_Return,
            Qt.Key.Key_Enter, Qt.Key.Key_Escape,
        )
        if event.key() in skip_keys:
            self._skip()
        else:
            super().keyPressEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  S T A N D A L O N E   T E S T
#  .venv\Scripts\python.exe ui\space_flight_widget.py
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SpaceFlightWidget()
    w.resize(1280, 720)
    w.setWindowTitle("SIG — Space Flight Widget  |  True 3D Perspective Starfield Edition")
    w.flight_finished.connect(
        lambda: (
            print("[TEST]  flight_finished emitted — JOURNEY begins!"),
            app.quit(),
        )
    )
    w.show()
    w.show_flight()
    sys.exit(app.exec())
