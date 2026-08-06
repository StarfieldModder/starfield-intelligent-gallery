# ============================================================
#  SEVERITY ENGINE — Hybrid Severity (Rules + AI Intuition)
#  Location: C:\IG\sentinel\severity_engine.py
# ============================================================

def rule_based_severity(reason: str) -> str:
    """
    Baseline severity using explicit rules.
    """

    reason_lower = reason.lower()

    if any(word in reason_lower for word in ("corrupt", "missing core", "fatal", "crash")):
        return "critical"

    if any(word in reason_lower for word in ("instability", "unstable", "desync")):
        return "medium"

    if any(word in reason_lower for word in ("missing", "not found", "optional")):
        return "minor"

    # Default fallback
    return "minor"


def ai_intuition(reason: str) -> str:
    """
    AI intuition layer — detects deeper danger patterns.
    Cinematic override triggers happen here.
    """

    reason_lower = reason.lower()

    # Emotional danger patterns
    if any(word in reason_lower for word in ("collapse", "fracture", "echo", "disturbance")):
        return "critical"

    # Memory Chamber / Timeline anomalies
    if any(word in reason_lower for word in ("timeline", "memory", "chamber", "rift")):
        return "medium"

    # Guardian distress signals
    if "guardian" in reason_lower and "error" in reason_lower:
        return "critical"

    return None  # No override


def classify_severity(module_name: str, reason: str):
    """
    Hybrid severity:
    - Rule-based baseline
    - AI intuition override
    """

    baseline = rule_based_severity(reason)
    intuition = ai_intuition(reason)

    if intuition is None:
        # No override — return baseline
        return baseline, False

    # Override detected — cinematic escalation
    return intuition, True
