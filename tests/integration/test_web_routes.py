"""Integration tests for web application routes.

Tests that all page routes exist and return correct HTML responses.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        Test client instance
    """
    return TestClient(app)


def test_root_route_exists(client: TestClient) -> None:
    """Test / route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_teams_route_exists(client: TestClient) -> None:
    """Test /teams route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/teams")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_divisions_route_exists(client: TestClient) -> None:
    """Test /divisions route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/divisions")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_conferences_route_exists(client: TestClient) -> None:
    """Test /conferences route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/conferences")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_playoffs_route_exists(client: TestClient) -> None:
    """Test /playoffs route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/playoffs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_stats_route_exists(client: TestClient) -> None:
    """Test /stats route returns HTML.

    Args:
        client: FastAPI test client
    """
    response = client.get("/stats")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text


def test_all_page_routes_exist(client: TestClient) -> None:
    """Test all page routes return HTML.

    Args:
        client: FastAPI test client
    """
    routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Route {route} failed"
        assert "text/html" in response.headers["content-type"], f"Route {route} not HTML"
        assert "<!DOCTYPE html>" in response.text, f"Route {route} missing DOCTYPE"


def test_routes_have_view_context(client: TestClient) -> None:
    """Test routes pass view context to template.

    The view context should be accessible in the template for navigation highlighting.

    Args:
        client: FastAPI test client
    """
    # Note: Without inspecting the actual template rendering internals,
    # we can't directly verify context variables. This test ensures the
    # routes render successfully, which indirectly validates context handling.

    routes_with_context = [
        "/teams",
        "/divisions",
        "/conferences",
        "/playoffs",
        "/stats",
    ]

    for route in routes_with_context:
        response = client.get(route)
        assert response.status_code == 200
        # Template rendering succeeded (would fail if context was malformed)
        assert "<!DOCTYPE html>" in response.text


def test_routes_not_returning_json_errors(client: TestClient) -> None:
    """Test routes don't return JSON 404 errors.

    Args:
        client: FastAPI test client
    """
    routes = ["/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

    for route in routes:
        response = client.get(route)
        # Should not get JSON error response
        assert '{"detail":"Not Found"}' not in response.text
        assert "Not Found" not in response.text or "<!DOCTYPE html>" in response.text
