# ============================================================
#  MEMORY CHAMBER RIFT STABILIZER
#  Location: C:\IG\memory\memory_rift_stabilizer.py
# ============================================================

class MemoryRiftStabilizer:
    def __init__(self):
        self.active_rifts = 0

    def detect_rift(self, description):
        if "rift" in description.lower():
            self.active_rifts += 1
            return "Rift detected"
        return "No rift"

    def stabilize(self):
        if self.active_rifts > 0:
            self.active_rifts -= 1
            return "Rift stabilized"
        return "No active rifts"

    def status(self):
        if self.active_rifts > 0:
            return f"{self.active_rifts} active rift(s) in Memory Chamber."
        return "Memory Chamber stable."
