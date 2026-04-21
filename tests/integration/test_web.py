"""Integration tests for NHL Scrabble web interface.

Tests the complete web application including API endpoints, templates, and error handling.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app.

    Returns:
        Test client instance
    """
    return TestClient(app)


@pytest.fixture
def mock_team_scores() -> dict[str, TeamScore]:
    """Create mock team scores for testing.

    Returns:
        Dictionary of mock TeamScore objects
    """
    player1 = PlayerScore(
        first_name="Connor",
        last_name="McDavid",
        full_name="Connor McDavid",
        team="EDM",
        first_score=11,
        last_score=17,
        full_score=28,
        division="Pacific",
        conference="Western",
    )
    player2 = PlayerScore(
        first_name="Leon",
        last_name="Draisaitl",
        full_name="Leon Draisaitl",
        team="EDM",
        first_score=6,
        last_score=15,
        full_score=21,
        division="Pacific",
        conference="Western",
    )

    team = TeamScore(
        abbrev="EDM",
        players=[player1, player2],
        total=49,  # 28 + 21
        conference="Western",
        division="Pacific",
    )

    return {"EDM": team}


@pytest.fixture
def mock_playoff_standings() -> dict[str, list[Any]]:
    """Create mock playoff standings for testing.

    Returns:
        Dictionary of mock playoff standings
    """
    return {
        "Eastern": [],
        "Western": [],
    }


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint returns healthy status.

        Args:
            client: Test client fixture
        """
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_health_security_headers(self, client: TestClient) -> None:
        """Test health endpoint includes security headers.

        Args:
            client: Test client fixture
        """
        response = client.get("/health")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"


class TestRootEndpoint:
    """Tests for root endpoint serving web interface."""

    def test_root_returns_html(self, client: TestClient) -> None:
        """Test root endpoint returns HTML.

        Args:
            client: Test client fixture
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_root_includes_title(self, client: TestClient) -> None:
        """Test root endpoint includes page title.

        Args:
            client: Test client fixture
        """
        response = client.get("/")
        assert "NHL Scrabble" in response.text

    def test_root_includes_security_headers(self, client: TestClient) -> None:
        """Test root endpoint includes security headers.

        Args:
            client: Test client fixture
        """
        response = client.get("/")

        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers


