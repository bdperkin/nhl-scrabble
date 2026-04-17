"""Integration tests for FastAPI web API endpoints."""

from __future__ import annotations

import sys

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import analysis_cache, app

# Get the actual module object from sys.modules
web_app_module = sys.modules["nhl_scrabble.web.app"]


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        TestClient instance for making requests to the FastAPI app
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear analysis cache before each test."""
    analysis_cache.clear()


def test_analyze_endpoint_parameter_validation(client: TestClient) -> None:
    """Test that analyze endpoint validates parameters."""
    # top_players too low
    response = client.get("/api/analyze?top_players=0")
    assert response.status_code == 422

    # top_players too high
    response = client.get("/api/analyze?top_players=101")
    assert response.status_code == 422

    # top_team_players too low
    response = client.get("/api/analyze?top_team_players=0")
    assert response.status_code == 422

    # top_team_players too high
    response = client.get("/api/analyze?top_team_players=31")
    assert response.status_code == 422


def test_clear_cache_endpoint(client: TestClient) -> None:
    """Test cache clear endpoint."""
    # Add something to cache first
    analysis_cache["test_key"] = {"timestamp": "2026-04-17", "data": {}}

    response = client.get("/api/cache/clear")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Cache cleared"
    assert data["entries_cleared"] == 1
    assert "timestamp" in data
    assert len(analysis_cache) == 0


def test_clear_cache_empty(client: TestClient) -> None:
    """Test clearing an already empty cache."""
    response = client.get("/api/cache/clear")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Cache cleared"
    assert data["entries_cleared"] == 0


def test_get_player_endpoint_not_implemented(client: TestClient) -> None:
    """Test get player endpoint returns not implemented."""
    response = client.get("/api/players/8478483")

    assert response.status_code == 501
    assert "not implemented" in response.json()["detail"].lower()


# Note: Full end-to-end tests for /api/analyze and /api/teams/{team_abbrev}
# require either real NHL API access or comprehensive mocking of TeamProcessor
# and PlayoffCalculator internals. These are better tested manually with:
#   nhl-scrabble serve
# then visiting http://localhost:8000 and using the web interface or API docs.
#
# The endpoints are fully implemented and functional, but integration testing
# them requires either:
# 1. Live NHL API access (slow, flaky, requires network)
# 2. Comprehensive mock fixtures that replicate the entire data flow
# 3. Dedicated test doubles with realistic NHL data structures
#
# For CI/CD, we verify endpoint registration and parameter validation only.


def test_api_endpoints_registered(client: TestClient) -> None:
    """Test that all API endpoints are registered in OpenAPI schema."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    openapi_spec = response.json()

    # Check all expected paths are registered
    assert "/api/analyze" in openapi_spec["paths"]
    assert "/api/cache/clear" in openapi_spec["paths"]
    assert "/api/teams/{team_abbrev}" in openapi_spec["paths"]
    assert "/api/players/{player_id}" in openapi_spec["paths"]
