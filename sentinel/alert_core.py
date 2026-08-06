# ============================================================
#  ALERT CORE — Brainstem of the Sentinel
#  Location: C:\IG\sentinel\alert_core.py
#  Role: Freeze program, choose visual mode, open Alert Panel
# ============================================================

from typing import List

# In your actual project, replace these with real imports:
# from panels.alert_panel import show_soft_alert, show_hard_alert

# Placeholder UI hooks (to be wired to your PySide6 / IG UI system)
def show_soft_alert(**kwargs):
    # TODO: Connect to Starfield-style overlay panel
    print("[SOFT ALERT]", kwargs.get("emotional_line"), kwargs.get("analytical_line"))


def show_hard_alert(**kwargs):
    # TODO: Connect to full-screen Temple Alert takeover
    print("[HARD ALERT]", kwargs.get("emotional_line"), kwargs.get("analytical_line"))


# ------------------------------------------------------------
#  VISUAL MODE DECISION
# ------------------------------------------------------------
def is_critical(severity: str) -> bool:
    return severity.lower() in ("critical", "severe", "fatal")


# ------------------------------------------------------------
#  MAIN ALERT HANDLER
# ------------------------------------------------------------
def handle_alert(
    module_name: str,
    reason: str,
    severity: str,
    emotional_line: str,
    analytical_line: str,
    suggestions: List[str],
    pulse_word: str,
    override: bool,
):
    """
    Central alert handler.
    Decides visual mode, freezes flow, and opens the Temple Alert panel.
    """

    # 1 — Decide visual mode (Hybrid Visual: soft vs hard)
    critical = is_critical(severity)

    payload = {
        "module_name": module_name,
        "reason": reason,
        "severity": severity,
        "emotional_line": emotional_line,
        "analytical_line": analytical_line,
        "suggestions": suggestions,
        "pulse_word": pulse_word,
        "override": override,
    }

    # 2 — Route to appropriate visual mode
    if critical:
        # Full-screen Temple takeover
        show_hard_alert(**payload)
    else:
        # Soft overlay, program paused but visible
        show_soft_alert(**payload)

    # 3 — Here you can add hooks for:
    #    - pausing/resuming main event loop
    #    - safe shutdown
    #    - “Resume Program” / “Shutdown Safely” callbacks
