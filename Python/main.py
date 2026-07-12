# ============================================================
# File        : main.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Created     : May 2026
# Description : Application entry point.
#               Launches the SIG Cinematic Intro (Unified).
# ============================================================

import sys
from PyQt6.QtWidgets import QApplication
from SIG.sig_launcher import SIGLauncher

def main():
    app = QApplication(sys.argv)
    win = SIGLauncher(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


