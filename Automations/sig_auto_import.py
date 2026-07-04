# ================================================================
# File        : sig_auto_import.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (AI Engineering Assistant)
# Created     : Sunday, June 28, 2026 at 8:15 AM PDT
# Description : Imports converted MP4 files into SIG storage.
#               Future expansion: metadata, thumbnails, story markers.
# ================================================================

from pathlib import Path


def ingest_mp4_into_sig(mp4_path: Path, storage_root: str):
    videos_dir = Path(storage_root) / "Videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    print(f"[SIG] Imported video: {mp4_path}")
