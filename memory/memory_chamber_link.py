# ============================================================
#  MEMORY CHAMBER LINK — Sentinel Integration
# ============================================================

from sentinel.sentinel_api import invoke_sentinel

def check_memory_integrity(memory_state):
    """
    Detects memory rifts, anomalies, or desync.
    """

    if "rift" in memory_state.lower():
        invoke_sentinel("MemoryChamber", "memory rift detected")

    if "echo" in memory_state.lower():
        invoke_sentinel("MemoryChamber", "echo instability")

    if "fragment" in memory_state.lower():
        invoke_sentinel("MemoryChamber", "memory fragment instability")
