r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      S I G _ L A U N C H E R . P Y             ║
║        ██╔════╝ ██║ ██╔════╝      GUI Front Door — Launch Orchestrator      ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "Open the hatch. Let the story begin."    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_launcher.py                                               ║
║  Location   :  C:\SIG\sig_launcher.py                                        ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.04 — Launch Orchestrator Edition                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The proper GUI front door for SIG. It:                                      ║
║    • Creates the QApplication                                                ║
║    • Shows the IntroPanelWidget (The Crossing + title sequence)              ║
║    • Hands off to CarrierDeck when the intro finishes                        ║
║    • Hands off to CosmicChoicePanel when the player is ready to choose       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
from PySide6.QtWidgets import QApplication

from carrier_deck import CarrierDeck
from cosmic_choice_panel import CosmicChoicePanel
from ui.intro_panel_widget import IntroPanelWidget


def launch_sig(debug: bool = False) -> None:
    """
    Launch the full SIG GUI experience:
      1. IntroPanelWidget (title + The Crossing)
      2. CarrierDeck
      3. CosmicChoicePanel
    """
    app = QApplication(sys.argv)

    def on_intro_finished():
        deck = CarrierDeck(debug=debug, on_choice=on_choice_made)
        deck.run()

    def on_choice_made():
        panel = CosmicChoicePanel()
        panel.run()

    intro = IntroPanelWidget()
    intro.intro_finished.connect(on_intro_finished)
    intro.showFullScreen()
    intro.show_panel()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch_sig()
