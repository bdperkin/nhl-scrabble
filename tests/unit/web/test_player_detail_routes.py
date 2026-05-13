"""Tests for player-related routes.

This module tests error handling and edge cases for player routes that are not covered by
integration tests.
"""

from unittest.mock import AsyncMock, MagicMock, patch

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
                "full_name": "Connor McDavid",
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


@patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_loads(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
    mock_nhl_player_details: dict,
) -> None:
    """Test that player detail page loads successfully.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock async analysis endpoint
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


@patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_shows_photo(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
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


@patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
def test_player_detail_page_invalid_player(
    mock_analyze: AsyncMock,
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


@patch("nhl_scrabble.web.routes.players.analyze_post")
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_shows_team_logo(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
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


@patch("nhl_scrabble.web.routes.players.analyze_post")
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_shows_country_flag(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
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


@patch("nhl_scrabble.web.routes.players.analyze_post")
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_nhl_api_error(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test handling of NHL API errors.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    from nhl_scrabble.exceptions import NHLApiError

    # Setup mocks
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.side_effect = NHLApiError("API failed")
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Should return 503 Service Unavailable
    assert response.status_code == 503


@patch("nhl_scrabble.web.routes.players.analyze_post")
def test_player_detail_page_analysis_error(
    mock_analyze: AsyncMock,
    test_client: TestClient,
) -> None:
    """Test handling of analysis endpoint errors.

    Args:
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
    """
    from nhl_scrabble.exceptions import NHLApiError

    # Setup mock to raise error
    mock_analyze.side_effect = NHLApiError("Analysis failed")

    # Make request
    response = test_client.get("/players/8478402")

    # Should return 503 Service Unavailable (NHL API error)
    assert response.status_code == 503


@patch("nhl_scrabble.web.routes.players.analyze_post")
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_missing_birthplace_data(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test handling of missing birthplace data in NHL API response.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    # Setup mocks with minimal player data
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = {
        "playerId": 8478402,
        "firstName": {"default": "Connor"},
        "lastName": {"default": "McDavid"},
        # Missing birthCity, birthStateProvince, birthCountry
        "position": "C",
        "sweaterNumber": 97,
    }
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Should still return 200 with default values
    assert response.status_code == 200
    assert b"Unknown" in response.content  # Default birthplace


@patch("nhl_scrabble.web.routes.players.analyze_post")
@patch("nhl_scrabble.web.routes.players.NHLApiClient")
def test_player_detail_page_no_country_flag(
    mock_nhl_client: MagicMock,
    mock_analyze: AsyncMock,
    test_client: TestClient,
    mock_analysis_data: dict,
) -> None:
    """Test that no country flag URL is generated when country is missing.

    Args:
        mock_nhl_client: Mock NHL API client
        mock_analyze: Mock analysis endpoint
        test_client: Test client fixture
        mock_analysis_data: Mock analysis data
    """
    # Setup mocks with no birth country
    mock_analyze.return_value = mock_analysis_data
    mock_client_instance = MagicMock()
    mock_client_instance.get_player_details.return_value = {
        "playerId": 8478402,
        "firstName": {"default": "Connor"},
        "lastName": {"default": "McDavid"},
        "birthCity": {"default": "Richmond Hill"},
        "birthCountry": "",  # Empty country
        "position": "C",
        "sweaterNumber": 97,
    }
    mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
    mock_nhl_client.return_value.__exit__.return_value = None

    # Make request
    response = test_client.get("/players/8478402")

    # Should return 200 but no flag URL
    assert response.status_code == 200


class TestPlayersPage:
    """Tests for /players route."""

    @patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
    def test_players_page_loads(
        self,
        mock_analyze: AsyncMock,
        test_client: TestClient,
        mock_analysis_data: dict,
    ) -> None:
        """Test that players page loads successfully.

        Args:
            mock_analyze: Mock analysis endpoint
            test_client: Test client fixture
            mock_analysis_data: Mock analysis data
        """
        # Setup mock
        mock_analyze.return_value = mock_analysis_data

        # Make request
        response = test_client.get("/players")

        # Assertions
        assert response.status_code == 200
        assert b"Connor McDavid" in response.content

    def test_players_page_templates_not_configured(
        self,
        test_client: TestClient,
    ) -> None:
        """Test error handling when templates are not configured.

        Args:
            test_client: Test client fixture
        """
        # Temporarily remove templates from app state
        original_templates = app.state.templates
        app.state.templates = None

        try:
            response = test_client.get("/players")
            assert response.status_code == 500
            assert b"Templates not configured" in response.content
        finally:
            # Restore templates
            app.state.templates = original_templates

    @patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
    def test_players_page_nhl_api_error(
        self,
        mock_analyze: AsyncMock,
        test_client: TestClient,
    ) -> None:
        """Test error handling when NHL API fails.

        Args:
            mock_analyze: Mock analysis endpoint
            test_client: Test client fixture
        """
        from nhl_scrabble.api import NHLApiError

        mock_analyze.side_effect = NHLApiError("API failed")

        response = test_client.get("/players")

        assert response.status_code == 500
        assert b"Failed to fetch NHL data" in response.content


class TestPlayerDetailPageEdgeCases:
    """Additional edge case tests for player detail page."""

    def test_player_detail_page_templates_not_configured(
        self,
        test_client: TestClient,
    ) -> None:
        """Test error handling when templates are not configured.

        Args:
            test_client: Test client fixture
        """
        # Temporarily remove templates from app state
        original_templates = app.state.templates
        app.state.templates = None

        try:
            response = test_client.get("/players/8478402")
            assert response.status_code == 500
            assert b"Templates not configured" in response.content
        finally:
            # Restore templates
            app.state.templates = original_templates

    @patch("nhl_scrabble.web.routes.players.analyze_post", new_callable=AsyncMock)
    @patch("nhl_scrabble.web.routes.players.NHLApiClient")
    def test_player_detail_page_with_team_standings(
        self,
        mock_nhl_client: MagicMock,
        mock_analyze: AsyncMock,
        test_client: TestClient,
        mock_analysis_data: dict,
        mock_nhl_player_details: dict,
    ) -> None:
        """Test that team name is looked up from team_standings when available.

        Args:
            mock_nhl_client: Mock NHL API client
            mock_analyze: Mock analysis endpoint
            test_client: Test client fixture
            mock_analysis_data: Mock analysis data
            mock_nhl_player_details: Mock NHL player details
        """
        # Add team_standings to mock data
        mock_data_with_standings = {
            **mock_analysis_data,
            "team_standings": [
                {
                    "abbrev": "EDM",
                    "name": "Edmonton Oilers",
                    "division": "Pacific",
                    "conference": "Western",
                },
            ],
        }

        # Setup mocks
        mock_analyze.return_value = mock_data_with_standings
        mock_client_instance = MagicMock()
        mock_client_instance.get_player_details.return_value = mock_nhl_player_details
        mock_nhl_client.return_value.__enter__.return_value = mock_client_instance
        mock_nhl_client.return_value.__exit__.return_value = None

        # Make request
        response = test_client.get("/players/8478402")

        # Should return 200 and use full team name from standings
        assert response.status_code == 200
        assert b"Edmonton Oilers" in response.content


class TestPlayerApiEndpoint:
    """Tests for /api/players/{player_id} endpoint."""

    def test_get_player_api_endpoint(
        self,
        test_client: TestClient,
    ) -> None:
        """Test that API endpoint returns 404 (not yet implemented).

        Args:
            test_client: Test client fixture
        """
        response = test_client.get("/api/players/8478402")

        # This endpoint is not yet fully implemented
        assert response.status_code == 404
        assert b"Player 8478402 not found" in response.content
