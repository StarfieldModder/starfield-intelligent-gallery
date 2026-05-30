# ============================================================
# File        : main_window.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Created     : May 2026
# Description : Main SIG application window.
#               Hosts panels such as Deep Archive and future
#               NG+ layer interfaces.
# ============================================================

from PyQt6.QtWidgets import QMainWindow
from GalleryApp.panels.deep_archive_panel import DeepArchivePanel

class MainSIGWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Starfield Intelligent Gallery")
        self.resize(1280, 720)
        self.deep_archive = None

    def open_deep_archive(self):
        if self.deep_archive is None:
            self.deep_archive = DeepArchivePanel(self)
        self.deep_archive.show()
