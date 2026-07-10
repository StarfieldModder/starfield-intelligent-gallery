# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: animations/scanline.py
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

from PyQt6.QtCore import QTimer

class Scanline:
    """
    Provides a vertical scanline effect for holographic panels.
    """

    def __init__(self, panel=None, speed=3, interval=40):
        self.panel = panel
        self.speed = speed
        self.position = 0

        self.timer = None
        if panel:
            self.timer = QTimer(panel)
            self.timer.timeout.connect(self._advance)
            self.timer.start(interval)

    def _advance(self):
        if not self.panel:
            print("[Scanline] No panel assigned yet.")
            return

        self.position = (self.position + self.speed) % max(1, self.panel.height())
        self.panel.update()
