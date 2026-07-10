# mission_controller/tests/conftest.py
import asyncio
import threading
import inspect
import pytest
from unittest.mock import MagicMock

from mission_controller.director import MissionDirector
from mission_controller.worker_manager import WorkerManager


def run_coro_sync(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()
        asyncio.set_event_loop(None)


def make_dispatch_sync(worker):
    dispatch = getattr(worker, "dispatch", None)
    if dispatch is None:
        return worker
    if not inspect.iscoroutinefunction(dispatch):
        return worker
    original = dispatch
    def sync_dispatch(mission_record):
        return run_coro_sync(original(mission_record))
    setattr(worker, "dispatch", sync_dispatch)
    return worker


@pytest.fixture
def db_client():
    db = MagicMock()
    db.insert.return_value = {"id": "rec-000"}
    db.find.return_value = ([], 0)
    return db


@pytest.fixture
def storage_client():
    s = MagicMock()
    s.exists.return_value = False
    s.upload.return_value = {"key": "obj-000"}
    return s


@pytest.fixture
def classifier():
    c = MagicMock()
    c.classify.return_value = {"label": "unknown", "score": 0.5}
    return c


@pytest.fixture
def director_with_sync_worker():
    worker = WorkerManager()
    make_dispatch_sync(worker)
    director = MissionDirector(worker_manager=worker)
    return director, worker
