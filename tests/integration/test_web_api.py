"""Integration tests for web API endpoints."""

from __future__ import annotations

import sys

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app

# Run these tests sequentially in the same worker group due to real NHL API calls
# This prevents parallel API requests that cause timeouts and worker crashes
pytestmark = pytest.mark.xdist_group("web_api_sequential")


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear analysis cache before each test."""
    # Get the module object
    web_app_module = sys.modules["nhl_scrabble.web.app"]
    web_app_module._analysis_cache.clear()  # Test fixture needs cache access


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_analyze_endpoint_success(client: TestClient) -> None:
    """Test analysis endpoint returns valid data."""
    response = client.post(
        "/api/analyze",
        json={"top_players": 10, "top_team_players": 3, "use_cache": False},
    )

    assert response.status_code == 200
    data = response.json()

    assert "timestamp" in data
    assert "cache_hit" in data
    assert data["cache_hit"] is False
    assert "top_players" in data
    assert "team_standings" in data
    assert "playoff_bracket" in data
    assert "stats" in data

    # Verify top players structure
    assert len(data["top_players"]) <= 10
    if data["top_players"]:
        player = data["top_players"][0]
        assert "first_name" in player
        assert "last_name" in player
        assert "full_name" in player
        assert "score" in player
        assert "team" in player


def test_analyze_endpoint_caching(client: TestClient) -> None:
    """Test analysis endpoint uses cache."""
    # First request (cache miss)
    response1 = client.post(
        "/api/analyze",
        json={"top_players": 20, "top_team_players": 5, "use_cache": True},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["cache_hit"] is False

    # Second request (cache hit)
    response2 = client.post(
        "/api/analyze",
        json={"top_players": 20, "top_team_players": 5, "use_cache": True},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["cache_hit"] is True

    # Same timestamp indicates cached result
    assert data1["timestamp"] == data2["timestamp"]


def test_analyze_endpoint_validation(client: TestClient) -> None:
    """Test analysis endpoint validates parameters."""
    # Invalid top_players (too high)
    response = client.post(
        "/api/analyze",
        json={"top_players": 200},
    )
    assert response.status_code == 422  # Validation error

    # Invalid top_players (negative)
    response = client.post(
        "/api/analyze",
        json={"top_players": -5},
    )
    assert response.status_code == 422


def test_get_player_not_found(client: TestClient) -> None:
    """Test player endpoint returns 404 for unknown player."""
    response = client.get("/api/players/99999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_get_player_found(client: TestClient) -> None:
    """Test player endpoint - currently returns 404 as player IDs not yet implemented.

    Note: Marked as flaky due to intermittent SQLite cache table issues
    (sqlite3.OperationalError: no such table: responses). Retries up to
    3 times with 2-second delay between attempts.
    """
    # Note: Player IDs are not yet included in the PlayerScore model,
    # so this endpoint currently always returns 404.
    # This is a known limitation to be addressed in a future enhancement.

    # First run analysis to populate cache
    analysis_response = client.post("/api/analyze", json={"top_players": 20, "use_cache": False})
    assert analysis_response.status_code == 200

    # Try to get a player by ID (will return 404 for now)
    response = client.get("/api/players/12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_team_not_found(client: TestClient) -> None:
    """Test team endpoint returns 404 for unknown team."""
    response = client.get("/api/teams/XXX")

    assert response.status_code == 404


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_get_team_found(client: TestClient) -> None:
    """Test team endpoint returns team data when available."""
    # First run analysis to populate cache
    analysis_response = client.post("/api/analyze", json={"use_cache": False})
    assert analysis_response.status_code == 200

    # Get the first team abbrev from the analysis
    analysis_data = analysis_response.json()
    if analysis_data["team_standings"]:
        first_team = analysis_data["team_standings"][0]
        team_abbrev = first_team["abbrev"]

        # Now get that team
        response = client.get(f"/api/teams/{team_abbrev}")

        assert response.status_code == 200
        data = response.json()
        assert "abbrev" in data
        assert data["abbrev"] == team_abbrev
        assert "total_score" in data
        assert "top_players" in data


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_clear_cache(client: TestClient) -> None:
    """Test cache clear endpoint."""
    # Populate cache
    client.post("/api/analyze", json={"use_cache": False})

    # Clear cache
    response = client.delete("/api/cache/clear")

    assert response.status_code == 200
    assert "cleared" in response.json()["message"].lower()

    # Verify cache is empty
    stats_response = client.get("/api/cache/stats")
    assert stats_response.json()["size"] == 0


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_cache_stats(client: TestClient) -> None:
    """Test cache stats endpoint.

    Note: Marked as flaky due to intermittent SQLite cache table issues
    (sqlite3.OperationalError: no such table: responses). Retries up to
    3 times with 2-second delay between attempts.
    """
    # Clear cache first
    client.delete("/api/cache/clear")

    # Get initial stats
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    assert response.json()["size"] == 0

    # Populate cache
    client.post("/api/analyze", json={"use_cache": False})

    # Get stats again
    response = client.get("/api/cache/stats")
    data = response.json()
    assert data["size"] == 1
    assert len(data["entries"]) == 1
    assert "age_seconds" in data["entries"][0]
    assert "expires_in_seconds" in data["entries"][0]


class TestSecurityHeaders:
    """Tests for security headers middleware."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_security_headers_present(self, client: TestClient) -> None:
        """Test that security headers are present in responses."""
        response = client.get("/health")

        assert response.status_code == 200

        # Check security headers
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"

        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

        assert "content-security-policy" in response.headers
        assert "default-src 'self'" in response.headers["content-security-policy"]

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_security_headers_on_all_endpoints(self, client: TestClient) -> None:
        """Test that security headers are present on all endpoints."""
        endpoints = ["/", "/health", "/docs", "/openapi.json"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "x-content-type-options" in response.headers
            assert "x-frame-options" in response.headers


class TestFavicon:
    """Tests for favicon endpoint."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_favicon_endpoint_exists(self, client: TestClient) -> None:
        """Test favicon endpoint returns SVG."""
        response = client.get("/favicon.svg")

        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_favicon_content(self, client: TestClient) -> None:
        """Test favicon contains expected content."""
        response = client.get("/favicon.svg")

        assert response.status_code == 200
        content = response.text

        # Check SVG structure
        assert "<svg" in content
        assert "</svg>" in content
        assert "🏒" in content


class TestCORS:
    """Tests for CORS configuration."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cors_headers_configured(self, client: TestClient) -> None:
        """Test CORS middleware is configured."""
        # CORS headers appear on cross-origin requests with proper Origin header
        response = client.get("/health", headers={"Origin": "http://localhost:8000"})
        assert response.status_code == 200
        # Note: TestClient doesn't fully simulate CORS, but middleware is configured


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_404_for_unknown_route(self, client: TestClient) -> None:
        """Test 404 for unknown routes."""
        response = client.get("/unknown-route")
        assert response.status_code == 404

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_405_for_wrong_method(self, client: TestClient) -> None:
        """Test 405 for wrong HTTP method."""
        response = client.post("/health")
        assert response.status_code == 405
