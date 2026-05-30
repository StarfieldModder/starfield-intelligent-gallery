# ============================================================
# File        : intro_panel_window.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Description : Cinematic relic intro window.
#               Orchestrates starfield, relic awakening,
#               NG+ gating, and panel transitions.
# ============================================================

from pathlib import Path

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QEasingCurve,
)

from GalleryApp.core.relic_state import RelicState
from GalleryApp.sig_intro.relic_intro_panel import RelicIntroPanel
from GalleryApp.sig_intro.relic_button import RelicButton
from GalleryApp.sig_intro.starfield_background import StarfieldBackground


# NG+ unlock rules
UNLOCK_RULES = {
    0: ["ENTER GALLERY"],
    1: ["ENTER GALLERY", "NG+ RELIC"],
    2: ["ENTER GALLERY", "NG+ RELIC", "DEEP ARCHIVE"],
    3: ["ENTER GALLERY", "NG+ RELIC", "DEEP ARCHIVE", "RELIC SETTINGS"],
}


class IntroPanelWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Make the window background fully transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        # Avoid half-painted frames while we assemble the scene
        self.setUpdatesEnabled(False)

        self.setWindowTitle("SIG – Relic Intro")
        self.setGeometry(100, 100, 1280, 720)

        # ----------------------------------------------------
        # Load relic state (NG+ progression)
        # ----------------------------------------------------
        self.state_path = Path.home() / ".sig_relic_state.json"
        self.relic_state = RelicState.load(self.state_path)

        # ----------------------------------------------------
        # Relic panel overlay (floating arcs, glyphs, glow)
        # (Create first so it always covers the window)
        # ----------------------------------------------------
        self.relic_panel = RelicIntroPanel(self)
        self.relic_panel.setGeometry(self.rect())

        # ----------------------------------------------------
        # Starfield background (cinematic drift)
        # (Central widget, sits behind the relic panel)
        # ----------------------------------------------------
        self.starfield = StarfieldBackground(self)
        self.setCentralWidget(self.starfield)

        # Ensure relic panel is on top
        self.relic_panel.raise_()

        # ----------------------------------------------------
        # Buttons + animations
        # ----------------------------------------------------
        self._create_buttons()
        self._build_awakening_sequence()
        self._build_button_animations()
        self._apply_unlock_rules()

        # ----------------------------------------------------
        # Begin the cinematic awakening
        # ----------------------------------------------------
        self.setUpdatesEnabled(True)
        self.awakening.start()

    # --------------------------------------------------------
    # Resize handling
    # --------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep relic panel covering the full window
        self.relic_panel.setGeometry(self.rect())
        self.relic_panel.raise_()

    # --------------------------------------------------------
    # Create buttons
    # --------------------------------------------------------
    def _create_buttons(self):
        btn_w, btn_h = 260, 48
        center_x = self.width() // 2 - btn_w // 2
        base_y = self.height() // 2 + 96

        self.button1 = RelicButton("ENTER GALLERY", self.relic_panel)
        self.button2 = RelicButton("NG+ RELIC", self.relic_panel)
        self.button3 = RelicButton("DEEP ARCHIVE", self.relic_panel)
        self.button4 = RelicButton("RELIC SETTINGS", self.relic_panel)

        self.button1.setGeometry(center_x, base_y, btn_w, btn_h)
        self.button2.setGeometry(center_x, base_y + 64, btn_w, btn_h)
        self.button3.setGeometry(center_x, base_y + 128, btn_w, btn_h)
        self.button4.setGeometry(center_x, base_y + 192, btn_w, btn_h)

        # Button actions
        self.button1.mousePressEvent = self._open_main_sig
        self.button3.mousePressEvent = self._open_deep_archive

    # --------------------------------------------------------
    # Unlock rules (NG+ gating)
    # --------------------------------------------------------
    def _apply_unlock_rules(self):
        allowed = UNLOCK_RULES.get(self.relic_state.ng_plus_level, [])

        if "ENTER GALLERY" not in allowed:
            self.button1.hide()
        if "NG+ RELIC" not in allowed:
            self.button2.hide()
        if "DEEP ARCHIVE" not in allowed:
            self.button3.hide()
        if "RELIC SETTINGS" not in allowed:
            self.button4.hide()

    # --------------------------------------------------------
    # Awakening sequence (floating arcs + glow)
    # --------------------------------------------------------
    def _build_awakening_sequence(self):
        # Arc coalescence (slow, ancient)
        frame_anim = QPropertyAnimation(self.relic_panel, b"frameProgress")
        frame_anim.setDuration(4500)
        frame_anim.setStartValue(0.0)
        frame_anim.setEndValue(1.0)
        frame_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Glow awakening (warm amber)
        glow_anim = QPropertyAnimation(self.relic_panel, b"glowIntensity")
        glow_anim.setDuration(3600)
        glow_anim.setStartValue(0.0)
        glow_anim.setEndValue(1.0)
        glow_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Sequence
        self.awakening = QSequentialAnimationGroup(self)
        self.awakening.addAnimation(frame_anim)
        self.awakening.addAnimation(glow_anim)
        self.awakening.finished.connect(self._on_awakening_finished)

    def _on_awakening_finished(self):
        # Begin breathing + drift
        self.relic_panel.startHumPulse()
        self.relic_panel.startDrift()

        # Begin first button materialization
        self.btn1_seq.start()

    # --------------------------------------------------------
    # Button animations (coalescence + particle reveal)
    # --------------------------------------------------------
    def _build_button_animations(self):
        self.btn1_seq = self._make_button_seq(self.button1, 1600, 2200)
        self.btn2_seq = self._make_button_seq(self.button2, 1400, 2000)
        self.btn3_seq = self._make_button_seq(self.button3, 1300, 1900)
        self.btn4_seq = self._make_button_seq(self.button4, 1200, 1800)

        self.btn1_seq.finished.connect(self._start_btn2_if_visible)
        self.btn2_seq.finished.connect(self._start_btn3_if_visible)
        self.btn3_seq.finished.connect(self._start_btn4_if_visible)

    def _make_button_seq(self, button, dur_coalesce, dur_text):
        coalesce = QPropertyAnimation(button, b"coalesceProgress")
        coalesce.setDuration(dur_coalesce)
        coalesce.setStartValue(0.0)
        coalesce.setEndValue(1.0)
        coalesce.setEasingCurve(QEasingCurve.Type.InOutCubic)

        text = QPropertyAnimation(button, b"particleProgress")
        text.setDuration(dur_text)
        text.setStartValue(0.0)
        text.setEndValue(1.0)
        text.setEasingCurve(QEasingCurve.Type.InOutCubic)

        seq = QSequentialAnimationGroup(self)
        seq.addAnimation(coalesce)
        seq.addAnimation(text)
        return seq

    def _start_btn2_if_visible(self):
        if self.button2.isVisible():
            self.btn2_seq.start()

    def _start_btn3_if_visible(self):
        if self.button3.isVisible():
            self.btn3_seq.start()

    def _start_btn4_if_visible(self):
        if self.button4.isVisible():
            self.btn4_seq.start()

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------
    def _open_main_sig(self, event):
        # Optional: starfield jump effect
        try:
            self.starfield.start_jump_cruise()
        except Exception:
            pass

        from GalleryApp.main_window import MainSIGWindow
        self.sig_window = MainSIGWindow()
        self.sig_window.show()

    def _open_deep_archive(self, event=None):
        from GalleryApp.deep_archive.deep_archive_window import DeepArchiveWindow
        self.deep_archive = DeepArchiveWindow()
        self.deep_archive.show()
