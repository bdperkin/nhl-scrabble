"""Unit tests for filters module."""

from __future__ import annotations

import pytest

from nhl_scrabble.filters import (
    AnalysisFilters,
    filter_conference_standings,
    filter_division_standings,
    filter_players,
    filter_playoff_standings,
    filter_teams,
)
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore



class TestFilterFunctions:
    """Tests for filter functions."""

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

    @pytest.fixture
    def sample_players(self) -> list[PlayerScore]:
        """Create sample players for testing."""
        return [
            PlayerScore("John", "Doe", "John Doe", 10, 10, 20, "TOR", "Atlantic", "Eastern"),
            PlayerScore("Jane", "Smith", "Jane Smith", 15, 15, 30, "MTL", "Atlantic", "Eastern"),
            PlayerScore("Bob", "Jones", "Bob Jones", 12, 12, 24, "BOS", "Atlantic", "Eastern"),
            PlayerScore(
                "Alice",
                "Johnson",
                "Alice Johnson",
                20,
                30,
                50,
                "EDM",
                "Pacific",
                "Western",
            ),
            PlayerScore(
                "Charlie",
                "Brown",
                "Charlie Brown",
                25,
                35,
                60,
                "VAN",
                "Pacific",
                "Western",
            ),
        ]

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

    def test_filter_players_no_filters(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players with no filters returns all players."""
        filters = AnalysisFilters()
        result = filter_players(sample_players, filters)
        assert len(result) == len(sample_players)
        assert result == sample_players

    def test_filter_players_by_team(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by team."""
        filters = AnalysisFilters(teams=frozenset(["TOR", "MTL"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 2  # John Doe (TOR), Jane Smith (MTL)
        assert all(p.team in ["TOR", "MTL"] for p in result)

    def test_filter_players_by_division(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by division."""
        filters = AnalysisFilters(divisions=frozenset(["Pacific"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 2  # Alice Johnson (EDM), Charlie Brown (VAN)
        assert all(p.division == "Pacific" for p in result)

    def test_filter_players_by_conference(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by conference."""
        filters = AnalysisFilters(conferences=frozenset(["Eastern"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 3  # John, Jane, Bob
        assert all(p.conference == "Eastern" for p in result)

    def test_filter_players_by_excluded_teams(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering out players from excluded teams."""
        filters = AnalysisFilters(excluded_teams=frozenset(["TOR", "MTL"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 3  # Bob, Alice, Charlie
        assert all(p.team not in ["TOR", "MTL"] for p in result)

    def test_filter_players_by_min_score(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by minimum score."""
        filters = AnalysisFilters(min_score=30)
        result = filter_players(sample_players, filters)
        assert len(result) == 3  # Jane (30), Alice (50), Charlie (60)
        assert all(p.full_score >= 30 for p in result)

    def test_filter_players_by_max_score(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by maximum score."""
        filters = AnalysisFilters(max_score=30)
        result = filter_players(sample_players, filters)
        assert len(result) == 3  # John (20), Jane (30), Bob (24)
        assert all(p.full_score <= 30 for p in result)

    def test_filter_players_by_score_range(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by score range."""
        filters = AnalysisFilters(min_score=25, max_score=55)
        result = filter_players(sample_players, filters)
        assert len(result) == 2  # Jane (30), Alice (50)
        assert all(25 <= p.full_score <= 55 for p in result)

    def test_filter_players_combined(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players with multiple filters."""
        filters = AnalysisFilters(
            conferences=frozenset(["Eastern"]),
            min_score=25,
        )
        result = filter_players(sample_players, filters)
        assert len(result) == 1  # Jane (30, Eastern)
        assert result[0].full_name == "Jane Smith"

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
