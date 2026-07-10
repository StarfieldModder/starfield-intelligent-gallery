# mission_controller/ingestion.py
from typing import Any, Dict, Optional

class IngestionError(Exception):
    pass

def ingest_record(record: Dict[str, Any], storage_client: Optional[Any] = None, db_client: Optional[Any] = None) -> Dict[str, Any]:
    """
    Minimal ingest_record stub for tests and local development.
    Validates required fields, optionally uploads to storage_client, and inserts to db_client.
    """
    if not isinstance(record, dict) or "name" not in record:
        raise ValueError("record must be a dict and include 'name'")

    # simulate storage upload if provided
    if storage_client:
        key = f"obj-{record.get('name')}"
        try:
            if not storage_client.exists(key):
                storage_client.upload(key, record.get("data", b""))
        except Exception:
            raise IngestionError("storage failure")

    # simulate DB insert if provided
    if db_client:
        try:
            res = db_client.insert({"name": record["name"], "metadata": record.get("metadata", {})})
            inserted_id = res.get("id") if isinstance(res, dict) else res
        except Exception:
            raise IngestionError("db failure")
    else:
        inserted_id = "stub-id"

    return {"status": "ingested", "id": inserted_id}
