# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: animations/drift.py
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

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint

class Drift:
    """
    Applies a slow, looping microgravity drift motion to a widget.
    """

    def __init__(self, widget=None, x_range=(-4, 4), y_range=(-2, 2), duration=8000):
        self.widget = widget
        self.anim = None

        # Only build the animation if a widget is provided
        if widget:
            self.anim = QPropertyAnimation(widget, b"driftOffset", widget)
            self.anim.setDuration(duration)
            self.anim.setStartValue(QPoint(x_range[0], y_range[0]))
            self.anim.setEndValue(QPoint(x_range[1], y_range[1]))
            self.anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            self.anim.setLoopCount(-1)

    def start(self):
        if not self.anim:
            print("[Drift] No widget assigned yet.")
            return

        self.anim.start()
