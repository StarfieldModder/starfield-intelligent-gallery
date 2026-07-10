# mission_controller/tests/test_director_worker_integration.py
import time
import pytest
from unittest.mock import MagicMock

from mission_controller.director import MissionDirector, MissionNotFoundError
from mission_controller.worker_manager import WorkerManager, WorkerDispatchError

def test_create_mission_writes_to_db_and_returns_id():
    fake_db = MagicMock()
    director = MissionDirector(db_client=fake_db)
    payload = {"foo": "bar"}

    mid = director.create_mission("test-mission", payload)

    assert isinstance(mid, str)
    fake_db.insert.assert_called_once()
    stored_record = fake_db.insert.call_args[0][0]
    assert stored_record["id"] == mid
    assert stored_record["name"] == "test-mission"
    assert stored_record["payload"] == payload

def test_register_worker_manager_and_dispatch_on_start():
    director = MissionDirector()
    wm = WorkerManager()
    director.register_worker_manager(wm)

    mid = director.create_mission("dispatch-mission", {"x": 1})
    director.start_mission(mid)

    dispatched = wm.dispatched()
    assert len(dispatched) == 1
    dispatch_id, mission_record = dispatched[0]
    assert isinstance(dispatch_id, str)
    assert mission_record["id"] == mid
    assert mission_record["status"] in ("created", "running")

def test_start_mission_calls_mock_worker_manager_dispatch():
    fake_worker = MagicMock()
    director = MissionDirector(worker_manager=fake_worker)

    mid = director.create_mission("mock-dispatch", {"a": 1})
    director.start_mission(mid)

    fake_worker.dispatch.assert_called_once()
    called_arg = fake_worker.dispatch.call_args[0][0]
    assert called_arg["id"] == mid

def test_shutdown_calls_worker_manager_shutdown():
    fake_worker = MagicMock()
    director = MissionDirector(worker_manager=fake_worker)

    # create and start a mission to ensure worker manager is used
    mid = director.create_mission("to-shutdown", {"k": "v"})
    director.start_mission(mid)

    director.shutdown()
    fake_worker.shutdown.assert_called_once()

def test_start_mission_missing_raises_mission_not_found():
    director = MissionDirector()
    with pytest.raises(MissionNotFoundError):
        director.start_mission("non-existent-id")

def test_dispatch_failure_is_handled_and_does_not_raise():
    # WorkerManager.dispatch raises WorkerDispatchError when shut down.
    wm = WorkerManager()
    director = MissionDirector(worker_manager=wm)

    mid = director.create_mission("will-fail-dispatch", {"p": 2})
    # shut down the worker manager so dispatch will raise
    wm.shutdown()

    # start_mission swallows dispatch exceptions in the stub; ensure no exception is raised
    director.start_mission(mid)

    # mission should be marked as running even if dispatch failed
    status = director.get_status(mid)
    assert status["status"] == "running"
    # no dispatches should have been recorded
    assert wm.dispatched() == []
