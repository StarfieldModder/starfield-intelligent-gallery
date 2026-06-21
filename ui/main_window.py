# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Main Window — Minimal Stable Edition (No Cinematics)
#
#  File: ui/main_window.py
#
#  Role:
#       Provides the main application window for SIG.
#       Loads the minimal ArtifactPanel with no cinematic features.
#       Safe, stable, and import‑clean for development.
#
#  Launch Command:
#       python C:\SIG\sig_main.py
#
#  Notes:
#       - No cinematic calls are made.
#       - No alignment / flare / transport / ascension.
#       - Only loads the ArtifactPanel and displays it.
# ================================================================

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt

from ui.artifact_panel import ArtifactPanel


class MainWindow(QMainWindow):
    """
    Minimal SIG Main Window.
    Loads the Artifact Panel with no cinematic behavior.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Starfield Intelligent Gallery — Minimal Edition")
        self.setMinimumSize(1280, 720)

        # Central widget container
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Simple label
        label = QLabel("Starfield Intelligent Gallery — Minimal Mode")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Button to show the Artifact Panel
        btn = QPushButton("Open Artifact Panel")
        btn.clicked.connect(self.show_artifact_panel)
        layout.addWidget(btn)

        # Placeholder for the panel instance
        self.artifact_panel = None

    # ------------------------------------------------------------
    # Show Artifact Panel (no cinematic calls)
    # ------------------------------------------------------------
    def show_artifact_panel(self):
        # Create the minimal Artifact Panel
        self.artifact_panel = ArtifactPanel()

        # Replace the central widget with the panel
        self.setCentralWidget(self.artifact_panel)
