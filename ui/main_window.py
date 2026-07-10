# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Main Window — TempleConsole Integration
#  File: main_window.py
#
#  Author: Mark J. Latsha
#  Co‑Author: Microsoft Copilot
#
#  Description:
#      Integrates TempleChildWidgetAlpha and TempleChildWidgetBeta
#      into the SIG Main Window as fully anchored child widgets.
#      This is the correct architecture — no top-level windows,
#      no drifting, no snapping, no floating. True Temple modules.
#
#  Launch Command:
#      python main_window.py
#
# ================================================================

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt

# --- Import your child widgets ---
from temple_child_widget_alpha import TempleChildWidgetAlpha
from temple_child_widget_beta import TempleChildWidgetBeta


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Main Window Setup ---
        self.setWindowTitle("Starfield Intelligent Gallery — TempleConsole")
        self.setMinimumSize(1200, 800)

        # --- Central Widget ---
        central = QWidget()
        self.setCentralWidget(central)

        # --- Layout for the TempleConsole ---
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Instantiate Child Widgets ---
        self.alpha_panel = TempleChildWidgetAlpha()
        self.beta_panel = TempleChildWidgetBeta()

        # --- Add to Layout ---
        layout.addWidget(self.alpha_panel)
        layout.addWidget(self.beta_panel)

        # --- Apply Layout ---
        central.setLayout(layout)
