# mission_controller/tests/test_process_mission.py
import math
import pytest
from unittest.mock import MagicMock

# Import the function under test. Adjust this import if your function lives elsewhere.
from mission_controller import process_mission

# Shared fixtures
@pytest.fixture
def fake_db():
    db = MagicMock()
    db.insert.return_value = {"id": "rec-000"}
    return db

@pytest.fixture
def fake_classifier():
    clf = MagicMock()
    clf.classify.return_value = {"label": "unknown", "score": 0.5}
    return clf

# 1. Happy path: normal payload with image
def test_happy_path_calls_db_and_classifier(fake_db, fake_classifier):
    payload = {"mission_name": "alpha", "image": b"fake-bytes", "metadata": {"priority": 1}}
    fake_db.insert.return_value = {"id": "rec-123"}
    fake_classifier.classify.return_value = {"label": "target", "score": 0.92}

    result = process_mission(payload, db_client=fake_db, classifier=fake_classifier)

    assert isinstance(result, dict)
    assert result["status"] == "ok"
    assert result["id"] == "rec-123"
    assert 0.0 <= result["score"] <= 1.0
    fake_db.insert.assert_called_once()
    fake_classifier.classify.assert_called_once_with(payload["image"])

# 2. Empty payload should raise a validation error
def test_empty_payload_raises_value_error(fake_db, fake_classifier):
    with pytest.raises(ValueError):
        process_mission({}, db_client=fake_db, classifier=fake_classifier)

# 3. No image: DB still written, classifier not called
def test_no_image_skips_classifier_but_writes_db(fake_db, fake_classifier):
    payload = {"mission_name": "no-image", "metadata": {"priority": 2}}
    fake_db.insert.return_value = {"id": "rec-456"}

    result = process_mission(payload, db_client=fake_db, classifier=fake_classifier)

    assert result["id"] == "rec-456"
    fake_db.insert.assert_called_once()
    fake_classifier.classify.assert_not_called()

# 4. Database failure propagates as exception
def test_db_failure_is_propagated(fake_db, fake_classifier):
    payload = {"mission_name": "alpha", "image": b"img"}
    fake_db.insert.side_effect = RuntimeError("db down")
    fake_classifier.classify.return_value = {"label": "x", "score": 0.5}

    with pytest.raises(RuntimeError):
        process_mission(payload, db_client=fake_db, classifier=fake_classifier)

# 5. Score clamping and rounding behavior at numeric edges
@pytest.mark.parametrize("raw_score,expected_score", [
    (1.2, 1.0),
    (-0.1, 0.0),
    (0.3333333, round(0.3333333, 4)),
])
def test_score_clamping_and_rounding(fake_db, fake_classifier, raw_score, expected_score):
    payload = {"mission_name": "edge", "image": b"img"}
    fake_db.insert.return_value = {"id": "rec-edge"}
    fake_classifier.classify.return_value = {"label": "edge", "score": raw_score}

    result = process_mission(payload, db_client=fake_db, classifier=fake_classifier)

    assert math.isclose(result["score"], expected_score, rel_tol=1e-9)
    assert result["id"] == "rec-edge"
