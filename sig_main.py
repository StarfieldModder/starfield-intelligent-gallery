"""
Starfield Intelligent Gallery (SIG)
Application Launcher

Role:
    - Creates QApplication
    - Instantiates ui.main_window.MainWindow (cinematic edition)
    - Starts the event loop

Note:
    The previous MainWindow implementation has been archived in:
        ui/old_main_window.py
"""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
s