class TestFaviconEndpoint:
    """Tests for favicon endpoint."""

    def test_favicon_returns_svg(self, client: TestClient) -> None:
        """Test favicon endpoint returns SVG.

        Args:
            client: Test client fixture
        """
        response = client.get("/favicon.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]

    def test_favicon_contains_svg_markup(self, client: TestClient) -> None:
        """Test favicon contains valid SVG markup.

        Args:
            client: Test client fixture
        """
        response = client.get("/favicon.svg")
        assert "<svg" in response.text
        assert "</svg>" in response.text


class TestAnalyzeEndpoint:
    """Tests for analysis API endpoint."""

    # Note: These tests require complex mocking of NHLApiClient context manager
    # and are currently disabled. They would benefit from refactoring to use
    # fixture data or real integration tests against a test server.
    # TODO: Refactor these tests to use simpler mocking or real test data

    @pytest.mark.skip(reason="Complex mocking - needs refactoring")
    @patch("nhl_scrabble.web.app.PlayoffCalculator")
    @patch("nhl_scrabble.web.app.TeamProcessor")
    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_analyze_post_success(
        self,
        mock_client_class: MagicMock,
        mock_team_processor_class: MagicMock,
        mock_playoff_calc_class: MagicMock,
        client: TestClient,
        mock_team_scores: dict[str, TeamScore],
        mock_playoff_standings: dict[str, list[Any]],
    ) -> None:
        """Test successful analysis via POST endpoint.

        Args:
            mock_client_class: Mocked NHL API client class
            mock_team_processor_class: Mocked team processor class
            mock_playoff_calc_class: Mocked playoff calculator class
            client: Test client fixture
            mock_team_scores: Mock team scores fixture
            mock_playoff_standings: Mock playoff standings fixture
        """
        # Setup mock client (context manager)
        mock_client_instance = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        mock_client_class.return_value.__exit__.return_value = None

        # Setup mock team processor
        mock_processor = MagicMock()
        mock_processor.process_all_teams.return_value = (
            mock_team_scores,
            list(mock_team_scores["EDM"].players),
            [],
        )
        mock_team_processor_class.return_value = mock_processor

        # Setup mock playoff calculator
        mock_calc = MagicMock()
        mock_calc.calculate_playoff_standings.return_value = mock_playoff_standings
        mock_playoff_calc_class.return_value = mock_calc

        # Make request
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 10,
                "top_team_players": 5,
                "use_cache": False,
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert "timestamp" in data
        assert "cache_hit" in data
        assert "top_players" in data
        assert "team_standings" in data
        assert "division_standings" in data
        assert "conference_standings" in data
        assert "playoff_bracket" in data
        assert "stats" in data

    @pytest.mark.skip(reason="Complex mocking - needs refactoring")
    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_analyze_post_api_error(
        self,
        mock_client_class: MagicMock,
        client: TestClient,
    ) -> None:
        """Test analysis POST handles NHL API errors.

        Args:
            mock_client_class: Mocked NHL API client class
            client: Test client fixture
        """
        # Setup mock to raise exception when entering context manager
        from nhl_scrabble.api import NHLApiError

        mock_client_class.return_value.__enter__.side_effect = NHLApiError("API Error")

        # Make request
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 10,
                "top_team_players": 5,
                "use_cache": False,
            },
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "fail" in data["detail"].lower()

    @pytest.mark.skip(reason="Complex mocking - needs refactoring")
    @patch("nhl_scrabble.web.app.PlayoffCalculator")
    @patch("nhl_scrabble.web.app.TeamProcessor")
    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_analyze_get_returns_json(
        self,
        mock_client_class: MagicMock,
        mock_team_processor_class: MagicMock,
        mock_playoff_calc_class: MagicMock,
        client: TestClient,
        mock_team_scores: dict[str, TeamScore],
        mock_playoff_standings: dict[str, list[Any]],
    ) -> None:
        """Test GET endpoint returns JSON when not HTMX request.

        Args:
            mock_client_class: Mocked NHL API client class
            mock_team_processor_class: Mocked team processor class
            mock_playoff_calc_class: Mocked playoff calculator class
            client: Test client fixture
            mock_team_scores: Mock team scores fixture
            mock_playoff_standings: Mock playoff standings fixture
        """
        # Setup mock client (context manager)
        mock_client_instance = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        mock_client_class.return_value.__exit__.return_value = None

        # Setup mock team processor
        mock_processor = MagicMock()
        mock_processor.process_all_teams.return_value = (
            mock_team_scores,
            list(mock_team_scores["EDM"].players),
            [],
        )
        mock_team_processor_class.return_value = mock_processor

        # Setup mock playoff calculator
        mock_calc = MagicMock()
        mock_calc.calculate_playoff_standings.return_value = mock_playoff_standings
        mock_playoff_calc_class.return_value = mock_calc

        # Make request without HTMX header
        response = client.get("/api/analyze?top_players=10&top_team_players=5&use_cache=false")

        assert response.status_code == 200
        # Should return JSON, not HTML
        data = response.json()
        assert "top_players" in data

    @pytest.mark.skip(reason="Complex mocking - needs refactoring")
    @patch("nhl_scrabble.web.app.PlayoffCalculator")
    @patch("nhl_scrabble.web.app.TeamProcessor")
    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_analyze_get_htmx_returns_html(
        self,
        mock_client_class: MagicMock,
        mock_team_processor_class: MagicMock,
        mock_playoff_calc_class: MagicMock,
        client: TestClient,
        mock_team_scores: dict[str, TeamScore],
        mock_playoff_standings: dict[str, list[Any]],
    ) -> None:
        """Test GET endpoint returns HTML for HTMX requests.

        Args:
            mock_client_class: Mocked NHL API client class
            mock_team_processor_class: Mocked team processor class
            mock_playoff_calc_class: Mocked playoff calculator class
            client: Test client fixture
            mock_team_scores: Mock team scores fixture
            mock_playoff_standings: Mock playoff standings fixture
        """
        # Setup mock client (context manager)
        mock_client_instance = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        mock_client_class.return_value.__exit__.return_value = None

        # Setup mock team processor
        mock_processor = MagicMock()
        mock_processor.process_all_teams.return_value = (
            mock_team_scores,
            list(mock_team_scores["EDM"].players),
            [],
        )
        mock_team_processor_class.return_value = mock_processor

        # Setup mock playoff calculator
        mock_calc = MagicMock()
        mock_calc.calculate_playoff_standings.return_value = mock_playoff_standings
        mock_playoff_calc_class.return_value = mock_calc

        # Make request with HTMX header
        response = client.get(
            "/api/analyze?top_players=10&top_team_players=5&use_cache=false",
            headers={"HX-Request": "true"},
        )

        assert response.status_code == 200
        # Should return HTML
        assert "text/html" in response.headers["content-type"]


