"""Tests for player detail page routes."""

from unittest.mock import MagicMock, patch

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
        Mock analysis data with player information
    """
    return {
        "timestamp": "2024-05-09T12:00:00",
        "top_players": [
            {
                "player_id": 8478402,
                "name": "Connor McDavid",
                "first_name": "Connor",
                "last_name": "McDavid",
                "team": "EDM",
                "team_name": "Edmonton Oilers",
                "division": "Pacific",
                "conference": "Western",
                "score": 24,
                "first_score": 12,
                "last_score": 12,
            },
        ],
        "stats": {
            "total_players": 1,
            "highest_score": 24,
            "lowest_score": 24,
            "avg_score": 24.0,
            "highest_player_name": "Connor McDavid",
        },
    }


@pytest.fixture
def mock_nhl_player_details() -> dict:
    """Create mock NHL API player details.

    Returns:
        Mock player details from NHL API
    """
    return {
        "playerId": 8478402,
        "firstName": {"default": "Connor"},
        "lastName": {"default": "McDavid"},
        "headshot": "https://assets.nhle.com/mugs/nhl/8478402.png",
        "birthCity": {"default": "Richmond Hill"},
        "birthStateProvince": {"default": "ON"},
        "birthCountry": "CAN",
        "position": "C",
        "sweaterNumber": 97,
    }


@patch("nhl_scrabble.web.app.analyze_post")
@patch("nhl_scrabble.web.app.NHLApiClient")
def test_player_detail_page_loads(
    mock_nhl_client: MagicMock,
    mock_analyze: MagicMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    mock_nhl_player_details: dict,
) -> None:
    """Test that player detail page loads successfully.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        mock_nhl_player_details: Mock NHL player details
    """
    # Setup mocks
    mock_analyze.return_value = mock_analysis_data

    # Mock the NHLApiClient context manager
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = mock_nhl_player_details
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Assertions
    assert response.status_code == 200
    assert b"Connor McDavid" in response.content
    assert b"player-header" in response.content


@patch("nhl_scrabble.web.app.analyze_post")
@patch("nhl_scrabble.web.app.NHLApiClient")
def test_player_detail_page_shows_photo(
    mock_nhl_client: MagicMock,
    mock_analyze: MagicMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    mock_nhl_player_details: dict,
) -> None:
    """Test that player photo is displayed.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        mock_nhl_player_details: Mock NHL player details
    """
    # Setup mocks
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = mock_nhl_player_details
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Assertions
    assert response.status_code == 200
    assert b"player-photo" in response.content
    assert b"assets.nhle.com/mugs/nhl/8478402.png" in response.content


@patch("nhl_scrabble.web.app.analyze_post")
def test_player_detail_page_invalid_player(
    mock_analyze: MagicMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test 404 for non-existent player.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    # Setup mock with no matching player
    mock_analyze.return_value = mock_analysis_data

    # Make request with invalid player ID
    response = test_client.get("/players/9999999")

    # Assertions
    assert response.status_code == 404


@patch("nhl_scrabble.web.app.analyze_post")
@patch("nhl_scrabble.web.app.NHLApiClient")
def test_player_detail_page_shows_team_logo(
    mock_nhl_client: MagicMock,
    mock_analyze: MagicMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    mock_nhl_player_details: dict,
) -> None:
    """Test that team logo is displayed.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        mock_nhl_player_details: Mock NHL player details
    """
    # Setup mocks
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = mock_nhl_player_details
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Assertions
    assert response.status_code == 200
    assert b"team-logo-small" in response.content
    assert b"assets.nhle.com/logos/nhl/svg/EDM_light.svg" in response.content


@patch("nhl_scrabble.web.app.analyze_post")
@patch("nhl_scrabble.web.app.NHLApiClient")
def test_player_detail_page_shows_country_flag(
    mock_nhl_client: MagicMock,
    mock_analyze: MagicMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    mock_nhl_player_details: dict,
) -> None:
    """Test that country flag is displayed.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
        mock_nhl_player_details: Mock NHL player details
    """
    # Setup mocks
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = mock_nhl_player_details
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Assertions
    assert response.status_code == 200
    assert b"flagcdn.com" in response.content
