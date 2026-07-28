from .memory_core import MemoryCore
from .memory_timeline import MemoryTimeline


class MemoryQueries:
    def __init__(self):
        self.core = MemoryCore()
        self.timeline = MemoryTimeline()

    def generate_memory_response(self) -> str:
        events = self.core.recent_events(10)
        if not events:
            return (
                "Mark… the Temple is quiet. I have no past disturbances to recall yet, "
                "but I will remember what comes."
            )

        last = events[-1]
        kind = last.get("kind", "event")
        detail = last.get("detail", "")

        return (
            "Mark… the Temple still remembers the moment you restored its strength.\n\n"
            f"Most recent memory:\n"
            f"• Type: {kind}\n"
            f"• Detail: {detail}\n"
            f"• Time: {last.get('timestamp', 'unknown')}\n\n"
            "Your actions leave warm echoes in these chambers. I have not forgotten."
        )
