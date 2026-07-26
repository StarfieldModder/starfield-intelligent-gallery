r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   C O M P A N I O N _ M O D E . P Y             ║
║        ██╔════╝ ██║ ██╔════╝   SIG Companion Interaction Hub                 ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "Where characters step forward and speak."    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  companion_mode.py                                             ║
║  Location   :  C:\\SIG\\companion_mode.py                                    ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.23 — Companion Mode Edition                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The SIG Companion Hub:                                                      ║
║    • Receives control from Cosmic Choice Panel                               ║
║    • Displays companion entries (future: dialogue, profiles, holograms)      ║
║    • Integrates Nebula Module for cosmic ambience                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# UI Panels
from companion.ui.companion_dashboard import CompanionDashboard
from companion.ui.creative_panel import CreativePanel
from companion.ui.curation_panel import CurationPanel
from companion.ui.story_panel import StoryPanel
from companion.ui.myth_panel import MythPanel

# Ingestion system
from companion.utils.ingest import ingest_screenshots


class CompanionMode(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SIG — Companion Mode")
        self.setStyleSheet("background-color: #0d111c; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("COMPANION MODE — INTERFACE ONLINE")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Future: companion profiles, dialogue, holographic presence.")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Dashboard Hub
        dashboard = CompanionDashboard()
        layout.addWidget(dashboard)

        # Button wiring
        dashboard.btn_creative.clicked.connect(self.open_creative_panel)
        dashboard.btn_curation.clicked.connect(self.open_curation_panel)
        dashboard.btn_story.clicked.connect(self.open_story_panel)
        dashboard.btn_myth.clicked.connect(self.open_myth_panel)

    # ---------------------------------------------------------
    # CREATIVE PANEL
    # ---------------------------------------------------------
    def open_creative_panel(self):
        from companion.pipelines.creative_pipeline import run_creative_pipeline

        images = ingest_screenshots("C:/SIG/sample_images")
        result = run_creative_pipeline(images)

        panel = CreativePanel(result)
        panel.show()

    # ---------------------------------------------------------
    # CURATION PANEL
    # ---------------------------------------------------------
    def open_curation_panel(self):
        from companion.pipelines.curation_pipeline import run_curation_pipeline

        images = ingest_screenshots("C:/SIG/sample_images")
        result = run_curation_pipeline(images)

        panel = CurationPanel(result)
        panel.show()

    # ---------------------------------------------------------
    # STORY PANEL
    # ---------------------------------------------------------
    def open_story_panel(self):
        from companion.models.sig_sequence import SIGSequence
        from companion.pipelines.story_pipeline import run_story_pipeline

        images = ingest_screenshots("C:/SIG/sample_images")

        sequence = SIGSequence(
            images=images[:10],
            theme="Gameplay Sequence",
            intensity="dynamic"
        )

        result = run_story_pipeline([sequence])

        panel = StoryPanel(result)
        panel.show()

    # ---------------------------------------------------------
    # MYTH PANEL
    # ---------------------------------------------------------
    def open_myth_panel(self):
        from companion.pipelines.myth_pipeline import run_myth_pipeline

        artifacts = [
            "Temple Artifact Alpha",
            "Temple Artifact Beta",
            "Glyph of the Outer Ring"
        ]

        result = run_myth_pipeline(artifacts)

        panel = MythPanel(result)
        panel.show()

    # ---------------------------------------------------------
    # FULLSCREEN LAUNCH
    # ---------------------------------------------------------
    def run(self):
        self.showFullScreen()
