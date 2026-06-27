# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: sig_launcher.py
# Module: Combined Launcher (Starfield + Intro Panel)
# Version: 2026.05.28 — Unified Cinematic Edition (Stabilized)
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# Location: Brentwood, California — Pacific Daylight Time
#
# Description:
#     This module launches the full SIG cinematic intro:
#         - Fullscreen StarfieldBackground (Jump Cruise Edition)
#         - IntroPanelWidget layered on top
#         - ENGAGE triggers the Grav-Drive Jump Cruise
#
# Notes:
#     - This is the correct unified launcher for SIG.
#     - Fixed early-resize timing bug (background now initialized safely).
#     - Can be run directly from VS Code using:
#           python "${file}"
#
# Timestamp:
#     Generated: May 28, 2026 — 7:12 AM PDT
# ================================================================

from __future__ import annotations
import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

from starfield_background import StarfieldBackground
from ui.intro_panel_widget import IntroPanelWidget


class SIGLauncher(QWidget):
    """
    Combines the StarfieldBackground and IntroPanelWidget
    into a single cinematic window.
    """

    def __init__(self, app: QApplication):
        super().__init__()

        # ------------------------------------------------------------
        # Initialize attributes BEFORE resize events can fire
        # ------------------------------------------------------------
        self.background = None
        self.panel = None
        self.app = app

        # ------------------------------------------------------------
        # Window setup
        # ------------------------------------------------------------
        self.setWindowTitle("Starfield Intelligent Gallery")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.showFullScreen()

        # ------------------------------------------------------------
        # Create starfield background (fills entire window)
        # ------------------------------------------------------------
        self.background = StarfieldBackground(self)
        self.background.setGeometry(self.rect())
        self.background.show()

        # ------------------------------------------------------------
        # Create intro panel (layered on top)
        # ------------------------------------------------------------
        self.panel = IntroPanelWidget(self.app, parent=self)
        self.panel.set_background(self.background)
        self.panel.show_panel()

    # ------------------------------------------------------------
    # Resize handling
    # ------------------------------------------------------------
    def resizeEvent(self, event):
        # Keep background full-screen on resize
        if self.background is not None:
            self.background.setGeometry(self.rect())
        super().resizeEvent(event)


# ================================================================
# Standalone Launch Harness
# ================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = SIGLauncher(app)
    sys.exit(app.exec())
