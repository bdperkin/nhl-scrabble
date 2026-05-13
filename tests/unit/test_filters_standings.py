"""Unit tests for standings filtering functions."""

from __future__ import annotations

import pytest

from nhl_scrabble.filters import (
    AnalysisFilters,
    filter_conference_standings,
    filter_division_standings,
    filter_playoff_standings,
)
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore


class TestFilterDivisionStandings:
    """Tests for filter_division_standings function."""

    def test_filter_division_standings_no_filters(self) -> None:
        """Test filtering division standings with no filters."""
        standings = {
            "Atlantic": DivisionStandings(
                name="Atlantic",
                total=1000,
                teams=[],
                player_count=25,
                avg_per_team=200.0,
            ),
            "Pacific": DivisionStandings(
                name="Pacific",
                total=900,
                teams=[],
                player_count=25,
                avg_per_team=180.0,
            ),
        }
        filters = AnalysisFilters()
        result = filter_division_standings(standings, filters)
        assert len(result) == 2
        assert result == standings

    def test_filter_division_standings_by_division(self) -> None:
        """Test filtering division standings by division."""
        standings = {
            "Atlantic": DivisionStandings(
                name="Atlantic",
                total=1000,
                teams=[],
                player_count=25,
                avg_per_team=200.0,
            ),
            "Pacific": DivisionStandings(
                name="Pacific",
                total=900,
                teams=[],
                player_count=25,
                avg_per_team=180.0,
            ),
        }
        filters = AnalysisFilters(divisions=frozenset(["Atlantic"]))
        result = filter_division_standings(standings, filters)
        assert len(result) == 1
        assert "Atlantic" in result
        assert "Pacific" not in result


class TestFilterConferenceStandings:
    """Tests for filter_conference_standings function."""

    def test_filter_conference_standings_no_filters(self) -> None:
        """Test filtering conference standings with no filters."""
        standings = {
            "Eastern": {"teams": [], "total": 1000},
            "Western": {"teams": [], "total": 900},
        }
        filters = AnalysisFilters()
        result = filter_conference_standings(standings, filters)
        assert len(result) == 2
        assert result == standings

    def test_filter_conference_standings_by_conference(self) -> None:
        """Test filtering conference standings by conference."""
        standings = {
            "Eastern": {"teams": [], "total": 1000},
            "Western": {"teams": [], "total": 900},
        }
        filters = AnalysisFilters(conferences=frozenset(["Eastern"]))
        result = filter_conference_standings(standings, filters)
        assert len(result) == 1
        assert "Eastern" in result
        assert "Western" not in result


class TestFilterPlayoffStandings:
    """Tests for filter_playoff_standings function."""

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

    def test_filter_playoff_standings_no_filters(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering playoff standings with no filters."""
        playoff_standings = {
            "Eastern": [
                PlayoffTeam(
                    "TOR",
                    500,
                    25,
                    20.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "MTL",
                    450,
                    25,
                    18.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
                PlayoffTeam(
                    "BOS",
                    400,
                    25,
                    16.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #3",
                    in_playoffs=True,
                    division_rank=3,
                    status_indicator="x",
                ),
            ],
            "Western": [
                PlayoffTeam(
                    "EDM",
                    520,
                    25,
                    20.8,
                    "Western",
                    "Pacific",
                    "Pacific #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "VAN",
                    480,
                    25,
                    19.2,
                    "Western",
                    "Pacific",
                    "Pacific #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
            ],
        }
        filters = AnalysisFilters()
        result = filter_playoff_standings(playoff_standings, filters)
        assert len(result) == 2
        assert len(result["Eastern"]) == 3
        assert len(result["Western"]) == 2

    def test_filter_playoff_standings_by_conference(
        self,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test filtering playoff standings by conference."""
        playoff_standings = {
            "Eastern": [
                PlayoffTeam(
                    "TOR",
                    500,
                    25,
                    20.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "MTL",
                    450,
                    25,
                    18.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
                PlayoffTeam(
                    "BOS",
                    400,
                    25,
                    16.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #3",
                    in_playoffs=True,
                    division_rank=3,
                    status_indicator="x",
                ),
            ],
            "Western": [
                PlayoffTeam(
                    "EDM",
                    520,
                    25,
                    20.8,
                    "Western",
                    "Pacific",
                    "Pacific #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "VAN",
                    480,
                    25,
                    19.2,
                    "Western",
                    "Pacific",
                    "Pacific #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
            ],
        }
        filters = AnalysisFilters(conferences=frozenset(["Eastern"]))
        result = filter_playoff_standings(playoff_standings, filters)
        assert len(result) == 1
        assert "Eastern" in result
        assert "Western" not in result

    def test_filter_playoff_standings_by_teams(self, sample_teams: dict[str, TeamScore]) -> None:
        """Test filtering playoff standings by specific teams."""
        playoff_standings = {
            "Eastern": [
                PlayoffTeam(
                    "TOR",
                    500,
                    25,
                    20.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "MTL",
                    450,
                    25,
                    18.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
                PlayoffTeam(
                    "BOS",
                    400,
                    25,
                    16.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #3",
                    in_playoffs=True,
                    division_rank=3,
                    status_indicator="x",
                ),
            ],
            "Western": [
                PlayoffTeam(
                    "EDM",
                    520,
                    25,
                    20.8,
                    "Western",
                    "Pacific",
                    "Pacific #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "VAN",
                    480,
                    25,
                    19.2,
                    "Western",
                    "Pacific",
                    "Pacific #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
            ],
        }
        filters = AnalysisFilters(teams=frozenset(["TOR", "EDM"]))
        result = filter_playoff_standings(playoff_standings, filters)
        assert len(result) == 2  # Both conferences have matching teams
        assert len(result["Eastern"]) == 1  # Only TOR
        assert len(result["Western"]) == 1  # Only EDM

    def test_filter_playoff_standings_removes_empty_conferences(
        self,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that conferences with no teams after filtering are removed."""
        playoff_standings = {
            "Eastern": [
                PlayoffTeam(
                    "TOR",
                    500,
                    25,
                    20.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "MTL",
                    450,
                    25,
                    18.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
                PlayoffTeam(
                    "BOS",
                    400,
                    25,
                    16.0,
                    "Eastern",
                    "Atlantic",
                    "Atlantic #3",
                    in_playoffs=True,
                    division_rank=3,
                    status_indicator="x",
                ),
            ],
            "Western": [
                PlayoffTeam(
                    "EDM",
                    520,
                    25,
                    20.8,
                    "Western",
                    "Pacific",
                    "Pacific #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    "VAN",
                    480,
                    25,
                    19.2,
                    "Western",
                    "Pacific",
                    "Pacific #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
            ],
        }
        filters = AnalysisFilters(teams=frozenset(["TOR"]))
        result = filter_playoff_standings(playoff_standings, filters)
        assert len(result) == 1  # Only Eastern remains
        assert "Eastern" in result
        assert "Western" not in result  # Removed because no teams matched
