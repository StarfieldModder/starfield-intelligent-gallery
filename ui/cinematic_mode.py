# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Cinematic Mode — Optional Add‑On Module
#
#  File: ui/cinematic_mode.py
#
#  Role:
#       Provides optional cinematic behaviors for SIG.
#       This module is intentionally separate from the minimal
#       ArtifactPanel so the core system remains stable.
#
#       When imported and used, it adds:
#           • alignment pulse
#           • slow reveal zoom
#           • flare burst
#           • transport fade
#           • ascension lift
#
#       If never imported, SIG runs in minimal mode.
#
#  Usage:
#       from ui.cinematic_mode import CinematicController
#       cine = CinematicController(artifact_panel)
#       cine.play_sequence()
#
#  Notes:
#       - All effects are optional.
#       - Missing assets never crash the app.
#       - This module does NOT modify ArtifactPanel itself.
# ================================================================

from PyQt6.QtCore import QTimer
import math


class CinematicController:
    """
    Optional cinematic controller for the minimal ArtifactPanel.
    This class orchestrates cinematic phases WITHOUT modifying
    the ArtifactPanel class itself.
    """

    def __init__(self, panel):
        self.panel = panel

    # ------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------
    def play_sequence(self,
                      alignment_ms=1400,
                      slow_reveal_ms=2200,
                      flare_ms=700,
                      transport_ms=900,
                      ascension_ms=1200):
        """Start the full cinematic sequence."""
        self._run_alignment(alignment_ms,
                            slow_reveal_ms,
                            flare_ms,
                            transport_ms,
                            ascension_ms)

    # ------------------------------------------------------------
    # Alignment
    # ------------------------------------------------------------
    def _run_alignment(self, duration, slow_reveal_ms, flare_ms, transport_ms, ascension_ms):
        self._align_elapsed = 0
        self._align_duration = duration

        self._align_timer = QTimer()
        self._align_timer.timeout.connect(
            lambda: self._alignment_tick(slow_reveal_ms, flare_ms, transport_ms, ascension_ms)
        )
        self._align_timer.start(50)

    def _alignment_tick(self, slow_reveal_ms, flare_ms, transport_ms, ascension_ms):
        self._align_elapsed += 50
        t = self._align_elapsed / float(self._align_duration)

        # Pulse arcs if present
        pulse = 1.0 + 0.05 * math.sin(self._align_elapsed / 120.0)
        for it in (self.panel.arc_outer_item,
                   self.panel.arc_inner_item,
                   self.panel.arc_orbit_item,
                   self.panel.arc_core_item):
            if it is not None:
                it.setScale(pulse)

        if self._align_elapsed >= self._align_duration:
            self._align_timer.stop()
            # restore
            for it in (self.panel.arc_outer_item,
                       self.panel.arc_inner_item,
                       self.panel.arc_orbit_item,
                       self.panel.arc_core_item):
                if it is not None:
                    it.setScale(1.0)
            self._run_slow_reveal(slow_reveal_ms, flare_ms, transport_ms, ascension_ms)

    # ------------------------------------------------------------
    # Slow reveal
    # ------------------------------------------------------------
    def _run_slow_reveal(self, duration, flare_ms, transport_ms, ascension_ms):
        self._sr_elapsed = 0
        self._sr_duration = duration

        # capture initial scales
        self._initial_scales = {}
        for it in (self.panel.arc_outer_item,
                   self.panel.arc_inner_item,
                   self.panel.arc_orbit_item,
                   self.panel.arc_core_item):
            if it is not None:
                self._initial_scales[it] = it.scale()

        self._sr_timer = QTimer()
        self._sr_timer.timeout.connect(
            lambda: self._slow_reveal_tick(flare_ms, transport_ms, ascension_ms)
        )
        self._sr_timer.start(33)

    def _slow_reveal_tick(self, flare_ms, transport_ms, ascension_ms):
        self._sr_elapsed += 33
        t = min(1.0, self._sr_elapsed / float(self._sr_duration))
        eased = (3 * t * t) - (2 * t * t * t)

        # slow rotation
        if self.panel.arc_orbit_item is not None:
            self.panel.arc_orbit_item.setRotation(
                self.panel.arc_orbit_item.rotation() + 0.06 * (1.0 - eased)
            )

        # subtle zoom
        for it, s0 in self._initial_scales.items():
            it.setScale(s0 * (1.0 + 0.06 * eased))

        if self._sr_elapsed >= self._sr_duration:
            self._sr_timer.stop()
            self._run_flare(flare_ms, transport_ms, ascension_ms)

    # ------------------------------------------------------------
    # Flare
    # ------------------------------------------------------------
    def _run_flare(self, duration, transport_ms, ascension_ms):
        self._flare_elapsed = 0
        self._flare_duration = duration

        self._flare_timer = QTimer()
        self._flare_timer.timeout.connect(
            lambda: self._flare_tick(transport_ms, ascension_ms)
        )
        self._flare_timer.start(33)

    def _flare_tick(self, transport_ms, ascension_ms):
        self._flare_elapsed += 33
        t = min(1.0, self._flare_elapsed / float(self._flare_duration))

        if self.panel.arc_core_item is not None:
            self.panel.arc_core_item.setOpacity(0.6 + 0.4 * t)
            self.panel.arc_core_item.setScale(1.0 + 0.08 * t)

        if self._flare_elapsed >= self._flare_duration:
            self._flare_timer.stop()
            if self.panel.arc_core_item is not None:
                self.panel.arc_core_item.setOpacity(1.0)
                self.panel.arc_core_item.setScale(1.0)
            self._run_transport(transport_ms, ascension_ms)

    # ------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------
    def _run_transport(self, duration, ascension_ms):
        self._tr_elapsed = 0
        self._tr_duration = duration

        self._tr_timer = QTimer()
        self._tr_timer.timeout.connect(
            lambda: self._transport_tick(ascension_ms)
        )
        self._tr_timer.start(33)

    def _transport_tick(self, ascension_ms):
        self._tr_elapsed += 33
        t = min(1.0, self._tr_elapsed / float(self._tr_duration))

        scale = 1.0 - 0.6 * t
        opacity = 1.0 - 0.9 * t

        for it in (self.panel.arc_outer_item,
                   self.panel.arc_inner_item,
                   self.panel.arc_orbit_item,
                   self.panel.arc_core_item):
            if it is not None:
                it.setScale(scale)
                it.setOpacity(opacity)

        if self._tr_elapsed >= self._tr_duration:
            self._tr_timer.stop()
            self._run_ascension(ascension_ms)

    # ------------------------------------------------------------
    # Ascension
    # ------------------------------------------------------------
    def _run_ascension(self, duration):
        self._asc_elapsed = 0
        self._asc_duration = duration

        self._asc_timer = QTimer()
        self._asc_timer.timeout.connect(self._ascension_tick)
        self._asc_timer.start(33)

    def _ascension_tick(self):
        self._asc_elapsed += 33
        t = min(1.0, self._asc_elapsed / float(self._asc_duration))

        dy = -40.0 * t
        opacity = 1.0 - 0.8 * t

        for it in (self.panel.arc_outer_item,
                   self.panel.arc_inner_item,
                   self.panel.arc_orbit_item,
                   self.panel.arc_core_item):
            if it is not None:
                it.setY(dy)
                it.setOpacity(opacity)

        if self._asc_elapsed >= self._asc_duration:
            self._asc_timer.stop()
