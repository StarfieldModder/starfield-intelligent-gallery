# mission_controller/query.py
from typing import Any, Dict, Tuple, List

def run_query(params: Dict[str, Any], db_client=None) -> Dict[str, Any]:
    """
    Minimal run_query stub for tests.
    Expects params with 'filters', 'page', 'page_size'.
    """
    if not params or not isinstance(params, dict):
        raise ValueError("invalid params")
    page = int(params.get("page", 1))
    page_size = int(params.get("page_size", 10))
    filters = params.get("filters", {})

    # If a db_client is provided, call its find method; otherwise return empty results
    if db_client:
        results, total = db_client.find(filters, page_size, (page - 1) * page_size, None)
    else:
        results, total = [], 0

    return {"results": list(results), "total": total, "page": page, "page_size": page_size}
