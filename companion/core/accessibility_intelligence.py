def simplify_summary(text: str):
    """
    Very simple placeholder:
    - Shortens long text
    - Keeps it readable
    """
    if len(text) > 120:
        return text[:117] + "..."
    return text

def accessibility_wrap(result: dict):
    """
    Wraps any pipeline result with a simplified view.
    """
    simplified = {}

    if "story_nodes" in result:
        simplified["story_titles"] = [n.title for n in result["story_nodes"]]

    if "wings" in result:
        simplified["wing_names"] = list(result["wings"].keys())

    simplified["status"] = result.get("status", "ok")
    return simplified
