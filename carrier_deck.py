r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   C A R R I E R _ D E C K . P Y                 ║
║        ██╔════╝ ██║ ██╔════╝   Interactive SIG Navigation Hub                ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "Where the panels wake up and speak."         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  carrier_deck.py                                               ║
║  Location   :  C:\\SIG\\carrier_deck.py                                      ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.23 — Interactive Deck Edition                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The interactive post-intro navigation surface:                              ║
║    • Receives control after “The Crossing”                                   ║
║    • Displays clickable SIG panels                                           ║
║    • Leads into the Cosmic Choice Panel                                      ║
║    • Integrates Nebula Module for cosmic ambience                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class CarrierDeck(QWidget):
    """
    The SIG Carrier Deck — the interactive navigation surface
    that appears after The Crossing and before the Cosmic Choice Panel.
    """

    def __init__(self, debug: bool = False, on_choice=None):
        super().__init__()
        self.debug = debug
        self._on_choice = on_choice

        self.setWindowTitle("SIG — Carrier Deck")
        self.setStyleSheet("background-color: #050810; color: white;")

        # Editor-friendly layout creation
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        # Title
        title = QLabel("CARRIER DECK — PANELS ONLINE")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Interactive choice button
        btn = QPushButton("ENTER COSMIC CHOICE PANEL")
        btn.setStyleSheet("background-color: #1a1f2b; color: white; padding: 20px;")
        btn.clicked.connect(self._on_choice)
        layout.addWidget(btn)

    def run(self):
        """Show the Carrier Deck in full-screen mode."""
        self.showFullScreen()


# ------------------------------------------------------------
# SAFE STANDALONE RUNNER
# ------------------------------------------------------------
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    def _dummy_choice():
        print("Cosmic Choice Panel would launch here.")

    deck = CarrierDeck(on_choice=_dummy_choice)
    deck.run()

    sys.exit(app.exec())