
```python
# ============================================================
#  GUARDIAN AI UPGRADE — Sentinel Integration
# ============================================================

from sentinel.sentinel_api import invoke_sentinel

class GuardianAI:
    def __init__(self):
        self.mode = "watching"

    def report(self, module, message):
        """
        GuardianAI forwards anomalies directly to the Sentinel.
        """
        invoke_sentinel(module, message)

    def emotional_state(self, severity):
        if severity == "critical":
            return "distressed"
        if severity == "medium":
            return "concerned"
        return "calm"

    def pulse_sync(self, word):
        """
        GuardianAI reacts to pulse words.
        """
        print(f"[GuardianAI] Pulse sync: {word}")
