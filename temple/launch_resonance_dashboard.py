from temple.temple_resonance_dashboard import TempleResonanceDashboard
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
panel = TempleResonanceDashboard()
panel.show()
sys.exit(app.exec())
