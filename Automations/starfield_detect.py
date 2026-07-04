# ================================================================
# File        : starfield_detect.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (AI Engineering Assistant)
# Created     : Sunday, June 28, 2026 at 8:35 AM PDT
# Description : Auto-detects Starfield installation location.
#               Future use: mapping captures, saves, stories.
# ================================================================

import os
from pathlib import Path


def detect_starfield_root() -> str | None:
    candidates = [
        r"C:\XboxGames\Starfield",
        r"C:\Program Files (x86)\Steam\steamapps\common\Starfield",
        r"C:\Program Files\Steam\steamapps\common\Starfield",
        r"C:\Steam\steamapps\common\Starfield",
        r"D:\Steam\steamapps\common\Starfield",
        r"E:\Steam\steamapps\common\Starfield",
    ]

    for path in candidates:
        if Path(path).exists():
            return path

    # Fallback: search for a folder named "Starfield"
    for root, dirs, files in os.walk("C:\\"):
        if "Starfield" in dirs:
            return os.path.join(root, "Starfield")

    return None
