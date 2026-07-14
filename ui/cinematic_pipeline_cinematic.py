"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗██████╗ ███████╗██╗     ██╗███╗   ██╗███████╗                   ║
║   ██╔══██╗██║██╔══██╗██╔════╝██║     ██║████╗  ██║██╔════╝                   ║
║   ██████╔╝██║██████╔╝█████╗  ██║     ██║██╔██╗ ██║█████╗                     ║
║   ██╔═══╝ ██║██╔═══╝ ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝                     ║
║   ██║     ██║██║     ███████╗███████╗██║██║ ╚████║███████╗                   ║
║   ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝                   ║
║                                                                              ║
║              C I N E M A T I C   P I P E L I N E                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  cinematic_pipeline_cinematic.py                               ║
║  Location   :  C:\SIG\ui\cinematic_pipeline_cinematic.py                     ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineering Collaborator)               ║
║  Version    :  2026.07.01 — Carrier Deck Edition                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT CHANGED vs stacking-fix build                                          ║
║                                                                              ║
║  • set_background() now accepts an OPTIONAL path.  When path is None         ║
║    (the new default), the background is set to solid black — no PNG          ║
║    is required.  This retires the starfield_soft.png dependency from         ║
║    this module entirely.                                                     ║
║  • starfield_soft.png is still accepted if you pass its path explicitly      ║
║    (backward-compatible with any code that calls set_background(path)).      ║
║  • The physical file at C:\SIG\Assets\starfield_soft.png is left on disk     ║
║    — other legacy code may still reference it.  This file just won't         ║
║    use it by default any more.                                               ║
║                                                                              ║
║  ARCHITECTURE                                                                ║
║  Absolute child geometry for deterministic z-stacking:                       ║
║    self.bg       (QLabel)         — fills widget, painted or black           ║
║    self.artifact (ArtifactReveal) — overlay raised above bg                  ║
║                                                                              ║
║  METHODS                                                                     ║
║    set_background(path=None)   — load PNG or go solid black                  ║
║    fade_in(ms=1200)            — QPropertyAnimation on bg opacity            ║
║    fade_out(ms=800)            — reverse fade                                ║
║    play_artifact_reveal()      — halo + glyph reveal sequence                ║
║    play_temple_sequence()      — Cosmic Choice panel sequence                ║
║    update_breath()             — ambient light-breathing (timer slot)        ║
║    ESC                         — exits the window                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import (
    QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt, QTimer,
)
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from ui.artifact_reveal import ArtifactReveal


class CinematicPipeline(QWidget):
    """
    SIG Cinematic Engine Pipeline.

    Uses absolute child geometry so layer z-stacking is deterministic.
    Background is a QLabel; ArtifactReveal overlay sits above it.

    set_background() accepts an optional image path.  When omitted
    (or when the path does not exist), the background is solid black —
    starfield_soft.png is no longer required.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # ── Background layer (child label, absolute geometry) ──────────────
        self.bg = QLabel(self)
        self.bg.setScaledContents(True)
        self.bg.setStyleSheet("background-color: black;")
        self.bg.setVisible(True)

        # ── Artifact overlay — glyph + resonance rings ─────────────────────
        self.artifact = ArtifactReveal(self)
        self.artifact.setVisible(True)

        # Stacking: bg behind, artifact in front
        self.bg.lower()
        self.artifact.raise_()

        # Keep animation references alive (prevent GC)
        self._active_animations: list = []

        # ── Ambient breathing timer (~25 FPS) ──────────────────────────────
        self.breath_timer = QTimer(self)
        self.breath_timer.setInterval(40)
        self.breath_timer.timeout.connect(self.update_breath)
        self.breath_phase = 0.0

        # Run startup geometry check after construction
        QTimer.singleShot(200, self._startup_debug)

    # ── Ensure children fill widget ────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        self.bg.setGeometry(0, 0, w, h)
        self.artifact.setGeometry(0, 0, w, h)
        self.artifact.raise_()

    # ── Background ─────────────────────────────────────────────────────────

    def set_background(self, path: Optional[str] = None) -> None:
        """
        Set the background image.

        Parameters
        ----------
        path : str or None
            Path to a PNG/JPG to display as background.
            If None, missing, or invalid, the background stays solid black.

        Notes
        -----
        starfield_soft.png is RETIRED — do NOT pass it here by default.
        The video layer (IntroPanelWidget / crossing_FINAL.mp4) owns the
        background during the intro sequence.  This method is used only for
        still-image backgrounds in later cinematic scenes (temple frames, etc.).
        """
        if path and os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.bg.setPixmap(pix)
                self.bg.setStyleSheet("")          # let image show through
                return

        # Fallback — solid black (no PNG required)
        self.bg.setPixmap(QPixmap())              # clear any previous image
        self.bg.setStyleSheet("background-color: black;")

    # ── Fades ──────────────────────────────────────────────────────────────

    def fade_in(self, duration_ms: int = 1200) -> None:
        """Fade the background layer in from transparent."""
        anim = QPropertyAnimation(self.bg, b"windowOpacity", self)
        anim.setDuration(duration_ms)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._active_animations.append(anim)
        anim.start()

    def fade_out(self, duration_ms: int = 800) -> None:
        """Fade the background layer out to transparent."""
        anim = QPropertyAnimation(self.bg, b"windowOpacity", self)
        anim.setDuration(duration_ms)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._active_animations.append(anim)
        anim.start()

    # ── Cinematic sequences ────────────────────────────────────────────────

    def play_artifact_reveal(self) -> None:
        """
        Halo + glyph reveal sequence via ArtifactReveal overlay.
        Starts the ambient breathing timer after the reveal completes.
        """
        self.artifact.start_reveal()
        QTimer.singleShot(2000, self.breath_timer.start)

    def play_temple_sequence(self) -> None:
        """
        Cosmic Choice Panel sequence — scenes 03–05.

        Delegates to cinematic_mode_v2 scene definitions once concrete
        Panel/AudioEngine implementations are wired in.
        Currently schedules the artifact reveal as a stand-in.
        """
        print("[CinematicPipeline] Temple sequence — beginning.")
        # Scene 03: The Breath Before Motion — fade to dark
        QTimer.singleShot(0,    lambda: self.fade_out(1000))
        # Scene 04: Resonance — artifact reveal with full halo
        QTimer.singleShot(1200, self.play_artifact_reveal)
        # Scene 05: Threshold — fade back to reveal the Cosmic Choice Panel
        QTimer.singleShot(4000, lambda: self.fade_in(1500))

    # ── Ambient breathing ──────────────────────────────────────────────────

    def update_breath(self) -> None:
        """
        Gentle sine-wave brightness modulation on the background layer.
        Called by breath_timer at ~25 FPS.
        """
        import math
        self.breath_phase += 0.035
        opacity = 0.88 + 0.12 * math.sin(self.breath_phase)
        self.bg.setWindowOpacity(opacity)

    # ── Debug ──────────────────────────────────────────────────────────────

    def _startup_debug(self) -> None:
        w, h = self.width(), self.height()
        print(f"[CinematicPipeline] startup geometry: {w}×{h}")
        if w == 0 or h == 0:
            print("[CinematicPipeline] WARNING: zero-size on startup — "
                  "resizeEvent will fix on first show.")

    # ── Keyboard ───────────────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            window = self.window()
            if window:
                window.close()
        else:
            super().keyPressEvent(event)
