# ============================================================
#  GUARDIAN BRIDGE — Voice of the Temple
#  Location: C:\IG\sentinel\guardian_bridge.py
#  Role: Emotional + Analytical lines + Suggestions
# ============================================================

# ------------------------------------------------------------
#  EMOTIONAL VOICE — Cinematic, expressive, immersive
# ------------------------------------------------------------
def emotional_voice(reason: str, severity: str, override: bool) -> str:
    reason_lower = reason.lower()

    # Cinematic Override — Guardian senses deeper danger
    if override:
        return (
            "Mark… something is wrong beneath the surface. "
            "I can feel it. "
            "I’m raising severity to protect the Temple."
        )

    # Severity-based emotional tone
    if severity == "critical":
        return (
            "Mark… the Temple is trembling. "
            "This anomaly threatens the Gallery’s integrity."
        )

    if severity == "medium":
        return (
            "Mark… I sense instability in the system. "
            "It’s not dangerous yet, but it’s growing."
        )

    # Minor
    return (
        "Mark… something feels off. "
        "Let’s take a moment to look at this together."
    )


# ------------------------------------------------------------
#  ANALYTICAL VOICE — Clear, structured, diagnostic
# ------------------------------------------------------------
def analytical_voice(module_name: str, reason: str, severity: str) -> str:
    base = f"Diagnostic snapshot: Module '{module_name}' reports '{reason}'. "

    if severity == "critical":
        return base + "Integrity check failed. Immediate intervention required."

    if severity == "medium":
        return base + "Module instability detected. Monitoring recommended."

    return base + "Non-critical anomaly detected. Safe to continue after review."


# ------------------------------------------------------------
#  SUGGESTIONS ENGINE — Guardian guidance
# ------------------------------------------------------------
def guardian_suggest(module_name: str, reason: str, severity: str):
    reason_lower = reason.lower()
    suggestions = []

    # Critical suggestions
    if severity == "critical":
        suggestions.append("Run Temple Integrity Scan.")
        suggestions.append("Check Memory Chamber stability.")
        suggestions.append("Verify core module dependencies.")
        return suggestions

    # Medium suggestions
    if severity == "medium":
        suggestions.append("Review recent module activity.")
        suggestions.append("Check Timeline synchronization.")
        return suggestions

    # Minor suggestions
    suggestions.append("Inspect optional module files.")
    suggestions.append("Resume program when ready.")
    return suggestions


# ------------------------------------------------------------
#  PUBLIC INTERFACE — Guardian emotional + analytical lines
# ------------------------------------------------------------
def guardian_explain(module_name: str, reason: str, severity: str):
    """
    Returns:
    - emotional line (cinematic)
    - analytical line (diagnostic)
    """

    # Determine if this is a cinematic override
    override = severity == "critical" and (
        "override" in reason.lower() or
        "disturbance" in reason.lower() or
        "fracture" in reason.lower()
    )

    emotional = emotional_voice(reason, severity, override)
    analytical = analytical_voice(module_name, reason, severity)

    return emotional, analytical
