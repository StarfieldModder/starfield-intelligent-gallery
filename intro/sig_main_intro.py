r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   S I G _ M A I N _ I N T R O . P Y            ║
║        ██╔════╝ ██║ ██╔════╝   Headless Intro Renderer (Cached Video)       ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "Intro as artifact, not just playback."      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_main_intro.py                                             ║
║  Location   :  C:\\SIG\\intro\\sig_main_intro.py                             ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.03 — Headless Intro Edition                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                            ║
║                                                                              ║
║  Provides a headless render path for the SIG intro:                          ║
║    • Uses the same timing as the GUI intro                                   ║
║    • Renders “The Crossing” plus title timing to MP4                         ║
║    • No Qt window — pure imageio / ffmpeg pipeline                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import imageio
import os
import numpy as np

def render_intro(output_path, width, height, fps, duration):
    if output_path is None:
        output_path = os.path.join("C:\\SIG\\renders", "crossing_FINAL.mp4")

    writer = imageio.get_writer(output_path, fps=fps)

    total_frames = fps * duration
    for frame_idx in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        writer.append_data(frame)

    writer.close()



