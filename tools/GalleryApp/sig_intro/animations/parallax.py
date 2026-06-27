# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: animations/parallax.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Subsystem: Holographic Intro Panel / Creative Orientation Window
#
#  Description:
#      This module is part of the SIG Introductory Floating Panel,
#      a holographic, Starfield‑inspired UI subsystem that provides
#      users with an open‑ended creative orientation experience.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 1.0
#  Created: May 2026
#
#  Notes:
#      This file is designed to be modular, extensible, and ready
#      for future enhancements including holographic effects,
#      parallax motion, particle dissolves, and sound integration.
# ================================================================

class Parallax:
    """
    Computes tilt values based on cursor position for holographic parallax.
    """

    def __init__(self, widget=None, max_tilt=3.0):
        self.widget = widget
        self.max_tilt = max_tilt
        self.tilt_x = 0.0
        self.tilt_y = 0.0

        if widget:
            widget.setMouseTracking(True)

    def update_from_mouse(self, event):
        if not self.widget:
            print("[Parallax] No widget assigned yet.")
            return

        w = self.widget.width()
        h = self.widget.height()

        cx = w / 2
        cy = h / 2

        dx = (event.position().x() - cx) / cx
        dy = (event.position().y() - cy) / cy

        self.tilt_x = dx * self.max_tilt
        self.tilt_y = dy * self.max_tilt

        self.widget.update()
