# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: animations/dissolve.py
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

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class Dissolve:
    """
    Handles fade-out dissolve animation for holographic panels.
    """

    def __init__(self, widget=None, duration=700):
        self.widget = widget

        # Some SIG modules may not pass a widget yet
        if widget and hasattr(widget, "opacity_effect"):
            self.effect = widget.opacity_effect
        else:
            self.effect = None

        self.anim = None
        if self.effect:
            self.anim = QPropertyAnimation(self.effect, b"opacity", widget)
            self.anim.setDuration(duration)
            self.anim.setStartValue(1.0)
            self.anim.setEndValue(0.0)
            self.anim.setEasingCurve(QEasingCurve.Type.InQuad)

    def start(self, on_finished=None):
        if not self.anim:
            print("[Dissolve] No widget/effect assigned yet.")
            return

        if on_finished:
            self.anim.finished.connect(on_finished)

        self.anim.start()
