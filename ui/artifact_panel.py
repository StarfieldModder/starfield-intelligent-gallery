# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Artifact Panel — Minimal Stable Edition (No Cinematics)
#
#  File: ui/artifact_panel.py
#
#  Role:
#       Provides a clean, safe, minimal ArtifactPanel widget.
#       Loads the starfield background and optional arc PNGs.
#       No animations, no flare, no alignment, no cinematic logic.
#
#  Launch Command:
#       python C:\SIG\sig_main.py
#
#  Notes:
#       - This version is intentionally simple and stable.
#       - All assets load defensively (missing files never crash).
#       - Only the starfield shimmer is active.
# ================================================================

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QUrl
import os
import math

from PySide6.QtWidgets import QGraphicsView

from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene



# ------------------------------------------------------------
# Asset paths (safe if missing)
# ------------------------------------------------------------
ARC_OUTER = r"C:\SIG\Assets\arcs\arc_outer.png"
ARC_INNER = r"C:\SIG\Assets\arcs\arc_inner.png"
ARC_ORBIT = r"C:\SIG\Assets\arcs\arc_orbit.png"
ARC_CORE  = r"C:\SIG\Assets\arcs\arc_core.png"

STARFIELD_PATH = r"C:\SIG\Assets\starfield_soft.png"


# ============================================================
# Starfield shimmer layer
# ============================================================
class StarfieldLayer(QGraphicsPixmapItem):
    """Simple JWST‑style shimmer effect."""
    def __init__(self, pixmap: QPixmap):
        super().__init__(pixmap)
        self.setOffset(-pixmap.width() / 2, -pixmap.height() / 2)
        self.phase = 0.0

    def update_shimmer(self):
        self.phase += 0.003
        opacity = 0.85 + 0.15 * (0.5 + 0.5 * math.sin(self.phase))
        self.setOpacity(opacity)


# ============================================================
# Minimal Artifact Panel
# ============================================================
class ArtifactPanel(QWidget):
    """
    Minimal, stable Artifact Panel.
    Loads starfield + arcs (if present).
    No cinematic features.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Allow key events if needed later
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Scene + view
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHints(self.view.renderHints())

        # Items
        self.starfield = None
        self.arc_outer_item = None
        self.arc_inner_item = None
        self.arc_orbit_item = None
        self.arc_core_item = None

        # Load assets
        self._load_starfield()
        self._load_arcs()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Only shimmer timer (safe)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)

    # --------------------------------------------------------
    # Asset loading
    # --------------------------------------------------------
    def _load_starfield(self):
        if os.path.exists(STARFIELD_PATH):
            pix = QPixmap(STARFIELD_PATH)
            if not pix.isNull():
                self.starfield = StarfieldLayer(pix)
                self.scene.addItem(self.starfield)

    def _safe_add_pixmap(self, path: str):
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                item = QGraphicsPixmapItem(pix)
                item.setOffset(-pix.width() / 2, -pix.height() / 2)
                self.scene.addItem(item)
                return item
        return None

    def _load_arcs(self):
        self.arc_outer_item = self._safe_add_pixmap(ARC_OUTER)
        self.arc_inner_item = self._safe_add_pixmap(ARC_INNER)
        self.arc_orbit_item = self._safe_add_pixmap(ARC_ORBIT)
        self.arc_core_item  = self._safe_add_pixmap(ARC_CORE)

        # Simple z‑order
        z = 0
        for it in (
            self.arc_orbit_item,
            self.arc_outer_item,
            self.arc_inner_item,
            self.arc_core_item
        ):
            if it is not None:
                it.setZValue(z)
                z += 1

    # --------------------------------------------------------
    # Internal tick (only shimmer + center)
    # --------------------------------------------------------
    def _tick(self):
        if self.starfield is not None:
            self.starfield.update_shimmer()

        # Keep view centered
        self.view.centerOn(0, 0)
