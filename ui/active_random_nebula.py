# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║         A C T I V E   R A N D O M   N E B U L A              ║
# ║         Starfield Intelligent Gallery                        ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  active_random_nebula.py                        ║
# ║  Location  :  C:\SIG\ui\active_random_nebula.py              ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)      ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator)║
# ║  Version   :  2026.07.02 — Unicode-Safe Edition v2           ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  WHAT THIS FILE IS                                           ║
# ║                                                              ║
# ║  A living nebula overlay that breathes behind the five       ║
# ║  Carrier Deck panels. Five archetypes of cosmic cloud,       ║
# ║  each with its own colour, size, drift vector, and           ║
# ║  opacity pulse rhythm.                                       ║
# ║                                                              ║
# ║  FIVE ARCHETYPES                                             ║
# ║    Orion     — broad blue-white emission cloud               ║
# ║    Veil      — wispy violet supernova remnant                ║
# ║    Omega     — dense red-gold star-forming region            ║
# ║    Iris      — compact sapphire reflection cloud             ║
# ║    Flame     — warm amber diffuse glow                       ║
# ║                                                              ║
# ║  TRANSPARENT TO MOUSE                                        ║
# ║    WA_TransparentForMouseEvents — clicks pass through to     ║
# ║    the panels underneath.                                    ║
# ║                                                              ║
# ║  PUBLIC INTERFACE                                            ║
# ║    ActiveRandomNebula(parent, density=5)                     ║
# ║    .start()   — begin animation                              ║
# ║    .stop()    — stop animation                               ║
# ║                                                              ║
# ║  FIX LOG                                                     ║
# ║  2026.07.02 — Header converted from triple-quote docstring   ║
# ║               to # comments — eliminates unicode escape      ║
# ║               crash on Python 3.13 / Windows paths           ║
# ║  2026.07.02 — v2: Re-issued as fully unicode-safe file       ║
# ╚══════════════════════════════════════════════════════════════╝
# ================================================================

from __future__ import annotations

import math
import random
from typing import List

from PySide6.QtCore  import Qt, QTimer
from PySide6.QtGui   import (QColor, QPainter, QPainterPath,
                              QRadialGradient)
from PySide6.QtWidgets import QWidget


# ---------------------------------------------------------------------------
# Cloud archetype definitions
# ---------------------------------------------------------------------------

_ARCHETYPES = [
    # name,    base_color (R, G, B),   base_alpha, size_factor, drift_speed
    ("Orion",  (120, 160, 255),         38,         1.20,        0.18),
    ("Veil",   (180,  80, 220),         30,         0.90,        0.14),
    ("Omega",  (210, 140,  40),         35,         1.05,        0.20),
    ("Iris",   ( 60, 100, 210),         28,         0.75,        0.16),
    ("Flame",  (220, 110,  50),         32,         0.85,        0.22),
]


# ---------------------------------------------------------------------------
# Single nebula cloud
# ---------------------------------------------------------------------------

