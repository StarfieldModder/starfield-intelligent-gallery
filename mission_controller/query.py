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

# mission_controller/query.py
from typing import Any, Dict, List, Tuple

def run_query(params: Dict[str, Any], db_client=None) -> Dict[str, Any]:
    # Validate params
    if not isinstance(params, dict):
        raise ValueError("params must be a dict")
    page = params.get("page")
    page_size = params.get("page_size")
    filters = params.get("filters")

    if page is None or page_size is None or not isinstance(filters, dict):
        raise ValueError("invalid params: require 'filters' dict, 'page' >= 1, 'page_size' >= 1")

    try:
        page = int(page)
        page_size = int(page_size)
    except Exception:
        raise ValueError("page and page_size must be integers")

    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be >= 1")

    # If db_client provided, call its find method; otherwise return empty results
    if db_client and hasattr(db_client, "find"):
        results, total = db_client.find(filters, page_size, (page - 1) * page_size, None)
    else:
        results, total = [], 0

    return {"results": list(results), "total": total, "page": page, "page_size": page_size}
