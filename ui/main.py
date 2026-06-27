# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: main.py
# Module: Application Entry Point
# Version: 2026.06.26 — PySide6 Unified Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# ================================================================

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.cinematic_pipeline import CinematicPipeline
from main_window import MainWindow


def main():
    # Create the global application object
    app = QApplication(sys.argv)

    # Create the main window (cinematic stage)
    window = MainWindow(app)
    window.show()

    # Create and attach the cinematic pipeline
    pipeline = CinematicPipeline(app, window)
    pipeline.setGeometry(window.rect())
    pipeline.show()

    # Enter the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()





