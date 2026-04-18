"""Integration tests for FastAPI web infrastructure."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble import __version__
from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        TestClient instance for making requests to the FastAPI app
    """
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint returns correct structure."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns API information."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    # Check that the JSON contains expected navigation links
    data = response.json()
    assert data["message"] == "NHL Scrabble Analyzer API"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_openapi_docs_available(client: TestClient) -> None:
    """Test OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs_available(client: TestClient) -> None:
    """Test ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_json_available(client: TestClient) -> None:
    """Test OpenAPI JSON spec is available."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert data["info"]["title"] == "NHL Scrabble Analyzer"
    assert data["info"]["version"] == __version__


def test_static_css_available(client: TestClient) -> None:
    """Test static CSS file is served correctly."""
    response = client.get("/static/css/style.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")

    # Check for some CSS content
    css_content = response.text
    assert "--color-primary" in css_content
    assert "--color-secondary" in css_content
    assert "NHL blue" in css_content


def test_static_js_available(client: TestClient) -> None:
    """Test static JavaScript file is served correctly."""
    response = client.get("/static/js/app.js")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/javascript"
    ) or response.headers["content-type"].startswith("text/javascript")

    # Check for some JS content
    js_content = response.text
    assert "analysisForm" in js_content
    assert "handleFormSubmit" in js_content


@pytest.mark.skip(reason="HTML templates not yet implemented - API endpoints only")
def test_home_page_has_form(client: TestClient) -> None:
    """Test home page contains the analysis form.

    Note: This test requires HTML templates which will be added in a future PR.
    Currently, the root endpoint returns JSON API information.
    """
    response = client.get("/")

    assert response.status_code == 200
    html_content = response.text

    # Check for form elements
    assert '<form id="analysisForm"' in html_content
    assert 'id="topPlayers"' in html_content
    assert 'id="topTeamPlayers"' in html_content
    assert 'id="useCache"' in html_content
    assert 'type="submit"' in html_content


@pytest.mark.skip(reason="HTML templates not yet implemented - API endpoints only")
def test_home_page_has_info_section(client: TestClient) -> None:
    """Test home page contains informational sections.

    Note: This test requires HTML templates which will be added in a future PR.
    Currently, the root endpoint returns JSON API information.
    """
    response = client.get("/")

    assert response.status_code == 200
    html_content = response.text

    # Check for info content
    assert "Scrabble Letter Values" in html_content
    assert "1 point:" in html_content
    assert "10 points:" in html_content