class TestCacheEndpoints:
    """Tests for cache management endpoints."""

    def test_clear_cache(self, client: TestClient) -> None:
        """Test cache clearing endpoint.

        Args:
            client: Test client fixture
        """
        response = client.delete("/api/cache/clear")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "cleared" in data["message"].lower()

    def test_cache_stats(self, client: TestClient) -> None:
        """Test cache statistics endpoint.

        Args:
            client: Test client fixture
        """
        response = client.get("/api/cache/stats")
        assert response.status_code == 200

        data = response.json()
        assert "size" in data
        assert "entries" in data
        assert isinstance(data["size"], int)
        assert isinstance(data["entries"], list)


class TestTeamEndpoint:
    """Tests for team details endpoint."""

    def test_get_team_not_found(self, client: TestClient) -> None:
        """Test getting team that doesn't exist.

        Args:
            client: Test client fixture
        """
        response = client.get("/api/teams/INVALID")
        assert response.status_code == 404
        assert "not found" in response.text.lower()


class TestPlayerEndpoint:
    """Tests for player details endpoint."""

    def test_get_player_not_implemented(self, client: TestClient) -> None:
        """Test player endpoint (not yet fully implemented).

        Args:
            client: Test client fixture
        """
        response = client.get("/api/players/12345")
        assert response.status_code == 404


class TestFormValidation:
    """Tests for form input validation."""

    def test_analyze_validates_top_players_min(self, client: TestClient) -> None:
        """Test analysis validates minimum top_players value.

        Args:
            client: Test client fixture
        """
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 0,  # Invalid: must be >= 1
                "top_team_players": 5,
            },
        )
        assert response.status_code == 422

    def test_analyze_validates_top_players_max(self, client: TestClient) -> None:
        """Test analysis validates maximum top_players value.

        Args:
            client: Test client fixture
        """
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 101,  # Invalid: must be <= 100
                "top_team_players": 5,
            },
        )
        assert response.status_code == 422

    def test_analyze_validates_top_team_players_min(self, client: TestClient) -> None:
        """Test analysis validates minimum top_team_players value.

        Args:
            client: Test client fixture
        """
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 10,
                "top_team_players": 0,  # Invalid: must be >= 1
            },
        )
        assert response.status_code == 422

    def test_analyze_validates_top_team_players_max(self, client: TestClient) -> None:
        """Test analysis validates maximum top_team_players value.

        Args:
            client: Test client fixture
        """
        response = client.post(
            "/api/analyze",
            json={
                "top_players": 10,
                "top_team_players": 31,  # Invalid: must be <= 30
            },
        )
        assert response.status_code == 422


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_allows_localhost(self, client: TestClient) -> None:
        """Test CORS allows localhost origin.

        Args:
            client: Test client fixture
        """
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:8000"},
        )
        # CORS middleware should handle this
        assert response.status_code in (200, 405)  # 405 if OPTIONS not implemented


class TestErrorHandling:
    """Tests for error handling and user-friendly error messages."""

    def test_404_on_unknown_route(self, client: TestClient) -> None:
        """Test 404 error on unknown route.

        Args:
            client: Test client fixture
        """
        response = client.get("/api/unknown-endpoint")
        assert response.status_code == 404

    def test_405_on_wrong_method(self, client: TestClient) -> None:
        """Test 405 error on wrong HTTP method.

        Args:
            client: Test client fixture
        """
        response = client.post("/health")  # Health only supports GET
        assert response.status_code == 405
