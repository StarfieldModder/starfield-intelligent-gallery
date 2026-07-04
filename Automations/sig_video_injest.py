# ================================================================
# File        : sig_video_ingest.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (AI Engineering Assistant)
# Created     : Sunday, June 28, 2026 at 8:15 AM PDT
# Description : Steam recording auto-detection module.
#               Finds the REAL Steam installation path automatically.
#               Watches for new recordings (session.mpd).
# ================================================================

import os
import time
import json
from pathlib import Path
from typing import Callable

SETTINGS_PATH = Path(r"C:\SIG\Settings\steam_auto_ingest.json")


# ------------------------------------------------------------
# Load SIG settings
# ------------------------------------------------------------
def load_settings():
    if not SETTINGS_PATH.exists():
        return {
            "auto_ingest_enabled": True,
            "steam_userdata_root": None,  # auto-detect
            "sig_storage_root": r"C:\SIG\Storage",
            "exporter_script": r"C:\SteamExporter\steam_game_recording_exporter.py",
        }
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# Auto-detect Steam installation
# ------------------------------------------------------------
def detect_steam_root() -> str:
    candidates = [
        r"C:\Steam",
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"D:\Steam",
        r"E:\Steam",
    ]

    for path in candidates:
        userdata = Path(path) / "userdata"
        if userdata.exists():
            return str(userdata)

    # Fallback: search entire C: drive (slow but safe)
    for root, dirs, files in os.walk("C:\\"):
        if "userdata" in dirs:
            return os.path.join(root, "userdata")

    return None


# ------------------------------------------------------------
# Find Steam recording folders
# ------------------------------------------------------------
def find_recording_folders(steam_userdata_root: str):
    for root, dirs, files in os.walk(steam_userdata_root):
        if "session.mpd" in files:
            yield root


# ------------------------------------------------------------
# Watch for new recordings
# ------------------------------------------------------------
def watch_for_new_recordings(steam_userdata_root: str, callback: Callable[[str], None]):
    seen = set()
    while True:
        for folder in find_recording_folders(steam_userdata_root):
            if folder not in seen:
                seen.add(folder)
                callback(folder)
        time.sleep(5)
