# ============================================================
# File        : intro_panel.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (Engineering Assistant)
# Created     : June 2026
# Description : Intro Panel for the SIG.
#               First cinematic screen shown on launch.
#               Includes fade-in and glow animations.
# ============================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

from ui.animation_engine import create_fade_in, create_glow_pulse


class IntroPanel(QWidget):
    def __init__(self):
        super().__init__()

        # --------------------------------------------------------
        # Panel Configuration
        # --------------------------------------------------------
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.0)  # start fully transparent

        self.setMinimumSize(800, 600)


        # --------------------------------------------------------
        # Layout
        # --------------------------------------------------------
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        # --------------------------------------------------------
        # Title Label
        # --------------------------------------------------------
        self.title = QLabel("STARFIELD INTELLIGENT GALLERY")
        self.title.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 4px;
        """)

        layout.addWidget(self.title)
        self.setLayout(layout)

        # --------------------------------------------------------
        # Animations
        # --------------------------------------------------------
        # Fade in the entire panel
        self.fade_in_animation = create_fade_in(self)
        self.fade_in_animation.start()

        # Glow pulse on the title
        self.glow_animation = create_glow_pulse(self.title)
        self.title.setGraphicsEffect(self.glow_animation.targetObject())
        self.glow_animation.start()


