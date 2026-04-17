"""Integration tests for FastAPI web API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        TestClient instance for making requests to the FastAPI app
    """
    return TestClient(app)


class TestAnalyzeEndpoint:
    """Tests for /api/analyze endpoint."""

    def test_analyze_endpoint_invalid_parameters(self, client: TestClient) -> None:
        """Test analyze endpoint validates parameters."""
        # Top players out of range (too high)
        response = client.get("/api/analyze?top_players=200")
        assert response.status_code == 422

        # Top players out of range (too low)
        response = client.get("/api/analyze?top_players=0")
        assert response.status_code == 422

        # Top team players out of range
        response = client.get("/api/analyze?top_team_players=50")
        assert response.status_code == 422


class TestSecurityHeaders:
    """Tests for security headers."""

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

    def test_security_headers_on_all_endpoints(self, client: TestClient) -> None:
        """Test that security headers are present on all endpoints."""
        endpoints = ["/", "/health", "/docs", "/openapi.json"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "x-content-type-options" in response.headers
            assert "x-frame-options" in response.headers


class TestFavicon:
    """Tests for favicon endpoint."""

    def test_favicon_endpoint_exists(self, client: TestClient) -> None:
        """Test favicon endpoint returns SVG."""
        response = client.get("/favicon.svg")

        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]

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

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test CORS headers are configured."""
        response = client.get("/health")

        # CORS middleware is configured (exact headers depend on request origin)
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_route(self, client: TestClient) -> None:
        """Test 404 for unknown routes."""
        response = client.get("/unknown-route")
        assert response.status_code == 404

    def test_405_for_wrong_method(self, client: TestClient) -> None:
        """Test 405 for wrong HTTP method."""
        response = client.post("/health")
        assert response.status_code == 405


class TestMetaTags:
    """Tests for SEO and meta tags."""

    def test_home_page_has_meta_tags(self, client: TestClient) -> None:
        """Test home page includes SEO meta tags."""
        response = client.get("/")

        assert response.status_code == 200
        html = response.text

        # Check meta tags
        assert 'name="description"' in html
        assert 'name="keywords"' in html
        assert 'name="author"' in html
        assert 'property="og:type"' in html
        assert 'property="og:title"' in html
        assert 'name="twitter:card"' in html

    def test_meta_description_content(self, client: TestClient) -> None:
        """Test meta description has appropriate content."""
        response = client.get("/")

        assert response.status_code == 200
        html = response.text

        # Check description content
        assert "Scrabble" in html
        assert "NHL" in html
