from core.diagnostic_reporter import record_error


def generate_artifact_lore(artifact_name: str):
    """
    Generates lore text for a given artifact name.
    """
    try:
        return (
            f"{artifact_name} is a relic of forgotten journeys, "
            f"echoing choices made among the stars."
        )
    except Exception as exc:
        record_error(
            module="myth_intelligence",
            function="generate_artifact_lore",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="warning",
            exc=exc,
        )
        return "Lore unavailable due to an internal error."


def build_myth_for_artifacts(artifacts):
    """
    Builds mythic entries for a list of artifact names.
    """
    try:
        myth_entries = {}

        for name in artifacts:
            myth_entries[name] = {
                "lore": generate_artifact_lore(name),
                "symbolism": (
                    "Represents the player's evolving relationship with the unknown."
                ),
            }

        return myth_entries

    except Exception as exc:
        record_error(
            module="myth_intelligence",
            function="build_myth_for_artifacts",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="critical",
            exc=exc,
        )
        return 
