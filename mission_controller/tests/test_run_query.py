# mission_controller/tests/test_run_query.py
import pytest
from unittest.mock import MagicMock
from mission_controller.query import run_query

def test_run_query_happy_path_calls_db_and_returns_results(db_client):
    # Arrange
    db_client.find.return_value = ([{"id": "r1"}], 1)
    params = {"filters": {}, "page": 1, "page_size": 10}

    # Act
    result = run_query(params, db_client=db_client)

    # Assert
    assert isinstance(result, dict)
    assert "results" in result
    assert isinstance(result["results"], list)
    assert result.get("total", 0) == 1
    assert result.get("page", 1) == 1
    db_client.find.assert_called_once()

@pytest.mark.parametrize("bad_params", [None, {}, {"page": 0, "page_size": 10}, {"filters": "no"}])
def test_run_query_invalid_params_raise(bad_params, db_client):
    with pytest.raises(ValueError):
        run_query(bad_params, db_client=db_client)

def test_run_query_applies_filters_to_db(db_client):
    params = {"filters": {"name": "alpha", "min_score": 0.8}, "page": 1, "page_size": 5}
    run_query(params, db_client=db_client)
    db_client.find.assert_called_once()
    called_filter = db_client.find.call_args[0][0]
    assert isinstance(called_filter, dict)
    assert called_filter.get("name") == "alpha"

def test_run_query_pagination_limits_and_offsets(db_client):
    params = {"filters": {}, "page": 3, "page_size": 2}
    run_query(params, db_client=db_client)
    _, called_limit, called_offset, _ = db_client.find.call_args[0]
    assert called_limit == 2
    assert called_offset == 4

def test_run_query_db_error_propagates(db_client):
    db_client.find.side_effect = RuntimeError("db failure")
    with pytest.raises(RuntimeError):
        run_query({"filters": {}, "page": 1, "page_size": 10}, db_client=db_client)