class _NebulaCloud:
    """One drifting, pulsing cloud blob."""

    def __init__(self, archetype: tuple, canvas_w: int, canvas_h: int):
        name, rgb, base_alpha, size_f, drift_spd = archetype
        self.name        = name
        self.rgb         = rgb
        self.base_alpha  = base_alpha
        self.size_f      = size_f
        self.drift_speed = drift_spd

        # Randomise position, size, pulse phase
        self.x  = random.uniform(0.05, 0.95) * canvas_w
        self.y  = random.uniform(0.05, 0.95) * canvas_h
        self.rx = random.uniform(0.15, 0.35) * canvas_w * size_f
        self.ry = random.uniform(0.10, 0.28) * canvas_h * size_f

        # Drift direction (slow, gentle)
        angle        = random.uniform(0, 2 * math.pi)
        spd          = drift_spd * random.uniform(0.5, 1.5)
        self.dx      = math.cos(angle) * spd
        self.dy      = math.sin(angle) * spd

        # Opacity pulse
        self.phase   = random.uniform(0, 2 * math.pi)
        self.pulse_f = random.uniform(0.4, 0.9)   # pulse frequency (rad/s)
        self.tick    = 0.0

        self._cw = canvas_w
        self._ch = canvas_h

    # ------------------------------------------------------------------
    def advance(self, dt: float) -> None:
        """Move and pulse the cloud."""
        self.tick += dt

        # Drift
        self.x += self.dx * dt * 60
        self.y += self.dy * dt * 60

        # Wrap around canvas edges (soft)
        margin = max(self.rx, self.ry)
        if self.x < -margin:
            self.x = self._cw + margin
        elif self.x > self._cw + margin:
            self.x = -margin
        if self.y < -margin:
            self.y = self._ch + margin
        elif self.y > self._ch + margin:
            self.y = -margin

    # ------------------------------------------------------------------
    def current_alpha(self) -> int:
        """Return current alpha (15–55) based on pulse."""
        pulse = math.sin(self.tick * self.pulse_f + self.phase)
        alpha = self.base_alpha + int(pulse * 12)
        return max(10, min(60, alpha))

    # ------------------------------------------------------------------
    def paint(self, painter: QPainter) -> None:
        alpha  = self.current_alpha()
        r, g, b = self.rgb

        grad = QRadialGradient(self.x, self.y, max(self.rx, self.ry))
        centre_color = QColor(r, g, b, alpha)
        edge_color   = QColor(r, g, b, 0)
        grad.setColorAt(0.0, centre_color)
        grad.setColorAt(0.5, QColor(r, g, b, alpha // 2))
        grad.setColorAt(1.0, edge_color)

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(self.x - self.rx), int(self.y - self.ry),
            int(self.rx * 2),       int(self.ry * 2)
        )


# ---------------------------------------------------------------------------
# Sparse star-field (tiny fixed dots for depth)
# ---------------------------------------------------------------------------

class _StarField:
    """A fixed field of tiny stars rendered under the nebula clouds."""

    def __init__(self, canvas_w: int, canvas_h: int, count: int = 120):
        self._stars: List[tuple] = []
        for _ in range(count):
            x     = random.uniform(0, canvas_w)
            y     = random.uniform(0, canvas_h)
            alpha = random.randint(60, 180)
            size  = random.uniform(0.5, 1.8)
            phase = random.uniform(0, 2 * math.pi)
            freq  = random.uniform(0.2, 0.7)
            self._stars.append((x, y, alpha, size, phase, freq))
        self._tick = 0.0

    def advance(self, dt: float) -> None:
        self._tick += dt

    def paint(self, painter: QPainter) -> None:
        painter.setPen(Qt.NoPen)
        for (x, y, base_alpha, size, phase, freq) in self._stars:
            twinkle = math.sin(self._tick * freq + phase)
            alpha   = int(base_alpha + twinkle * 40)
            alpha   = max(20, min(220, alpha))
            color   = QColor(220, 230, 255, alpha)
            painter.setBrush(color)
            painter.drawEllipse(
                int(x - size), int(y - size),
                int(size * 2),  int(size * 2)
            )


# ---------------------------------------------------------------------------
# Main widget
# ---------------------------------------------------------------------------

class ActiveRandomNebula(QWidget):
    """
    Living nebula overlay — sits behind the five Carrier Deck panels.

    Usage
    -----
        nebula = ActiveRandomNebula(parent=carrier_deck_widget, density=5)
        nebula.start()
    """

    # Tick interval in ms (≈30 fps)
    _TICK_MS = 33

    def __init__(self, parent: QWidget = None, density: int = 5):
        super().__init__(parent)

        # Transparent to mouse so panel clicks still work
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground,        True)
        self.setAttribute(Qt.WA_TranslucentBackground,     True)
        self.setWindowFlags(Qt.SubWindow)

        self._density  = max(1, min(density, 10))
        self._clouds:  List[_NebulaCloud]  = []
        self._stars:   _StarField | None   = None
        self._timer    = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._dt       = self._TICK_MS / 1000.0   # seconds per tick

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin the living nebula animation."""
        self._build_scene()
        self._timer.start(self._TICK_MS)

    def stop(self) -> None:
        """Pause the animation."""
        self._timer.stop()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_scene(self) -> None:
        w = self.width()  if self.width()  > 0 else 1280
        h = self.height() if self.height() > 0 else 720

        self._stars = _StarField(w, h, count=100 + self._density * 10)

        self._clouds.clear()
        for i in range(self._density):
            archetype = _ARCHETYPES[i % len(_ARCHETYPES)]
            self._clouds.append(_NebulaCloud(archetype, w, h))

        # Add a second pass of smaller accent clouds for richness
        for i in range(self._density):
            archetype = _ARCHETYPES[(i + 2) % len(_ARCHETYPES)]
            cloud = _NebulaCloud(archetype, w, h)
            cloud.rx *= 0.55
            cloud.ry *= 0.55
            cloud.base_alpha = max(10, cloud.base_alpha - 10)
            self._clouds.append(cloud)

    def _tick(self) -> None:
        dt = self._dt
        if self._stars:
            self._stars.advance(dt)
        for cloud in self._clouds:
            cloud.advance(dt)
        self.update()

    # ------------------------------------------------------------------
    # Qt painting
    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        # Rebuild the scene to match the new canvas size
        if self._clouds:
            self._build_scene()

    def paintEvent(self, event) -> None:   # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Clear to fully transparent
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Stars first (deepest layer)
        if self._stars:
            self._stars.paint(painter)

        # Nebula clouds on top
        for cloud in self._clouds:
            cloud.paint(painter)

        painter.end()
