# ============================================================
#  PULSE ENGINE — Heartbeat of the Temple
#  Location: C:\IG\sentinel\pulse_engine.py
#  Role: Word‑Sync + Keyword Pulse + Severity Pulse Mapping
# ============================================================

# ------------------------------------------------------------
#  EMOTIONAL WORD‑SYNC TRIGGERS
# ------------------------------------------------------------
EMOTIONAL_PULSE_MAP = {
    "mark": "soft",
    "wrong": "medium",
    "protect": "bright",
}

# ------------------------------------------------------------
#  ANALYTICAL KEYWORD PULSE TRIGGERS
# ------------------------------------------------------------
ANALYTICAL_PULSE_MAP = {
    "instability": "medium",
    "failed": "strong",
    "restore": "bright",
}

# ------------------------------------------------------------
#  SEVERITY-BASED PULSE INTENSITY
# ------------------------------------------------------------
SEVERITY_PULSE_MAP = {
    "minor": "soft",
    "medium": "medium",
    "critical": "bright",
}

# ------------------------------------------------------------
#  CINEMATIC OVERRIDE AMPLIFICATION
# ------------------------------------------------------------
def amplify_for_override(pulse: str) -> str:
    """
    When the Guardian performs a Cinematic Override,
    the Temple heartbeat intensifies.
    """
    if pulse == "soft":
        return "medium"
    if pulse == "medium":
        return "bright"
    return "bright"  # already max


# ------------------------------------------------------------
#  MAIN PULSE TRIGGER
# ------------------------------------------------------------
def trigger_pulse(reason: str, severity: str, override: bool = False) -> str:
    """
    Determines the pulse intensity based on:
    - emotional words
    - analytical keywords
    - severity level
    - cinematic override amplification

    Returns the pulse word used (for logging).
    """

    reason_lower = reason.lower()

    # 1 — Emotional Word‑Sync
    for word, pulse in EMOTIONAL_PULSE_MAP.items():
        if word in reason_lower:
            return amplify_for_override(pulse) if override else pulse

    # 2 — Analytical Keyword Pulse
    for word, pulse in ANALYTICAL_PULSE_MAP.items():
        if word in reason_lower:
            return amplify_for_override(pulse) if override else pulse

    # 3 — Severity-based fallback
    base_pulse = SEVERITY_PULSE_MAP.get(severity.lower(), "soft")

    return amplify_for_override(base_pulse) if override else base_pulse
