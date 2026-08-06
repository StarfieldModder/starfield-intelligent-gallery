# ============================================================
#  SENTINEL SEVERITY TUNING TABLE
#  Location: C:\IG\sentinel\severity_tuning_table.py
# ============================================================

SEVERITY_RULES = {
    "critical": [
        "fatal",
        "corrupt",
        "fracture",
        "collapse",
        "override",
        "rift",
    ],
    "medium": [
        "instability",
        "unstable",
        "desync",
        "echo",
        "loop",
    ],
    "minor": [
        "missing",
        "optional",
        "fragment",
    ],
}
