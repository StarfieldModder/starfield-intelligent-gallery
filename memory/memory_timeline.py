from pathlib import Path
import json

MEMORY_ROOT = Path("C:/IG/memory")
MEMORY_INDEX = MEMORY_ROOT / "memory_index.json"


class MemoryTimeline:
    def __init__(self):
        MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
        if not MEMORY_INDEX.exists():
            MEMORY_INDEX.write_text(json.dumps({"events": []}, indent=2, ensure_ascii=False))

    def get_timeline(self):
        data = json.loads(MEMORY_INDEX.read_text(encoding="utf-8"))
        return data["events"]

    def get_summary(self, max_events: int = 50):
        events = self.get_timeline()
        return events[-max_events:]
