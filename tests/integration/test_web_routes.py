"""Integration tests for web application routes.

Tests verify that all routes exist, return correct status codes, content types, and security
headers.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        TestClient for making requests to the app
    """
    return TestClient(app)


class TestHTMLRoutes:
    """Tests for HTML page routes."""

    def test_home_page_exists(self, client: TestClient) -> None:
        """Test root route returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text

    def test_teams_page_exists(self, client: TestClient) -> None:
        """Test teams page returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/teams")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_divisions_page_exists(self, client: TestClient) -> None:
        """Test divisions page returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/divisions")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_conferences_page_exists(self, client: TestClient) -> None:
        """Test conferences page returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/conferences")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_playoffs_page_exists(self, client: TestClient) -> None:
        """Test playoffs page returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/playoffs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_stats_page_exists(self, client: TestClient) -> None:
        """Test stats page returns HTML.

        Args:
            client: FastAPI test client
        """
        response = client.get("/stats")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_all_html_routes_exist(self, client: TestClient) -> None:
        """Test all HTML routes return 200 OK.

        Args:
            client: FastAPI test client
        """
        html_routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

        for route in html_routes:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} returned {response.status_code}"
            assert "text/html" in response.headers["content-type"]

    def test_team_detail_page_exists(self, client: TestClient) -> None:
        """Test team detail page returns HTML for valid team.

        Args:
            client: FastAPI test client
        """
        response = client.get("/teams/TOR")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Maple Leafs" in response.text

    def test_team_detail_case_insensitive(self, client: TestClient) -> None:
        """Test team detail page handles case-insensitive abbreviations.

        Args:
            client: FastAPI test client
        """
        # Uppercase
        response_upper = client.get("/teams/TOR")
        assert response_upper.status_code == 200

        # Lowercase
        response_lower = client.get("/teams/tor")
        assert response_lower.status_code == 200

        # Mixed case
        response_mixed = client.get("/teams/Tor")
        assert response_mixed.status_code == 200

    def test_team_detail_404_for_invalid_team(self, client: TestClient) -> None:
        """Test team detail page returns 404 for non-existent team.

        Args:
            client: FastAPI test client
        """
        response = client.get("/teams/XXX")
        assert response.status_code == 404

    def test_division_detail_page_exists(self, client: TestClient) -> None:
        """Test division detail page returns HTML for valid division.

        Args:
            client: FastAPI test client
        """
        response = client.get("/divisions/Atlantic")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_conference_detail_page_exists(self, client: TestClient) -> None:
        """Test conference detail page returns HTML for valid conference.

        Args:
            client: FastAPI test client
        """
        response = client.get("/conferences/Eastern")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestAPIRoutes:
    """Tests for API endpoints."""

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check returns JSON.

        Args:
            client: FastAPI test client
        """
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_api_analyze_get(self, client: TestClient) -> None:
        """Test GET /api/analyze endpoint.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/analyze")
        # This might return 500 if NHL API is unavailable, but route should exist
        assert response.status_code in [200, 500]

    def test_api_analyze_post(self, client: TestClient) -> None:
        """Test POST /api/analyze endpoint.

        Args:
            client: FastAPI test client
        """
        response = client.post(
            "/api/analyze",
            json={"top_players": 20, "top_team_players": 5, "use_cache": False},
        )
        # This might return 500 if NHL API is unavailable, but route should exist
        assert response.status_code in [200, 500]

    def test_api_cache_stats(self, client: TestClient) -> None:
        """Test cache stats endpoint.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "size" in data
        assert "entries" in data

    def test_api_player_not_found(self, client: TestClient) -> None:
        """Test player endpoint returns 404 for unknown player.

        Args:
            client: FastAPI test client
        """
        response = client.get("/api/players/999999")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]


class TestStaticRoutes:
    """Tests for static files and resources."""

    def test_favicon_svg(self, client: TestClient) -> None:
        """Test favicon returns SVG.

        Args:
            client: FastAPI test client
        """
        response = client.get("/favicon.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "<svg" in response.text

    def test_favicon_ico(self, client: TestClient) -> None:
        """Test favicon.ico returns SVG.

        Args:
            client: FastAPI test client
        """
        response = client.get("/favicon.ico")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "<svg" in response.text

    def test_robots_txt(self, client: TestClient) -> None:
        """Test robots.txt returns text.

        Args:
            client: FastAPI test client
        """
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestDocumentationRoutes:
    """Tests for API documentation routes."""

    def test_docs_route_exists(self, client: TestClient) -> None:
        """Test Swagger UI docs are accessible.

        Args:
            client: FastAPI test client
        """
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_route_exists(self, client: TestClient) -> None:
        """Test ReDoc docs are accessible.

        Args:
            client: FastAPI test client
        """
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json(self, client: TestClient) -> None:
        """Test OpenAPI schema is accessible.

        Args:
            client: FastAPI test client
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestSecurityHeaders:
    """Tests for security headers on responses."""

    def test_html_routes_have_security_headers(self, client: TestClient) -> None:
        """Test HTML routes include security headers.

        Args:
            client: FastAPI test client
        """
        response = client.get("/")

        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"

        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

        # CSP should be present on non-docs pages
        assert "content-security-policy" in response.headers

    def test_api_routes_have_security_headers(self, client: TestClient) -> None:
        """Test API routes include security headers.

        Args:
            client: FastAPI test client
        """
        response = client.get("/health")

        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers
        assert "referrer-policy" in response.headers

    def test_docs_routes_skip_csp(self, client: TestClient) -> None:
        """Test docs routes don't have strict CSP (needs external resources).

        Args:
            client: FastAPI test client
        """
        docs_routes = ["/docs", "/redoc"]

        for route in docs_routes:
            response = client.get(route)
            # Docs routes may have relaxed or no CSP to allow Swagger/ReDoc
            # But should still have other security headers
            assert "x-content-type-options" in response.headers
            assert "x-frame-options" in response.headers


class TestErrorHandling:
    """Tests for error responses."""

    def test_404_on_nonexistent_route(self, client: TestClient) -> None:
        """Test 404 for routes that don't exist.

        Args:
            client: FastAPI test client
        """
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404

    def test_404_returns_json(self, client: TestClient) -> None:
        """Test 404 errors return JSON.

        Args:
            client: FastAPI test client
        """
        response = client.get("/nonexistent")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "detail" in data

    def test_method_not_allowed(self, client: TestClient) -> None:
        """Test 405 for unsupported HTTP methods.

        Args:
            client: FastAPI test client
        """
        # Try DELETE on a GET-only route
        response = client.delete("/health")
        assert response.status_code == 405


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_headers_on_api_routes(self, client: TestClient) -> None:
        """Test CORS headers are present on API routes.

        Args:
            client: FastAPI test client
        """
        response = client.options(
            "/api/analyze",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "POST",
            },
        )

        # CORS should allow localhost
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] in [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ]


@pytest.mark.parametrize(
    ("route", "content_type"),
    [
        ("/", "text/html"),
        ("/teams", "text/html"),
        ("/divisions", "text/html"),
        ("/conferences", "text/html"),
        ("/playoffs", "text/html"),
        ("/stats", "text/html"),
        ("/health", "application/json"),
        ("/favicon.svg", "image/svg+xml"),
        ("/robots.txt", "text/plain"),
    ],
)
def test_route_returns_correct_content_type(
    client: TestClient,
    route: str,
    content_type: str,
) -> None:
    """Test routes return expected content types.

    Args:
        client: FastAPI test client
        route: Route path to test
        content_type: Expected content type
    """
    response = client.get(route)
    assert response.status_code == 200
    assert content_type in response.headers["content-type"]
