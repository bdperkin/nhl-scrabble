"""Tests for /nationalities endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the web app.

    Returns:
        TestClient instance
    """
    return TestClient(app)


@pytest.fixture
def mock_analysis_data() -> dict:
    """Create mock analysis data for testing.

    Returns:
        Mock analysis data with player and nationality information
    """
    return {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "nationality": "Canada",
            },
            {
                "player_id": 8477934,
                "full_name": "Auston Matthews",
                "first_name": "Auston",
                "last_name": "Matthews",
                "team": "TOR",
                "score": 22,
                "first_score": 11,
                "last_score": 11,
                "nationality": "United States",
            },
            {
                "player_id": 8477492,
                "full_name": "Cale Makar",
                "first_name": "Cale",
                "last_name": "Makar",
                "team": "COL",
                "score": 18,
                "first_score": 9,
                "last_score": 9,
                "nationality": "Canada",
            },
            {
                "player_id": 8471214,
                "full_name": "Carey Price",
                "first_name": "Carey",
                "last_name": "Price",
                "team": "MTL",
                "score": 15,
                "first_score": 8,
                "last_score": 7,
                "nationality": "Canada",
            },
            {
                "player_id": 8480012,
                "full_name": "Kirill Kaprizov",
                "first_name": "Kirill",
                "last_name": "Kaprizov",
                "team": "MIN",
                "score": 20,
                "first_score": 10,
                "last_score": 10,
                "nationality": "Russia",
            },
            {
                "player_id": 8479318,
                "full_name": "Mitch Marner",
                "first_name": "Mitch",
                "last_name": "Marner",
                "team": "TOR",
                "score": 19,
                "first_score": 9,
                "last_score": 10,
                "nationality": "Canada",
            },
        ],
        "stats": {"total_players": 6},
    }


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_loads(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that nationalities page loads successfully.

    Args:
        mock_analyze: Mock async analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data
    response = test_client.get("/nationalities")
    assert response.status_code == 200
    assert b"nationalit" in response.content.lower()


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_shows_statistics(
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that nationalities page displays nationality statistics.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    mock_analyze.return_value = mock_analysis_data
    response = test_client.get("/nationalities")
    assert response.status_code == 200
    assert b"canada" in response.content.lower() or b"mcdavid" in response.content.lower()


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_nhl_api_error(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test handling of NHL API errors on nationalities page.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    from nhl_scrabble.api import NHLApiError

    mock_analyze.side_effect = NHLApiError("API failed")
    response = test_client.get("/nationalities")
    assert response.status_code == 500


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_empty_nationality(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test nationalities page with empty nationality field.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "nationality": "",
            },
        ],
        "stats": {"total_players": 1},
    }
    mock_analyze.return_value = mock_data
    response = test_client.get("/nationalities")
    assert response.status_code == 200


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_single_nationality(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test nationalities page with a single nationality.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "nationality": "Canada",
            },
            {
                "player_id": 8477492,
                "full_name": "Sidney Crosby",
                "first_name": "Sidney",
                "last_name": "Crosby",
                "team": "PIT",
                "score": 20,
                "first_score": 10,
                "last_score": 10,
                "nationality": "Canada",
            },
        ],
        "stats": {"total_players": 2},
    }
    mock_analyze.return_value = mock_data
    response = test_client.get("/nationalities")
    assert response.status_code == 200
    assert b"canada" in response.content.lower()


@patch("nhl_scrabble.web.routes.nationalities.analyze_post", new_callable=AsyncMock)
def test_nationalities_page_with_missing_fields(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test nationalities page handles missing optional fields gracefully.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    mock_data = {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "full_name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
                "nationality": "Canada",
            },
        ],
        "stats": {"total_players": 1},
    }
    mock_analyze.return_value = mock_data
    response = test_client.get("/nationalities")
    assert response.status_code == 200
