# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: main_window.py
# Module: Main Application Window — Cinematic Stage
# Version: 2026.06.26 — PySide6 Unified Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# ================================================================

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
)

# Adjust this import to match your actual package structure.
# If intro_panel_widget.py is in a "ui" package, this is correct:
from ui.intro_panel_widget import IntroPanelWidget


class MainWindow(QMainWindow):
    """
    Main cinematic stage for the Starfield Intelligent Gallery (SIG).
    Hosts the intro pipeline, background layers, and future gallery systems.
    """

    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        # ------------------------------------------------------------
        # Window basics
        # ------------------------------------------------------------
        self.setWindowTitle("Starfield Intelligent Gallery")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: black;")

        # Central widget (stage root)
        central = QWidget(self)
        self.setCentralWidget(central)

        # ------------------------------------------------------------
        # Intro Panel Widget (Cinematic Choice Panel)
        # ------------------------------------------------------------
        self.intro_panel = IntroPanelWidget(app, self)

        # Show the intro panel after the window is ready
        QTimer.singleShot(0, self._show_intro_panel)

    def _show_intro_panel(self) -> None:
        """
        Entry point for the cinematic intro panel.
        This will trigger the expansion + fade-in sequence defined
        in IntroPanelWidget.show_panel().
        """
        self.intro_panel.show_panel()


# ================================================================
# Standalone Launch Harness
# ================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())

