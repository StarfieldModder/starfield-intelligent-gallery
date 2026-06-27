# C:\SIG\Python\sig_gallery_panel.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class GalleryPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        label = QLabel("FULL GALLERY PANEL – WELCOME, TRAVELER")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(label)
