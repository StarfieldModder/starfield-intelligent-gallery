# ============================================================
#  SENTINEL API — Summoning Gateway of the Temple
#  Location: C:\IG\sentinel\sentinel_api.py
#  Permanent Marker: Birth of the Sentinel — July 28, 2026
# ============================================================

import datetime
import os

from .alert_core import handle_alert
from .severity_engine import classify_severity
from .pulse_engine import trigger_pulse
from .guardian_bridge import guardian_explain, guardian_suggest

# ------------------------------------------------------------
#  LOGGING SETUP — sentinel.log
# ------------------------------------------------------------
LOG_PATH = os.path.join("C:\\IG\\logs", "sentinel.log")

def log_event(module, reason, severity, override=False, pulse_word=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = (
        f"[{timestamp}] MODULE={module} | REASON={reason} | "
        f"SEVERITY={severity} | OVERRIDE={override} | "
        f"PULSE_WORD={pulse_word}\n"
    )

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass  # Sentinel must never crash due to logging


# ------------------------------------------------------------
#  PUBLIC API — invoke_sentinel()
# ------------------------------------------------------------
def invoke_sentinel(module_name: str, reason: str):
    """
    Epic, commanding, cinematic summoning of the Sentinel.
    Called from ANY module in the Intelligent Gallery.
    """

    # 1 — Classify severity (Hybrid: rules + AI intuition)
    severity, override = classify_severity(module_name, reason)

    # 2 — Trigger pulse engine (Word‑Sync + Keyword Pulse)
    pulse_word = trigger_pulse(reason, severity)

    # 3 — Log the event
    log_event(module_name, reason, severity, override, pulse_word)

    # 4 — Guardian emotional + analytical explanation
    emotional, analytical = guardian_explain(module_name, reason, severity)

    # 5 — Guardian suggestions
    suggestions = guardian_suggest(module_name, reason, severity)

    # 6 — Handle alert (soft overlay or full-screen takeover)
    handle_alert(
        module_name=module_name,
        reason=reason,
        severity=severity,
        emotional_line=emotional,
        analytical_line=analytical,
        suggestions=suggestions,
        pulse_word=pulse_word,
        override=override
    )
