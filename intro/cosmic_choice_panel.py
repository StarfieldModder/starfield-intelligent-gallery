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
║  Version    :  2026.07.03 — Choice Panel Edition                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                            ║
║                                                                              ║
║  The interactive decision surface:                                            ║
║    • Receives control from Carrier Deck                                      ║
║    • Presents the core SIG choices                                           ║
║    • Drives the narrative / mode selection                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class CosmicChoicePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIG — Cosmic Choice Panel")
        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("COSMIC CHOICE PANEL")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        prompt = QLabel("Choose your path among the stars...")
        prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(prompt)

    def run(self):
        self.showFullScreen()
