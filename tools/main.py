r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗     M A I N . P Y                               ║
║        ██╔════╝ ██║ ██╔════╝     Mission Control — SIG Entry Point           ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║    Starfield Intelligent Gallery               ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝     "Every great journey begins with            ║
║                                    a single line of code."                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os

# ⭐ FIX: Ensure Python can see sig_launcher.py
sys.path.append(r"C:\SIG")


def main():
    parser = argparse.ArgumentParser(
        description="Starfield Intelligent Gallery — Mission Control"
    )
    parser.add_argument("--skip-intro", action="store_true",
                        help="Skip the cinematic intro")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug logging")
    parser.add_argument("--render", action="store_true",
                        help="Headless render mode")
    parser.add_argument("--output", type=str,
                        help="Output file for render mode")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--duration", type=int, default=8)
    parser.add_argument("--no-video", action="store_true",
                        help="Disable video playback")

    args = parser.parse_args()

    # ------------------------------------------------------------
    # 1. Headless render mode
    # ------------------------------------------------------------
    if args.render:
        from intro.sig_main_intro import render_intro
        render_intro(args.output, args.width, args.height,
                     args.fps, args.duration)
        return

    # ------------------------------------------------------------
    # 2. Skip intro → go directly to Carrier Deck
    # ------------------------------------------------------------
    if args.skip_intro:
        from ui.carrier_deck import CarrierDeck
        deck = CarrierDeck(debug=args.debug)
        deck.run()
        return

    # ------------------------------------------------------------
    # 3. Full cinematic chain (default)
    # ------------------------------------------------------------
    from sig_launcher import launch_sig
    launch_sig(debug=args.debug)


if __name__ == "__main__":
    main()


