# mission_controller/tests/test_director_stress.py
import threading
import time
import pytest

from mission_controller.director import MissionDirector
from mission_controller.worker_manager import WorkerManager

# Mark as flaky so transient timing failures are retried in CI (requires pytest-rerunfailures)
@pytest.mark.flaky(reruns=3, reruns_delay=0.2)
def test_stress_concurrent_dispatch():
    director = MissionDirector(worker_manager=WorkerManager())

    created = []
    lock = threading.Lock()

    def create_and_start(i):
        mid = director.create_mission(f"stress-{i}", {"i": i})
        # small jitter to increase interleaving
        time.sleep(0.005 * (i % 4))
        director.start_mission(mid)
        with lock:
            created.append(mid)

    threads = [threading.Thread(target=create_and_start, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    # Basic sanity checks
    assert len(created) == 50
    dispatched = director._workers.dispatched()
    assert len(dispatched) == 50
    dispatched_ids = {rec[1]["id"] for rec in dispatched}
    assert dispatched_ids == set(created)
