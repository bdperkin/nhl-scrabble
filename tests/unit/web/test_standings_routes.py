"""Tests for standings-related routes (league, playoffs, stats).

This module tests error handling and edge cases for league, playoffs, and stats routes that are not
covered by integration tests.
"""

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
        Mock analysis data with standings, playoff bracket, and stats
    """
    return {
        "timestamp": "2024-05-09T12:00:00",
        "team_standings": [
            {
                "abbrev": "TOR",
                "name": "Toronto Maple Leafs",
                "division": "Atlantic",
                "conference": "Eastern",
                "total_score": 5000,
                "avg_score": 50.0,
                "player_count": 100,
                "top_players": [],
            },
        ],
        "playoff_bracket": {
            "Eastern": [
                {
                    "abbrev": "TOR",
                    "name": "Toronto Maple Leafs",
                    "in_playoffs": True,
                },
            ],
            "Western": [
                {
                    "abbrev": "EDM",
                    "name": "Edmonton Oilers",
                    "in_playoffs": True,
                },
            ],
        },
        "top_players": [
            {
                "player_id": 8478402,
                "first_name": "Connor",
                "last_name": "McDavid",
                "full_name": "Connor McDavid",
                "score": 24,
            },
        ],
        "stats": {
            "total_teams": 32,
            "total_players": 800,
            "total_score": 50000,
        },
    }


class TestLeaguePage:
    """Tests for /league route."""

    def test_league_page_templates_not_configured(self, test_client: TestClient) -> None:
        """Test error handling when templates are not configured.

        Args:
            test_client: Test client fixture
        """
        # Temporarily remove templates from app state
        original_templates = app.state.templates
        app.state.templates = None

        try:
            response = test_client.get("/league")
            assert response.status_code == 500
            assert b"Templates not configured" in response.content
        finally:
            # Restore templates
            app.state.templates = original_templates

    @patch("nhl_scrabble.web.routes.standings.analyze_post", new_callable=AsyncMock)
    def test_league_page_nhl_api_error(
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

        response = test_client.get("/league")

        assert response.status_code == 500
        assert b"Failed to fetch NHL data" in response.content

    # Note: Success paths are tested in integration tests
    # These unit tests focus on error handling paths


class TestPlayoffsPage:
    """Tests for /playoffs route."""

    def test_playoffs_page_templates_not_configured(
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
            response = test_client.get("/playoffs")
            assert response.status_code == 500
            assert b"Templates not configured" in response.content
        finally:
            # Restore templates
            app.state.templates = original_templates

    @patch("nhl_scrabble.web.routes.standings.analyze_post", new_callable=AsyncMock)
    def test_playoffs_page_nhl_api_error(
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

        response = test_client.get("/playoffs")

        assert response.status_code == 500
        assert b"Failed to fetch NHL data" in response.content

    # Note: Success paths and playoff team counting logic are tested in integration tests
    # These unit tests focus on error handling paths


class TestStatsPage:
    """Tests for /stats route."""

    def test_stats_page_templates_not_configured(
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
            response = test_client.get("/stats")
            assert response.status_code == 500
            assert b"Templates not configured" in response.content
        finally:
            # Restore templates
            app.state.templates = original_templates

    @patch("nhl_scrabble.web.routes.standings.analyze_post", new_callable=AsyncMock)
    def test_stats_page_nhl_api_error(
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

        response = test_client.get("/stats")

        assert response.status_code == 500
        assert b"Failed to fetch NHL data" in response.content

    # Note: Success paths are tested in integration tests
    # These unit tests focus on error handling paths
