# mission_controller/__init__.py
"""
Safe package initializer that avoids hard failure when optional submodules are missing.
Expose MissionDirector if available; otherwise provide None and a lazy accessor.
"""

from typing import Any, Optional

__all__ = ["MissionDirector", "MissionNotFoundError", "get_mission_director"]

try:
    from .director import MissionDirector, MissionNotFoundError  # type: ignore
except Exception:
    MissionDirector = None  # type: ignore
    MissionNotFoundError = None  # type: ignore

def get_mission_director(db_client: Optional[Any] = None, worker_manager: Optional[Any] = None):
    if MissionDirector is None:
        raise ImportError("mission_controller.director is not available. Add director.py or the stub.")
    return MissionDirector(db_client=db_client, worker_manager=worker_manager)

# mission_controller/__init__.py
"""
Safe package initializer that avoids hard failure when optional submodules are missing.
Expose MissionDirector and common helpers if available.
"""

from typing import Any, Optional

__all__ = ["MissionDirector", "MissionNotFoundError", "get_mission_director", "process_mission", "run_query"]

# import director if present
try:
    from .director import MissionDirector, MissionNotFoundError  # type: ignore
except Exception:
    MissionDirector = None  # type: ignore
    MissionNotFoundError = None  # type: ignore

# try to import process_mission and run_query if they exist
try:
    from .process import process_mission  # type: ignore
except Exception:
    # Provide a minimal stub so tests that import the name don't fail at import time.
    def process_mission(*args, **kwargs):
        raise ImportError("mission_controller.process.process_mission is not available in this environment")

try:
    from .query import run_query  # type: ignore
except Exception:
    def run_query(*args, **kwargs):
        raise ImportError("mission_controller.query.run_query is not available in this environment")

def get_mission_director(db_client: Optional[Any] = None, worker_manager: Optional[Any] = None):
    if MissionDirector is None:
        raise ImportError("mission_controller.director is not available. Add director.py or the stub.")
    return MissionDirector(db_client=db_client, worker_manager=worker_manager)

# mission_controller/__init__.py (add or update)
try:
    from .process import process_mission  # type: ignore
except Exception:
    def process_mission(*args, **kwargs):
        raise ImportError("mission_controller.process.process_mission is not available in this environment")
