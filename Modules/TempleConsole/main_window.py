# ================================================================
#  Intelligent Gallery
#  Main Window — TempleConsole Integration
#  File: main_window.py
#
#  Author: Mark J. Latsha
#  Co‑Author: Microsoft Copilot
# ================================================================

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

# Correct imports based on your folder structure
from Modules.TempleConsole.temple_child_widget_alpha import TempleChildWidgetAlpha
from Modules.TempleConsole.temple_child_widget_beta import TempleChildWidgetBeta


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Starfield Intelligent Gallery — TempleConsole")
        self.setMinimumSize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.alpha_panel = TempleChildWidgetAlpha()
        self.beta_panel = TempleChildWidgetBeta()

        layout.addWidget(self.alpha_panel)
        layout.addWidget(self.beta_panel)

        central.setLayout(layout)
