"""Unit tests for team filtering functions."""

from __future__ import annotations

import pytest

from nhl_scrabble.filters import AnalysisFilters, filter_teams
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


class TestFilterTeams:
    """Tests for filter_teams function."""

    @pytest.fixture
    def sample_teams(self) -> dict[str, TeamScore]:
        """Create sample teams for testing."""
        player1 = PlayerScore("John", "Doe", "John Doe", 10, 10, 20, "TOR", "Atlantic", "Eastern")
        player2 = PlayerScore(
            "Jane",
            "Smith",
            "Jane Smith",
            15,
            15,
            30,
            "MTL",
            "Atlantic",
            "Eastern",
        )
        player3 = PlayerScore("Bob", "Jones", "Bob Jones", 12, 12, 24, "EDM", "Pacific", "Western")

        return {
            "TOR": TeamScore(
                "TOR",
                "Toronto Maple Leafs",
                500,
                [player1] * 25,
                "Atlantic",
                "Eastern",
            ),
            "MTL": TeamScore(
                "MTL",
                "Montreal Canadiens",
                450,
                [player2] * 25,
                "Atlantic",
                "Eastern",
            ),
            "BOS": TeamScore("BOS", "Boston Bruins", 400, [player1] * 25, "Atlantic", "Eastern"),
            "EDM": TeamScore("EDM", "Edmonton Oilers", 520, [player3] * 25, "Pacific", "Western"),
            "VAN": TeamScore("VAN", "Vancouver Canucks", 480, [player3] * 25, "Pacific", "Western"),
        }

    def test_filter_teams_no_filters(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering teams with no filters returns all teams."""
        filters = AnalysisFilters()
        result = filter_teams(sample_teams, filters)
        assert len(result) == len(sample_teams)
        assert result == sample_teams

    def test_filter_teams_by_division(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering teams by division."""
        filters = AnalysisFilters(divisions=frozenset(["Atlantic"]))
        result = filter_teams(sample_teams, filters)
        assert len(result) == 3  # TOR, MTL, BOS
        assert all(team.division == "Atlantic" for team in result.values())

    def test_filter_teams_by_conference(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering teams by conference."""
        filters = AnalysisFilters(conferences=frozenset(["Western"]))
        result = filter_teams(sample_teams, filters)
        assert len(result) == 2  # EDM, VAN
        assert all(team.conference == "Western" for team in result.values())

    def test_filter_teams_by_team_list(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering teams by specific team list."""
        filters = AnalysisFilters(teams=frozenset(["TOR", "MTL"]))
        result = filter_teams(sample_teams, filters)
        assert len(result) == 2
        assert "TOR" in result
        assert "MTL" in result

    def test_filter_teams_by_exclusion(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test excluding specific teams."""
        filters = AnalysisFilters(excluded_teams=frozenset(["TOR", "MTL"]))
        result = filter_teams(sample_teams, filters)
        assert len(result) == 3  # BOS, EDM, VAN
        assert "TOR" not in result
        assert "MTL" not in result
