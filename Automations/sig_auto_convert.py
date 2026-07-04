# ================================================================
# File        : sig_auto_convert.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (AI Engineering Assistant)
# Created     : Sunday, June 28, 2026 at 8:15 AM PDT
# Description : Converts Steam recordings (.m4s + .mpd) into MP4
#               using the GitHub Steam Exporter tool.
# ================================================================

import subprocess
from pathlib import Path
import os


def convert_recording_to_mp4(exporter_script: str, recording_folder: str, storage_root: str) -> Path:
    output_dir = Path(storage_root) / "Videos"
    output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run([
        "python",
        exporter_script,
        "--input", recording_folder,
        "--output", str(output_dir)
    ], check=False)

    mp4_files = sorted(output_dir.glob("*.mp4"), key=os.path.getmtime)
    return mp4_files[-1] if mp4_files else None
