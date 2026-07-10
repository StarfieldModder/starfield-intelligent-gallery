# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Temple Child Widget Beta
#  File: temple_child_widget_beta.py
#
#  Author: Mark J. Latsha
#  Co‑Author: Microsoft Copilot
#
#  Description:
#      The Beta Child Widget — the second fully anchored SIG module.
#      Designed to pair with Alpha inside the TempleConsole layout.
#      Behaves as a true child widget with no top‑level window drift.
#
#  Launch Command:
#      python temple_child_widget_beta.py
#
# ================================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class TempleChildWidgetBeta(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Widget Styling ---
        self.setObjectName("TempleChildWidgetBeta")
        self.setStyleSheet("""
            #TempleChildWidgetBeta {
                background-color: rgba(55, 40, 40, 180);
                border: 2px solid rgba(255, 200, 200, 120);
                border-radius: 12px;
            }
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Temple Child Widget Beta")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        self.setLayout(layout)
