from temple.temple_resonance_dashboard import TempleResonanceDashboard
from PySide6.QtWidgets import QApplication
import sys

module = sys.argv[1]
description = sys.argv[2]

app = QApplication(sys.argv)
panel = TempleResonanceDashboard()
panel.show()
panel.register_event(module, description)
sys.exit(app.exec())
