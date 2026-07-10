# mission_controller/tests/test_ingest_record.py
import pytest
from mission_controller.ingestion import ingest_record

def test_ingest_record_happy_path(storage_client, db_client):
    record = {"name": "sample", "data": b"bytes", "metadata": {"source": "sensor"}}
    db_client.insert.return_value = {"id": "rec-123"}
    storage_client.exists.return_value = False
    storage_client.upload.return_value = {"key": "obj-123"}

    result = ingest_record(record, storage_client=storage_client, db_client=db_client)

    assert isinstance(result, dict)
    assert result.get("status") == "ingested"
    assert result.get("id") == "rec-123"
    storage_client.exists.assert_called_once()
    storage_client.upload.assert_called_once()
    db_client.insert.assert_called_once()

def test_ingest_record_missing_fields_raises(storage_client, db_client):
    record = {"data": b"bytes"}  # missing 'name'
    with pytest.raises(ValueError):
        ingest_record(record, storage_client=storage_client, db_client=db_client)
    storage_client.upload.assert_not_called()
    db_client.insert.assert_not_called()

def test_ingest_record_storage_failure_raises(storage_client, db_client):
    record = {"name": "sample", "data": b"bytes"}
    storage_client.upload.side_effect = RuntimeError("storage unavailable")
    with pytest.raises(RuntimeError):
        ingest_record(record, storage_client=storage_client, db_client=db_client)
    db_client.insert.assert_not_called()

def test_ingest_record_db_failure_raises(storage_client, db_client):
    record = {"name": "sample", "data": b"bytes"}
    db_client.insert.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError):
        ingest_record(record, storage_client=storage_client, db_client=db_client)
    storage_client.upload.assert_called_once()

def test_ingest_record_skips_upload_if_exists(storage_client, db_client):
    record = {"name": "sample", "data": b"bytes"}
    storage_client.exists.return_value = True
    db_client.insert.return_value = {"id": "rec-existing"}

    result = ingest_record(record, storage_client=storage_client, db_client=db_client)

    assert result["id"] == "rec-existing"
    storage_client.exists.assert_called_once()
    storage_client.upload.assert_not_called()
    db_client.insert.assert_called_once()
