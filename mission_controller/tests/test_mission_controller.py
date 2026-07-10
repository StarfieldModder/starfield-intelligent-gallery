# mission_controller/tests/test_mission_controller.py
import pytest
from unittest.mock import MagicMock
from mission_controller import process_mission

def test_process_mission_happy_path():
    payload = {"mission_name": "alpha", "image": b"fake-bytes", "metadata": {"priority": 1}}
    fake_db = MagicMock()
    fake_db.insert.return_value = {"id": "rec-123"}
    fake_classifier = MagicMock()
    fake_classifier.classify.return_value = {"label": "target", "score": 0.92}

    result = process_mission(payload, db_client=fake_db, classifier=fake_classifier)

    assert isinstance(result, dict)
    assert result["status"] == "ok"
    assert result["id"] == "rec-123"
    assert 0.0 <= result["score"] <= 1.0
    fake_db.insert.assert_called_once()
    fake_classifier.classify.assert_called_once_with(payload["image"])
