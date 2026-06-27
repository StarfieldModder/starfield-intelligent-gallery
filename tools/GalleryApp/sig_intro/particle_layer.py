# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: particle_layer.py
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
#  Version: 1.1
#  Created: May 2026
#
#  Notes:
#      This file is designed to be modular, extensible, and ready
#      for future enhancements including holographic effects,
#      parallax motion, particle dissolves, and sound integration.
# ================================================================
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
import random

class ParticleLayer(QWidget):
    """
    Simple particle dissolve layer for exit animation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.active = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_particles)

    # ------------------------------------------------------------
    # PUBLIC INITIALIZER (required by IntroPanel)
    # ------------------------------------------------------------
    def initialize(self):
        """
        Placeholder initializer for compatibility with IntroPanel.
        Future versions may load particle textures or shader effects.
        """
        print("[ParticleLayer] initialize() called.")
        self.show()

    # ------------------------------------------------------------
    # PARTICLE SYSTEM
    # ------------------------------------------------------------
    def start(self):
        self.active = True
        self._generate_particles()
        self.timer.start(30)

    def _generate_particles(self):
        width = self.width() or 800
        height = self.height() or 600

        self.particles = []
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            dx = random.uniform(-1.5, 1.5)
            dy = random.uniform(-1.5, 1.5)
            alpha = random.randint(150, 255)
            self.particles.append([x, y, dx, dy, alpha])

    def _update_particles(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 4
        self.update()

    # ------------------------------------------------------------
    # PAINT EVENT
    # ------------------------------------------------------------
    def paintEvent(self, event):
        if not self.active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for x, y, dx, dy, alpha in self.particles:
            if alpha > 0:
                painter.setPen(QColor(200, 220, 255, alpha))
                painter.drawPoint(int(x), int(y))
