# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: intro_panel.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Subsystem: Holographic Intro Panel / Creative Orientation Window
#
#  Description:
#      Step 3: Hologram activation layer. Provides fade-in animation,
#      glyph pulse, and shimmer overlay for the SIG Intro Panel.
#      This module is the core of the holographic reveal sequence.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 3.0
#  Created: May 2026
#
#  Notes:
#      - Fade-in animation for the entire panel.
#      - Glyph pulse animation (soft glow).
#      - Holographic shimmer overlay.
#      - Ready for Step 3B orchestration in intro_panel_widget.py.
# ================================================================

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor, QPainter, QFont


class IntroPanel(QWidget):
    """
    Holographic Intro Panel with fade-in, glyph pulse, and shimmer.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ------------------------------------------------------------
        # SIG GLYPH (placeholder text for now)
        # ------------------------------------------------------------
        self.glyph = QLabel("SIG")
        self.glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.glyph.setStyleSheet("color: white;")
        self.glyph.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))

        self.layout.addWidget(self.glyph)

        # Opacity for fade-in
        self.setWindowOpacity(0.0)

        # Start fade-in after widget is shown
        QTimer.singleShot(300, self._start_fade_in)

        # Start glyph pulse after fade-in begins
        QTimer.singleShot(800, self._start_glyph_pulse)

    # ------------------------------------------------------------
    # FADE-IN ANIMATION
    # ------------------------------------------------------------
    def _start_fade_in(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(1200)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

    # ------------------------------------------------------------
    # GLYPH PULSE ANIMATION
    # ------------------------------------------------------------
    def _start_glyph_pulse(self):
        self.pulse_anim = QPropertyAnimation(self.glyph, b"styleSheet")
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setLoopCount(-1)

        self.pulse_anim.setStartValue("color: rgba(255, 255, 255, 180);")
        self.pulse_anim.setEndValue("color: rgba(255, 255, 255, 255);")

        self.pulse_anim.start()

    # ------------------------------------------------------------
    # HOLOGRAPHIC SHIMMER OVERLAY
    # ------------------------------------------------------------
    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Soft shimmer pass
        shimmer = QColor(255, 255, 255, 18)
        painter.fillRect(self.rect(), shimmer)

