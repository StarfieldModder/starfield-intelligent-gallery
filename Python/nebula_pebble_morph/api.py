# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: api.py
# Module: Nebula Pebble Morph — Public API
# Version: 2026.07.11 — SIG Temple Integration Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# Location: Brentwood, California — Pacific Daylight Time
#
# Description:
#     Public API entry point for the Nebula Pebble Morph subsystem.
#     Allows SIG Temple components to trigger the July 10 cinematic morph.
#
# Notes:
#     - Clean, stable, durable API for Temple-wide access.
#     - Follows Master Systems Architect rules:
#           * Minimal surface area
#           * Clear invocation path
#           * No internal leakage
# ================================================================

from .nebula_pebble_morph import NebulaPebbleMorph


def run_nebula_pebble_morph():
    """
    Public API entry point for the Nebula Pebble Morph subsystem.
    """
    morph = NebulaPebbleMorph()
    morph.run()
