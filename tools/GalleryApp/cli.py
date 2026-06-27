# ============================================================
# File        : cli.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot
# Created     : May 2026
# Description : Console entry point for SIG. Allows the user to
#               launch the entire application with a single word:
#               "sig".
# ============================================================

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import main as launch_main

def main():
    launch_main()

if __name__ == "__main__":
    main()
