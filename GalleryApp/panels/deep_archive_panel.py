# ============================================================
# File        : deep_archive_panel.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Created     : May 2026
# Description : Placeholder Deep Archive panel.
#               Future home of universe history and NG+ layers.
# ============================================================

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class DeepArchivePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deep Archive")

        layout = QVBoxLayout(self)
        title = QLabel("DEEP ARCHIVE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; color: white;")

        subtitle = QLabel("This is where your universe history will live.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #CCCCCC;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.setStyleSheet("background-color: #050811;")
