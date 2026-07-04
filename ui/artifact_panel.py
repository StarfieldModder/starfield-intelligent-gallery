# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║              A R T I F A C T   P A N E L                     ║
# ║              Starfield Intelligent Gallery — Minimal Edition  ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  artifact_panel.py                               ║
# ║  Location  :  C:\SIG\ui\artifact_panel.py                     ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)       ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator) ║
# ║  Version   :  2026.07.01 — Carrier Deck Edition               ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  WHAT CHANGED vs original                                     ║
# ║  • STARFIELD_PATH and StarfieldLayer are RETIRED.            ║
# ║    starfield_soft.png is superseded by The Crossing MP4      ║
# ║    played through IntroPanelWidget / sig_layer_video.py.     ║
# ║  • _load_starfield() now skips the PNG load silently —       ║
# ║    the method is kept as a no-op so any legacy callers       ║
# ║    that call it directly don't crash.                        ║
# ║  • Arc PNGs (arc_outer, arc_inner, arc_orbit, arc_core)      ║
# ║    still load defensively — unchanged.                        ║
# ║  • Shimmer timer removed (no PNG to shimmer).                ║
# ╚══════════════════════════════════════════════════════════════╝

from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

import os

# ------------------------------------------------------------
# Arc asset paths — still active, load defensively
# ------------------------------------------------------------
ARC_OUTER = r"C:\SIG\Assets\arcs\arc_outer.png"
ARC_INNER = r"C:\SIG\Assets\arcs\arc_inner.png"
ARC_ORBIT = r"C:\SIG\Assets\arcs\arc_orbit.png"
ARC_CORE  = r"C:\SIG\Assets\arcs\arc_core.png"

# STARFIELD_PATH is intentionally NOT defined here.
# starfield_soft.png is RETIRED — The Crossing MP4 owns the background.
# The physical file at C:\SIG\Assets\starfield_soft.png is left in place
# (legacy code outside this file may still reference it directly).


# ============================================================
# Minimal Artifact Panel
# ============================================================
class ArtifactPanel(QWidget):
    """
    Minimal, stable Artifact Panel.

    Loads arc PNGs if present (still used by ArtifactReveal overlays).
    No longer loads starfield_soft.png — video layer owns the background.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Scene + view (kept for arc-overlay and glyph geometry)
        self.scene = QGraphicsScene(self)
        self.view  = QGraphicsView(self.scene, self)
        self.view.setRenderHints(self.view.renderHints())
        self.view.setStyleSheet("background: transparent; border: none;")

        # Layout — view fills the panel
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # Arc items (None until loaded)
        self.arc_outer_item = None
        self.arc_inner_item = None
        self.arc_orbit_item = None
        self.arc_core_item  = None

        # Starfield is RETIRED — attribute kept as None so callers
        # that check self.starfield won't crash.
        self.starfield = None

        # Load remaining assets
        self._load_arcs()

    # ── No-op stub kept for API compat ───────────────────────────────────
    def _load_starfield(self) -> None:
        """
        RETIRED — starfield_soft.png is superseded by The Crossing MP4.
        This stub exists purely so legacy call-sites don't raise AttributeError.
        """
        self.starfield = None

    # ── Arc loading ───────────────────────────────────────────────────────
    def _load_arcs(self) -> None:
        arc_defs = [
            (ARC_OUTER, "arc_outer_item"),
            (ARC_INNER, "arc_inner_item"),
            (ARC_ORBIT, "arc_orbit_item"),
            (ARC_CORE,  "arc_core_item"),
        ]
        for path, attr in arc_defs:
            if os.path.exists(path):
                pix  = QPixmap(path)
                item = QGraphicsPixmapItem(pix)
                self.scene.addItem(item)
                setattr(self, attr, item)
            else:
                setattr(self, attr, None)
