# FRAGMENT ORCHESTRATOR
# Starfield Intelligent Gallery · 2026.07.25
# Author: Mark J. Latsha (Games)
# Co‑Author: Microsoft Copilot (AI Engineer Colleague)

from __future__ import annotations
import math
from typing import Callable, List, Optional

from core.diagnostic_reporter import record_error


class FragmentOrchestrator:
    """
    The unified conductor for all AncientFragment instances.
    Responsibilities:
      • Observe fragment state changes
      • Broadcast cinematic events to Companion Mode
      • Synchronize outer ring rotation / glow
      • Drive inscription reveal timelines
      • Provide a clean, minimal API for SIG engines
    """

    def __init__(self):
        try:
            self.fragments: List = []
            self._t: float = 0.0

            # Companion Mode hooks (user‑assignable)
            self.on_select: Optional[Callable] = None
            self.on_dim: Optional[Callable] = None
            self.on_settle: Optional[Callable] = None
            self.on_reveal: Optional[Callable] = None

            # Outer Ring hooks
            self.on_outer_ring_pulse: Optional[Callable] = None
            self.on_outer_ring_sync: Optional[Callable] = None

        except Exception as exc:
            record_error("fragment_orchestrator", "__init__", 0,
                         type(exc).__name__, str(exc), "critical", exc)

    # ──────────────────────────────────────────────────────────────────────────
    # Registration
    # ──────────────────────────────────────────────────────────────────────────

    def register(self, fragment) -> None:
        """Add a fragment to the orchestrator."""
        try:
            self.fragments.append(fragment)
        except Exception as exc:
            record_error("fragment_orchestrator", "register", 0,
                         type(exc).__name__, str(exc), "warning", exc)

    # ──────────────────────────────────────────────────────────────────────────
    # Update Loop
    # ──────────────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        """
        Called once per frame by SIG's main loop.
        Drives fragment updates, inscription reveals, and cinematic sync.
        """
        try:
            self._t += dt

            for frag in self.fragments:
                prev_state = getattr(frag, "state", None)
                # allow frag.update to accept current time or dt depending on implementation
                try:
                    frag.update(self._t)
                except TypeError:
                    frag.update(dt)

                # Detect state transitions
                if prev_state != getattr(frag, "state", None):
                    self._handle_state_change(frag, prev_state, frag.state)

                # Drive inscription reveal (Companion Mode controlled)
                if getattr(frag, "settled", False) and getattr(frag, "inscription", 1.0) < 1.0:
                    frag.inscription += dt * 0.35
                    if frag.inscription > 1.0:
                        frag.inscription = 1.0
                        if self.on_reveal:
                            try:
                                self.on_reveal(frag)
                            except Exception as exc:
                                record_error("fragment_orchestrator", "on_reveal", 0,
                                             type(exc).__name__, str(exc), "warning", exc)

                # Sync outer ring rotation with fragment breath
                if self.on_outer_ring_sync and getattr(frag, "settled", False):
                    breath = math.sin(self._t * getattr(frag, "_breath_speed", 1.0)
                                      + getattr(frag, "_breath_phase", 0.0))
                    try:
                        self.on_outer_ring_sync(frag, breath)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_outer_ring_sync", 0,
                                     type(exc).__name__, str(exc), "warning", exc)

        except Exception as exc:
            record_error("fragment_orchestrator", "update", 0,
                         type(exc).__name__, str(exc), "critical", exc)

    # ──────────────────────────────────────────────────────────────────────────
    # State Change Handling
    # ──────────────────────────────────────────────────────────────────────────

    def _handle_state_change(self, frag, old, new) -> None:
        """Broadcast cinematic events to Companion Mode + Outer Ring."""
        try:
            # Use attributes on frag for state constants if present
            SELECTED = getattr(frag, "SELECTED", "selected")
            DIMMED = getattr(frag, "DIMMED", "dimmed")
            SETTLED = getattr(frag, "SETTLED", "settled")

            if new == SELECTED:
                if self.on_select:
                    try:
                        self.on_select(frag)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_select", 0,
                                     type(exc).__name__, str(exc), "warning", exc)
                if self.on_outer_ring_pulse:
                    try:
                        self.on_outer_ring_pulse(frag)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_outer_ring_pulse", 0,
                                     type(exc).__name__, str(exc), "warning", exc)

            elif new == DIMMED:
                if self.on_dim:
                    try:
                        self.on_dim(frag)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_dim", 0,
                                     type(exc).__name__, str(exc), "warning", exc)

            elif new == SETTLED:
                if self.on_settle:
                    try:
                        self.on_settle(frag)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_settle", 0,
                                     type(exc).__name__, str(exc), "warning", exc)
                if self.on_outer_ring_pulse:
                    try:
                        self.on_outer_ring_pulse(frag)
                    except Exception as exc:
                        record_error("fragment_orchestrator", "on_outer_ring_pulse", 0,
                                     type(exc).__name__, str(exc), "warning", exc)

        except Exception as exc:
            record_error("fragment_orchestrator", "_handle_state_change", 0,
                         type(exc).__name__, str(exc), "warning", exc)
