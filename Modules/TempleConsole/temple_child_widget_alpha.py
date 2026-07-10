# ================================================================
#  Starfield Intelligent Gallery (SIG)
#  Temple Child Widget Alpha
#  File: temple_child_widget_alpha.py
#
#  Author: Mark J. Latsha
#  Co‑Author: Microsoft Copilot
#
#  Description:
#      The Alpha Child Widget — a fully anchored SIG module designed
#      to sit inside the TempleConsole layout without drifting,
#      snapping, or behaving like a top‑level window. This widget
#      represents the first embedded panel in the Temple architecture.
#
#  Launch Command:
#      python temple_child_widget_alpha.py
#
# ================================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class TempleChildWidgetAlpha(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Widget Styling ---
        self.setObjectName("TempleChildWidgetAlpha")
        self.setStyleSheet("""
            #TempleChildWidgetAlpha {
                background-color: rgba(40, 40, 55, 180);
                border: 2px solid rgba(200, 200, 255, 120);
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

        title = QLabel("Temple Child Widget Alpha")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        self.setLayout(layout)
