# ============================================================
#  GUARDIAN EMOTION MATRIX
#  Location: C:\IG\guardian\guardian_emotion_matrix.py
# ============================================================

class GuardianEmotionMatrix:
    def __init__(self):
        self.severity = "minor"
        self.pulse = "soft"

    def update(self, severity, pulse_word):
        self.severity = severity
        self.pulse = pulse_word

    def current_state(self):
        if self.severity == "critical" and self.pulse == "bright":
            return "Guardian is highly distressed."
        if self.severity == "medium":
            return "Guardian is concerned."
        return "Guardian is calm."

    def describe(self):
        return f"Emotion Matrix — severity: {self.severity}, pulse: {self.pulse}"
