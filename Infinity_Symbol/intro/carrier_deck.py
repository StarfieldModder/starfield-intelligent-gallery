r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   C A R R I E R _ D E C K . P Y                 ║
║        ██╔════╝ ██║ ██╔════╝   Post-Intro SIG Navigation Hub                 ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "Where the panels wake up and speak."         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  carrier_deck.py                                               ║
║  Location   :  C:\\SIG\\carrier_deck.py                                      ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.23 — Carrier Deck Edition                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The main post-intro navigation surface:                                     ║
║    • Receives control after “The Crossing”                                   ║
║    • Displays SIG panels                                                     ║
║    • Leads into the Cosmic Choice Panel                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class CarrierDeck(QWidget):
    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.setWindowTitle("SIG — Carrier Deck")
        self.setStyleSheet("background-color: #050810; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CARRIER DECK — PANELS ONLINE")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Cosmic Choice Panel is forming...")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

    def run(self):
        self.showFullScreen()
