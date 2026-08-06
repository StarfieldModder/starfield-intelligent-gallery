# ============================================================
#  TEMPLE RESONANCE ENGINE
#  Location: C:\IG\temple\temple_resonance_engine.py
# ============================================================

class TempleResonanceEngine:
    def __init__(self):
        self.resonance_level = 0
        self.events = []

    def register_event(self, source, description):
        """
        Registers a Temple event and adjusts resonance.
        """
        self.events.append((source, description))
        self.resonance_level += 1

    def dampen(self, amount=1):
        """
        Reduces resonance level.
        """
        self.resonance_level = max(0, self.resonance_level - amount)

    def status(self):
        if self.resonance_level >= 10:
            return "High resonance — Temple is vibrating with activity."
        if self.resonance_level >= 5:
            return "Moderate resonance — Temple is active."
        return "Low resonance — Temple is calm."
