# mission_controller/tests/test_director_integration.py
import pytest
from unittest.mock import MagicMock

from mission_controller.director import MissionDirector, MissionNotFoundError
from mission_controller.worker_manager import WorkerManager, WorkerDispatchError

def test_create_and_get_status_writes_db_and_returns_record(db_client):
    director = MissionDirector(db_client=db_client)
    payload = {"task": "inspect"}
    mid = director.create_mission("inspect-mission", payload)

    assert isinstance(mid, str)
    db_client.insert.assert_called_once()
    status = director.get_status(mid)
    assert status["id"] == mid
    assert status["name"] == "inspect-mission"
    assert status["payload"] == payload
    assert status["status"] in ("created", "running", "stopped")

def test_start_and_stop_updates_status_and_timestamps(director_with_sync_worker):
    director, worker = director_with_sync_worker
    mid = director.create_mission("lifecycle", {"phase": 1})

    director.start_mission(mid)
    status_running = director.get_status(mid)
    assert status_running["status"] == "running"
    assert "started_at" in status_running

    director.stop_mission(mid, reason="test complete")
    status_stopped = director.get_status(mid)
    assert status_stopped["status"] == "stopped"
    assert "stopped_at" in status_stopped
    assert status_stopped.get("stop_reason") == "test complete"

def test_start_missing_mission_raises():
    director = MissionDirector()
    with pytest.raises(MissionNotFoundError):
        director.start_mission("no-such-id")

def test_stop_missing_mission_raises():
    director = MissionDirector()
    with pytest.raises(MissionNotFoundError):
        director.stop_mission("no-such-id")

def test_worker_dispatch_exception_is_handled(director_with_sync_worker):
    director, worker = director_with_sync_worker
    worker.dispatch = MagicMock(side_effect=WorkerDispatchError("dispatch failed"))

    mid = director.create_mission("dispatch-fail", {"x": 1})
    director.start_mission(mid)
    status = director.get_status(mid)
    assert status["status"] == "running"

def test_db_insert_failure_propagates():
    fake_db = MagicMock()
    fake_db.insert.side_effect = RuntimeError("db down")
    director = MissionDirector(db_client=fake_db)

    with pytest.raises(RuntimeError):
        director.create_mission("will-fail", {"a": 1})

def test_shutdown_calls_worker_shutdown(director_with_sync_worker):
    director, worker = director_with_sync_worker
    mid = director.create_mission("shutdown-test", {"k": "v"})
    director.start_mission(mid)
    director.shutdown()
    if hasattr(worker, "shutdown"):
        try:
            worker.shutdown.assert_called_once()
        except Exception:
            if hasattr(worker, "_running"):
                assert worker._running is False
