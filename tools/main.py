# ============================================================
# File        : main.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (Engineering Assistant)
# Created     : June 2026
# Description : Application entry point.
#               Launches the SIG Main Window (PySide6 Edition).
# ============================================================

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


