# ================================================================
# File        : SIGVideoIngestionEngine.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (AI Engineering Assistant)
# Created     : Sunday, June 28, 2026 at 8:45 AM PDT
# Description : Continuous background watcher for Steam recordings.
#               Auto-detects Steam + Starfield locations.
#               Converts recordings to MP4 and imports into SIG.
#               Designed to run as a tiny background companion.
# ================================================================

import threading

from sig_video_ingest import (
    load_settings,
    detect_steam_root,
    watch_for_new_recordings,
)
from sig_auto_convert import convert_recording_to_mp4
from sig_auto_import import ingest_mp4_into_sig
from starfield_detect import detect_starfield_root


class SIGVideoIngestionEngine:
    """
    SIGVideoIngestionEngine
    ------------------------
    - Loads SIG settings (including auto_ingest_enabled).
    - Auto-detects Steam userdata root if not specified.
    - Auto-detects Starfield installation root (for future use).
    - Starts a background thread that watches for new Steam recordings.
    - Converts new recordings to MP4 using the exporter script.
    - Imports MP4 files into SIG storage.
    """

    def __init__(self):
        self.settings = load_settings()
        self.enabled = bool(self.settings.get("auto_ingest_enabled", False))
        self.thread = None

        # Detect Steam userdata root
        self.steam_userdata_root = self.settings.get("steam_userdata_root")
        if not self.steam_userdata_root:
            self.steam_userdata_root = detect_steam_root()
            if self.steam_userdata_root:
                print(f"[SIG] Detected Steam userdata at: {self.steam_userdata_root}")
            else:
                print("[SIG] ERROR: Could not detect Steam userdata root.")

        # Detect Starfield installation root (for future story/capture mapping)
        self.starfield_root = self.settings.get("starfield_install_root")
        if not self.starfield_root:
            self.starfield_root = detect_starfield_root()
            if self.starfield_root:
                print(f"[SIG] Detected Starfield at: {self.starfield_root}")
            else:
                print("[SIG] WARNING: Could not detect Starfield installation.")

        self.storage_root = self.settings.get("sig_storage_root", r"C:\SIG\Storage")
        self.exporter_script = self.settings.get(
            "exporter_script",
            r"C:\SteamExporter\steam_game_recording_exporter.py",
        )

    # ------------------------------------------------------------
    # Start background watcher
    # ------------------------------------------------------------
    def start(self):
        if not self.enabled:
            print("[SIG] Steam auto-ingest is disabled in settings.")
            return

        if not self.steam_userdata_root:
            print("[SIG] Cannot start auto-ingest: Steam userdata root unknown.")
            return

        def handle_new_recording(folder: str):
            print(f"[SIG] New Steam recording detected: {folder}")
            mp4_path = convert_recording_to_mp4(
                self.exporter_script,
                folder,
                self.storage_root,
            )
            if mp4_path:
                ingest_mp4_into_sig(mp4_path, self.storage_root)
            else:
                print("[SIG] WARNING: No MP4 produced for recording folder.")

        def run():
            watch_for_new_recordings(self.steam_userdata_root, handle_new_recording)

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        print("[SIG] Steam auto-ingest engine started (background watcher).")
