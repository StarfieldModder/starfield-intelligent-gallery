# mission_controller/ingestion.py
from typing import Any, Dict, Optional

class IngestionError(Exception):
    pass

def ingest_record(record: Dict[str, Any], storage_client: Optional[Any] = None, db_client: Optional[Any] = None) -> Dict[str, Any]:
    """
    Minimal ingest_record for tests.
    - Validates required fields.
    - If storage_client provided, uploads (propagates storage exceptions).
    - If db_client provided, inserts and returns inserted id (propagates db exceptions).
    - On success returns a dict including 'id', 'name', and 'status' == 'ingested'.
    """
    if not isinstance(record, dict) or "name" not in record:
        raise ValueError("record must be a dict and include 'name'")

    # storage upload (propagate exceptions so tests can observe them)
    if storage_client:
        key = f"obj-{record.get('name')}"
        if not storage_client.exists(key):
            storage_client.upload(key, record.get("data", b""))

    # db insert (propagate exceptions)
    inserted_id = None
    if db_client:
        res = db_client.insert({"name": record["name"], "metadata": record.get("metadata", {})})
        inserted_id = res.get("id") if isinstance(res, dict) else res

    return {"id": inserted_id, "name": record["name"], "status": "ingested"}
