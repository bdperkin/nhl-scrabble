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
    data = response.json()

    assert "message" in data
    assert "docs" in data
    assert "health" in data
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
