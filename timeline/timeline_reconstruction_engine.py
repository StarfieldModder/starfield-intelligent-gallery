# ============================================================
#  TIMELINE RECONSTRUCTION ENGINE
#  Location: C:\IG\timeline\timeline_reconstruction_engine.py
# ============================================================

class TimelineReconstructionEngine:
    def __init__(self):
        self.events = []
        self.reconstructed = []

    def add_event(self, timestamp, description):
        self.events.append((timestamp, description))

    def reconstruct(self):
        """
        Simple reconstruction: sort by timestamp.
        """
        self.reconstructed = sorted(self.events, key=lambda e: e[0])
        return self.reconstructed

    def summary(self):
        if not self.reconstructed:
            return "No reconstructed timeline yet."
        return f"Reconstructed {len(self.reconstructed)} events into a coherent timeline."
