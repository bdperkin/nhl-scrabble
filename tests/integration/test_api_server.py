"""Integration tests for REST API server.

Tests the complete API server functionality including all endpoints. Uses FastAPI TestClient to
simulate HTTP requests without running the server.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.api_server.app import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.

    Returns:
        TestClient: FastAPI test client instance.
    """
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nhl-scrabble-api"
        assert data["version"] == "1.0.0"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "NHL Scrabble API"
        assert data["version"] == "1.0.0"
        assert data["docs_url"] == "/docs"


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation endpoints."""

    def test_docs_endpoint(self, client: TestClient) -> None:
        """Test Swagger UI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, client: TestClient) -> None:
        """Test ReDoc docs are accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json(self, client: TestClient) -> None:
        """Test OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "NHL Scrabble API"
        assert data["info"]["version"] == "1.0.0"


class TestTeamsEndpoints:
    """Tests for teams endpoints."""

    def test_get_all_teams(self, client: TestClient) -> None:
        """Test getting all teams."""
        response = client.get("/api/v1/teams")

        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert "count" in data
        assert isinstance(data["teams"], list)
        assert data["count"] > 0

    def test_get_teams_by_division(self, client: TestClient) -> None:
        """Test filtering teams by division."""
        response = client.get("/api/v1/teams?division=Atlantic")

        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert data["filters"]["division"] == "Atlantic"

        # Verify all teams are from Atlantic division
        for team in data["teams"]:
            assert team["division"] == "Atlantic"

    def test_get_teams_by_conference(self, client: TestClient) -> None:
        """Test filtering teams by conference."""
        response = client.get("/api/v1/teams?conference=Eastern")

        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert data["filters"]["conference"] == "Eastern"

        # Verify all teams are from Eastern conference
        for team in data["teams"]:
            assert team["conference"] == "Eastern"

    def test_get_specific_team(self, client: TestClient) -> None:
        """Test getting a specific team by abbreviation."""
        # First get all teams to find a valid abbreviation
        response = client.get("/api/v1/teams")
        assert response.status_code == 200
        teams = response.json()["teams"]
        assert len(teams) > 0

        # Get first team's abbreviation
        team_abbrev = teams[0]["abbrev"]

        # Get specific team
        response = client.get(f"/api/v1/teams/{team_abbrev}")
        assert response.status_code == 200
        data = response.json()
        assert data["abbrev"] == team_abbrev
        assert "name" in data
        assert "total_score" in data
        assert "players" in data

    def test_get_nonexistent_team(self, client: TestClient) -> None:
        """Test getting a team that doesn't exist."""
        response = client.get("/api/v1/teams/XXX")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestPlayersEndpoints:
    """Tests for players endpoints."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_all_players(self, client: TestClient) -> None:
        """Test getting all players."""
        response = client.get("/api/v1/players")

        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert "count" in data
        assert isinstance(data["players"], list)
        assert data["count"] > 0

    def test_get_players_with_min_score(self, client: TestClient) -> None:
        """Test filtering players by minimum score."""
        min_score = 100
        response = client.get(f"/api/v1/players?min_score={min_score}")

        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert data["filters"]["min_score"] == min_score

        # Verify all players meet minimum score
        for player in data["players"]:
            assert player["score"] >= min_score

    def test_get_players_with_max_score(self, client: TestClient) -> None:
        """Test filtering players by maximum score."""
        max_score = 50
        response = client.get(f"/api/v1/players?max_score={max_score}")

        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert data["filters"]["max_score"] == max_score

        # Verify all players are below maximum score
        for player in data["players"]:
            assert player["score"] <= max_score

    def test_get_players_with_limit(self, client: TestClient) -> None:
        """Test limiting number of players returned."""
        limit = 10
        response = client.get(f"/api/v1/players?limit={limit}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) <= limit

    def test_get_players_sorted_by_score(self, client: TestClient) -> None:
        """Test sorting players by score."""
        response = client.get("/api/v1/players?sort_by=score&order=desc&limit=10")

        assert response.status_code == 200
        data = response.json()
        players = data["players"]

        # Verify descending order
        for i in range(len(players) - 1):
            assert players[i]["score"] >= players[i + 1]["score"]

    def test_get_players_sorted_by_name(self, client: TestClient) -> None:
        """Test sorting players by name."""
        response = client.get("/api/v1/players?sort_by=name&order=asc&limit=10")

        assert response.status_code == 200
        data = response.json()
        players = data["players"]

        # Verify ascending alphabetical order
        for i in range(len(players) - 1):
            name1 = (players[i]["last_name"], players[i]["first_name"])
            name2 = (players[i + 1]["last_name"], players[i + 1]["first_name"])
            assert name1 <= name2

    def test_get_players_by_team(self, client: TestClient) -> None:
        """Test filtering players by team."""
        # First get all teams to find a valid abbreviation
        response = client.get("/api/v1/teams")
        assert response.status_code == 200
        teams = response.json()["teams"]
        assert len(teams) > 0
        team_abbrev = teams[0]["abbrev"]

        # Get players for that team
        response = client.get(f"/api/v1/players?team={team_abbrev}")

        assert response.status_code == 200
        data = response.json()
        assert "players" in data

        # Verify all players are from the specified team
        for player in data["players"]:
            assert player["team"] == team_abbrev


class TestStandingsEndpoints:
    """Tests for standings endpoints."""

    def test_get_division_standings(self, client: TestClient) -> None:
        """Test getting division standings."""
        response = client.get("/api/v1/standings/division")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "division"
        assert "divisions" in data
        assert isinstance(data["divisions"], list)
        assert len(data["divisions"]) > 0

        # Verify structure
        for division in data["divisions"]:
            assert "division" in division
            assert "teams" in division
            assert isinstance(division["teams"], list)

    def test_get_conference_standings(self, client: TestClient) -> None:
        """Test getting conference standings."""
        response = client.get("/api/v1/standings/conference")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "conference"
        assert "conferences" in data
        assert isinstance(data["conferences"], list)
        assert len(data["conferences"]) > 0

        # Verify structure
        for conference in data["conferences"]:
            assert "conference" in conference
            assert "teams" in conference
            assert isinstance(conference["teams"], list)

    def test_get_playoff_standings(self, client: TestClient) -> None:
        """Test getting playoff standings."""
        response = client.get("/api/v1/standings/playoffs")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "playoffs"
        assert "eastern_conference" in data
        assert "western_conference" in data
        assert isinstance(data["eastern_conference"], list)
        assert isinstance(data["western_conference"], list)

    def test_get_invalid_standings_type(self, client: TestClient) -> None:
        """Test getting standings with invalid type."""
        response = client.get("/api/v1/standings/invalid")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid standings type" in data["detail"]


class TestCORSHeaders:
    """Tests for CORS middleware."""

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test that CORS headers are present in responses."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_nonexistent_endpoint(self, client: TestClient) -> None:
        """Test 404 error for non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    def test_405_for_wrong_http_method(self, client: TestClient) -> None:
        """Test 405 error for unsupported HTTP methods."""
        response = client.post("/health")

        assert response.status_code == 405
