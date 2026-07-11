# mission_controller/process.py
from typing import Any, Dict, Optional

def _clamp_and_round_score(raw_score: Optional[float]) -> Optional[float]:
    if raw_score is None:
        return None
    clamped = max(0.0, min(1.0, float(raw_score)))
    return round(clamped, 4)

def process_mission(payload: Dict[str, Any], db_client: Optional[Any] = None, classifier: Optional[Any] = None) -> Dict[str, Any]:
    """
    Minimal process_mission used by tests:
    - payload must include 'mission_name'
    - if 'image' present and classifier provided, call classifier.classify(image)
    - insert a record into db_client and return a result dict with id, label (if any), score (if any), and status 'ok'
    """
    if not isinstance(payload, dict) or "mission_name" not in payload:
        raise ValueError("payload must include 'mission_name'")

    result: Dict[str, Any] = {"mission_name": payload["mission_name"]}

    # classify if image present
    if "image" in payload and classifier is not None:
        classification = classifier.classify(payload["image"])
        label = classification.get("label")
        raw_score = classification.get("score")
        score = _clamp_and_round_score(raw_score)
        result.update({"label": label, "score": score})
    else:
        result.update({"label": None, "score": None})

    # write to DB if provided
    if db_client:
        db_res = db_client.insert({"mission_name": payload["mission_name"], "metadata": payload.get("metadata", {})})
        inserted_id = db_res.get("id") if isinstance(db_res, dict) else db_res
        result["id"] = inserted_id

    # test suite expects a status field
    result["status"] = "ok"
    return result
