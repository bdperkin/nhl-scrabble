"""Unit tests for player filtering functions."""

from __future__ import annotations

import pytest

from nhl_scrabble.filters import AnalysisFilters, filter_players
from nhl_scrabble.models.player import PlayerScore


class TestFilterPlayers:
    """Tests for filter_players function."""

    @pytest.fixture
    def sample_players(self) -> list[PlayerScore]:
        """Create sample players for testing."""
        return [
            PlayerScore(
                "John",
                "Doe",
                "John Doe",
                10,
                10,
                20,
                "TOR",
                "Atlantic",
                "Eastern",
                position_code="C",
                position="Center",
                position_type="Forward",
            ),
            PlayerScore(
                "Jane",
                "Smith",
                "Jane Smith",
                15,
                15,
                30,
                "MTL",
                "Atlantic",
                "Eastern",
                position_code="L",
                position="Left Wing",
                position_type="Forward",
            ),
            PlayerScore(
                "Bob",
                "Jones",
                "Bob Jones",
                12,
                12,
                24,
                "BOS",
                "Atlantic",
                "Eastern",
                position_code="D",
                position="Defense",
                position_type="Defense",
            ),
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
                position_code="G",
                position="Goalie",
                position_type="Goalie",
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
                position_code="R",
                position="Right Wing",
                position_type="Forward",
            ),
        ]

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

    def test_filter_players_by_position_code(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by position code."""
        filters = AnalysisFilters(positions=frozenset(["C"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 1  # John (C)
        assert result[0].position_code == "C"

    def test_filter_players_by_position_type(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by position type."""
        filters = AnalysisFilters(positions=frozenset(["Forward"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 3  # John (C), Jane (L), Charlie (R) - all Forwards
        assert all(p.position_type == "Forward" for p in result)

    def test_filter_players_by_full_position_name(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by full position name."""
        filters = AnalysisFilters(positions=frozenset(["Goalie"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 1  # Alice (Goalie)
        assert result[0].position == "Goalie"

    def test_filter_players_by_multiple_positions(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players by multiple positions."""
        filters = AnalysisFilters(positions=frozenset(["D", "G"]))
        result = filter_players(sample_players, filters)
        assert len(result) == 2  # Bob (D), Alice (G)
        assert all(p.position_code in ["D", "G"] for p in result)

    def test_filter_players_combined(self, sample_players: list[PlayerScore]) -> None:
        """Test filtering players with multiple filters."""
        filters = AnalysisFilters(
            conferences=frozenset(["Eastern"]),
            min_score=25,
        )
        result = filter_players(sample_players, filters)
        assert len(result) == 1  # Jane (30, Eastern)
        assert result[0].full_name == "Jane Smith"
