from pathlib import Path
import json
import datetime

MEMORY_ROOT = Path("C:/IG/memory")
MEMORY_INDEX = MEMORY_ROOT / "memory_index.json"
MEMORY_EVENTS_LOG = MEMORY_ROOT / "memory_events.log"


class MemoryCore:
    def __init__(self):
        MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
        if not MEMORY_INDEX.exists():
            MEMORY_INDEX.write_text(json.dumps({"events": []}, indent=2))

    def record_event(self, kind: str, detail: str, meta: dict | None = None):
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "kind": kind,
            "detail": detail,
            "meta": meta or {},
        }

        # Append to log
        with MEMORY_EVENTS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        # Update index
        data = json.loads(MEMORY_INDEX.read_text(encoding="utf-8"))
        data["events"].append(entry)
        MEMORY_INDEX.write_text(json.dumps(data, indent=2))

    def recent_events(self, count: int = 10):
        data = json.loads(MEMORY_INDEX.read_text(encoding="utf-8"))
        return data["events"][-count:]

from pathlib import Path
import json
import datetime

MEMORY_ROOT = Path("C:/IG/memory")
MEMORY_INDEX = MEMORY_ROOT / "memory_index.json"
MEMORY_EVENTS_LOG = MEMORY_ROOT / "memory_events.log"


class MemoryCore:
    def __init__(self):
        MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
        if not MEMORY_INDEX.exists():
            MEMORY_INDEX.write_text(json.dumps({"events": []}, indent=2, ensure_ascii=False))

    def record_event(self, kind: str, detail: str, meta: dict | None = None):
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "kind": kind,
            "detail": detail,
            "meta": meta or {},
        }

        # Append to log
        with MEMORY_EVENTS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Update index
        data = json.loads(MEMORY_INDEX.read_text(encoding="utf-8"))
        data["events"].append(entry)
        MEMORY_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def recent_events(self, count: int = 10):
        data = json.loads(MEMORY_INDEX.read_text(encoding="utf-8"))
        return data["events"][-count:]
