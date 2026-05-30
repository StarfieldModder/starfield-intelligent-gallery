# ============================================================
# File        : deep_archive_window.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Description : Placeholder window for the Deep Archive.
#               This will evolve into the full vault system.
# ============================================================

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class DeepArchiveWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Deep Archive – Prototype")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        title = QLabel("DEEP ARCHIVE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; color: white;")

        subtitle = QLabel("The vault is not yet constructed.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #CCCCCC;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
