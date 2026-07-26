r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   C O S M I C _ C H O I C E _ P A N E L . P Y   ║
║        ██╔════╝ ██║ ██╔════╝   Decision Surface — SIG Narrative Fork         ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "The moment the player chooses their path."   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  cosmic_choice_panel.py                                        ║
║  Location   :  C:\SIG\cosmic_choice_panel.py                                 ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.23 — Choice Panel Edition (Patched 15:44 PDT)         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The interactive decision surface:                                           ║
║    • Receives control from Carrier Deck                                      ║
║    • Presents the core SIG choices                                           ║
║    • Drives the narrative / mode selection                                   ║
║                                                                              ║
║  PATCH NOTES (2026.07.23 — 15:44 PDT)                                        ║
║    • Added Companion Mode launch button                                      ║
║    • Added import for CompanionDashboard                                     ║
║    • Added full-screen launch logic                                          ║
║    • Preserved original layout + cinematic style                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

# === Phase 6: Companion Mode import ===
from companion.ui.companion_dashboard import CompanionDashboard


class CosmicChoicePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIG — Cosmic Choice Panel")
        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("COSMIC CHOICE PANEL")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        # Prompt
        prompt = QLabel("Choose your path among the stars...")
        prompt.setAlignment(Qt.AlignCenter)
        prompt.setStyleSheet("font-size: 18px; margin-bottom: 20px;")
        layout.addWidget(prompt)

        # === Companion Mode Button ===
        self.btn_companion = QPushButton("Enter Companion Mode")
        self.btn_companion.setStyleSheet("""
            QPushButton {
                background-color: #1f2937;
                color: #e5e7eb;
                padding: 14px;
                border-radius: 8px;
                font-size: 18px;
                border: 2px solid #374151;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            QPushButton:pressed {
                background-color: #4b5563;
            }
        """)
        self.btn_companion.clicked.connect(self.launch_companion_mode)
        layout.addWidget(self.btn_companion)

    # === Phase 6: Launch Companion Mode ===
    def launch_companion_mode(self):
        """Launch the Companion Intelligence Dashboard."""
        dashboard = CompanionDashboard()
        dashboard.showFullScreen()

    def run(self):
        self.showFullScreen()

