# ============================================================
#  TIMELINE INSTABILITY DETECTOR — Sentinel Integration
# ============================================================

from sentinel.sentinel_api import invoke_sentinel

def scan_timeline(events):
    """
    Detects fractures, loops, desync, or temporal anomalies.
    """

    for event in events:
        text = event.lower()

        if "fracture" in text:
            invoke_sentinel("TimelineEngine", "timeline fracture")

        if "loop" in text:
            invoke_sentinel("TimelineEngine", "temporal loop detected")

        if "desync" in text:
            invoke_sentinel("TimelineEngine", "timeline desync")

        if "rift" in text:
            invoke_sentinel("TimelineEngine", "timeline rift detected")
