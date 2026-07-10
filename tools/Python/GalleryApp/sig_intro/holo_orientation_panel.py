# ================================================================
#  STARFIELD INTELLIGENT GALLERY — INTRODUCTORY FLOATING PANEL
#  Module: holo_orientation_panel.py
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
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty

from .holo_glyph_button import HoloGlyphButton
from .sound_bus import SoundBus

class HoloOrientationPanel(QWidget):
    """
    The floating holographic intro panel.
    """
    def __init__(self, sound_bus: SoundBus | None = None, parent=None):
        super().__init__(parent)
        self.sound_bus = sound_bus

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)

        self._drift_offset = QPoint(0, 0)
        self._tilt_x = 0.0
        self._tilt_y = 0.0

        self._setup_layout()
        self._setup_opacity()
        self._setup_scanline()
        self._setup_drift_animation()

        if self.sound_bus:
            self.sound_bus.play_panel_in()

    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top arc
        top = QHBoxLayout()
        top.setSpacing(32)
        top.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_explore = HoloGlyphButton("EXPLORE MY IMAGES", self.sound_bus)
        self.btn_reflect = HoloGlyphButton("BEGIN A REFLECTION JOURNEY", self.sound_bus)
        self.btn_story = HoloGlyphButton("CREATE A STORY SEQUENCE", self.sound_bus)
        self.btn_journal = HoloGlyphButton("OPEN MY TRAVELER'S JOURNAL", self.sound_bus)
        self.btn_open = HoloGlyphButton("START UNDEFINED (OPEN MODE)", self.sound_bus)

        for b in [self.btn_explore, self.btn_reflect, self.btn_story, self.btn_journal, self.btn_open]:
            top.addWidget(b)

        # Bottom arc
        bottom = QHBoxLayout()
        bottom.setSpacing(32)
        bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_continue = HoloGlyphButton("CONTINUE WHERE I LEFT OFF", self.sound_bus)
        self.btn_inspire = HoloGlyphButton("INSPIRATION MODE", self.sound_bus)
        self.btn_quiet = HoloGlyphButton("QUIET MODE", self.sound_bus)
        self.btn_grows = HoloGlyphButton("THIS TOOL GROWS WITH YOU", self.sound_bus)
        self.btn_custom = HoloGlyphButton("YOUR SUGGESTIONS HERE >>>", self.sound_bus)

        for b in [self.btn_continue, self.btn_inspire, self.btn_quiet, self.btn_grows, self.btn_custom]:
            bottom.addWidget(b)

        layout.addLayout(top)
        layout.addLayout(bottom)

    def _setup_opacity(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        self.entry_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.entry_anim.setDuration(1200)
        self.entry_anim.setStartValue(0.0)
        self.entry_anim.setEndValue(1.0)
        self.entry_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def start_entry_animation(self):
        self.entry_anim.start()

    def _setup_scanline(self):
        from PyQt6.QtCore import QTimer
        self.scanline_pos = 0
        self.scanline_timer = QTimer(self)
        self.scanline_timer.timeout.connect(self._advance_scanline)
        self.scanline_timer.start(40)

    def _advance_scanline(self):
        self.scanline_pos = (self.scanline_pos + 3) % self.height()
        self.update()

    def _setup_drift_animation(self):
        self.drift_anim = QPropertyAnimation(self, b"driftOffset", self)
        self.drift_anim.setDuration(8000)
        self.drift_anim.setStartValue(QPoint(-4, -2))
        self.drift_anim.setEndValue(QPoint(4, 2))
        self.drift_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.drift_anim.setLoopCount(-1)
        self.drift_anim.start()

    def getDriftOffset(self):
        return self._drift_offset

    def setDriftOffset(self, value):
        self._drift_offset = value
        self.update()

    driftOffset = pyqtProperty(QPoint, fget=getDriftOffset, fset=setDriftOffset)

    def mouseMoveEvent(self, event):
        cx = self.width() / 2
        cy = self.height() / 2
        dx = (event.position().x() - cx) / cx
        dy = (event.position().y() - cy) / cy
        self._tilt_x = dx * 3
        self._tilt_y = dy * 3
        self.update()

    def start_exit_animation(self, on_finished=None):
        if self.sound_bus:
            self.sound_bus.play_panel_out()

        self.exit_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.exit_anim.setDuration(700)
        self.exit_anim.setStartValue(1.0)
        self.exit_anim.setEndValue(0.0)
        self.exit_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        if on_finished:
            self.exit_anim.finished.connect(on_finished)

        self.exit_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self._drift_offset)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._tilt_x)
        painter.rotate(-self._tilt_y)
        painter.translate(-self.width() / 2, -self.height() / 2)

        rect = self.rect().adjusted(10, 10, -10, -10)
        bg_color = QColor(10, 20, 40, 180)
        border_color = QColor(120, 190, 255, 200)

        painter.setBrush(bg_color)
        painter.setPen(border_color)
        painter.drawRoundedRect(rect, 18, 18)

        scan_color = QColor(180, 220, 255, 40)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(scan_color)
        scan_rect = rect.adjusted(0, self.scanline_pos, 0, 0)
        scan_rect.setHeight(8)
        painter.drawRect(scan_rect)

        super().paintEvent(event)
