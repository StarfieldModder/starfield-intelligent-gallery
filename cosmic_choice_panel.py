r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   C O S M I C _ C H O I C E _ P A N E L . P Y  ║
║        ██╔════╝ ██║ ██╔════╝   Decision Surface — SIG Narrative Fork        ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "The moment the player chooses their path."  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  cosmic_choice_panel.py                                        ║
║  Location   :  C:\\SIG\\cosmic_choice_panel.py                               ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.03 — Choice Panel + Wiring Edition                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                            ║
║                                                                              ║
║  The interactive decision surface:                                            ║
║    • Receives control from Carrier Deck                                      ║
║    • Presents the core SIG choices                                           ║
║    • Drives the narrative / mode selection                                  ║
║    • Wires directly into Gallery, Relics, Companion, Archive modes          ║
║    • Adds hover animations, nebula background, and panel effects            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QFont

from gallery_mode import GalleryMode
from relics_mode import RelicsMode
from companions_mode import CompanionMode
from archive_mode import ArchiveMode
from nebula_module import render_nebula

class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1f2b;
                color: white;
                padding: 20px;
                border: 2px solid #3a4a6b;
            }
            QPushButton:hover {
                background-color: #243047;
                border: 2px solid #6fa3ff;
            }
        """)
        self._glyph_anim = QPropertyAnimation(self, b"windowOpacity")
        self._glyph_anim.setDuration(300)
        self._glyph_anim.setStartValue(0.8)
        self._glyph_anim.setEndValue(1.0)

    def enterEvent(self, event):
        self._glyph_anim.start()
        super().enterEvent(event)

class CosmicChoicePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIG — Cosmic Choice Panel")

        # Nebula background (simple color + future hook to nebula_module)
        nebula_state = render_nebula()
        self.setStyleSheet("background-color: #02040a; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("COSMIC CHOICE PANEL")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 28))
        layout.addWidget(title)

        prompt = QLabel("Choose your path among the stars...")
        prompt.setAlignment(Qt.AlignCenter)
        prompt.setFont(QFont("Segoe UI", 16))
        layout.addWidget(prompt)

        # Buttons → instances of modes
        btn_gallery = HoverButton("ENTER GALLERY MODE")
        btn_gallery.clicked.connect(self._enter_gallery)
        layout.addWidget(btn_gallery)

        btn_relics = HoverButton("ENTER RELICS MODE")
        btn_relics.clicked.connect(self._enter_relics)
        layout.addWidget(btn_relics)

        btn_companion = HoverButton("ENTER COMPANION MODE")
        btn_companion.clicked.connect(self._enter_companion)
        layout.addWidget(btn_companion)

        btn_archive = HoverButton("ENTER ARCHIVE MODE")
        btn_archive.clicked.connect(self._enter_archive)
        layout.addWidget(btn_archive)

    def _enter_gallery(self):
        mode = GalleryMode()
        mode.run()

    def _enter_relics(self):
        mode = RelicsMode()
        mode.run()

    def _enter_companion(self):
        mode = CompanionMode()
        mode.run()

    def _enter_archive(self):
        mode = ArchiveMode()
        mode.run()

    def run(self):
        self.showFullScreen()
