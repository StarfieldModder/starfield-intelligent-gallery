# ============================================================
#  GUARDIAN PERSONALITY EXPANSION
#  Location: C:\IG\guardian\guardian_personality_expansion.py
# ============================================================

class GuardianPersonality:
    def __init__(self):
        self.mood = "calm"

    def update_mood(self, severity):
        if severity == "critical":
            self.mood = "distressed"
        elif severity == "medium":
            self.mood = "concerned"
        else:
            self.mood = "calm"

    def react_to_pulse(self, pulse_word):
        if pulse_word == "bright":
            return "The Guardian feels the Temple’s heartbeat intensify."
        if pulse_word == "medium":
            return "The Guardian senses rising tension."
        return "The Guardian remains steady."

    def describe(self):
        if self.mood == "distressed":
            return "Guardian is on high alert."
        if self.mood == "concerned":
            return "Guardian is watching closely."
        return "Guardian is calm and observant."
