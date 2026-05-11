"""Unit tests for player grouping utilities."""

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.processors.grouping import (
    calculate_group_statistics,
    group_by_birth_country,
    group_by_conference,
    group_by_division,
    group_by_nationality,
    group_by_position,
    group_by_position_code,
    group_by_position_type,
    group_by_team,
)


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Create sample players for testing."""
    return [
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            birthplace="Richmond Hill, ON",
            birth_country="CAN",
            nationality="Canada",
            position_code="C",
            position="Center",
            position_type="Forward",
        ),
        PlayerScore(
            first_name="Leon",
            last_name="Draisaitl",
            full_name="Leon Draisaitl",
            first_score=18,
            last_score=24,
            full_score=42,
            team="EDM",
            division="Pacific",
            conference="Western",
            birthplace="Cologne",
            birth_country="DEU",
            nationality="Germany",
            position_code="L",
            position="Left Wing",
            position_type="Forward",
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            first_score=18,
            last_score=22,
            full_score=40,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
            birthplace="San Ramon, CA",
            birth_country="USA",
            nationality="United States",
            position_code="C",
            position="Center",
            position_type="Forward",
        ),
        PlayerScore(
            first_name="William",
            last_name="Nylander",
            full_name="William Nylander",
            first_score=21,
            last_score=23,
            full_score=44,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
            birthplace="Calgary, AB",
            birth_country="CAN",
            nationality="Canada",
            position_code="R",
            position="Right Wing",
            position_type="Forward",
        ),
    ]


class TestGroupByNationality:
    """Test grouping players by nationality."""

    def test_group_by_nationality(self, sample_players: list[PlayerScore]) -> None:
        """Test grouping players by nationality."""
        grouped = group_by_nationality(sample_players)

        assert "Canada" in grouped
        assert "Germany" in grouped
        assert "United States" in grouped

        assert len(grouped["Canada"]) == 2
        assert len(grouped["Germany"]) == 1
        assert len(grouped["United States"]) == 1

    def test_group_by_nationality_player_names(self, sample_players: list[PlayerScore]) -> None:
        """Test that grouped players are correct."""
        grouped = group_by_nationality(sample_players)

        canadian_names = {p.full_name for p in grouped["Canada"]}
        assert "Connor McDavid" in canadian_names
        assert "William Nylander" in canadian_names

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_nationality([])
        assert grouped == {}

    def test_group_unknown_nationality(self) -> None:
        """Test grouping players with unknown nationality."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=10,
            full_score=20,
            team="TST",
            division="Test",
            conference="Test",
            nationality="",  # Unknown
        )

        grouped = group_by_nationality([player])
        assert "Unknown" in grouped
        assert len(grouped["Unknown"]) == 1


class TestGroupByBirthCountry:
    """Test grouping players by birth country code."""

    def test_group_by_birth_country(self, sample_players: list[PlayerScore]) -> None:
        """Test grouping players by country code."""
        grouped = group_by_birth_country(sample_players)

        assert "CAN" in grouped
        assert "DEU" in grouped
        assert "USA" in grouped

        assert len(grouped["CAN"]) == 2
        assert len(grouped["DEU"]) == 1
        assert len(grouped["USA"]) == 1

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_birth_country([])
        assert grouped == {}


class TestGroupByTeam:
    """Test grouping players by team."""

    def test_group_by_team(self, sample_players: list[PlayerScore]) -> None:
        """Test grouping players by team."""
        grouped = group_by_team(sample_players)

        assert "EDM" in grouped
        assert "TOR" in grouped

        assert len(grouped["EDM"]) == 2
        assert len(grouped["TOR"]) == 2

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_team([])
        assert grouped == {}


class TestGroupByDivision:
    """Test grouping players by division."""

    def test_group_by_division(self, sample_players: list[PlayerScore]) -> None:
        """Test grouping players by division."""
        grouped = group_by_division(sample_players)

        assert "Pacific" in grouped
        assert "Atlantic" in grouped

        assert len(grouped["Pacific"]) == 2
        assert len(grouped["Atlantic"]) == 2

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_division([])
        assert grouped == {}


class TestGroupByConference:
    """Test grouping players by conference."""

    def test_group_by_conference(self, sample_players: list[PlayerScore]) -> None:
        """Test grouping players by conference."""
        grouped = group_by_conference(sample_players)

        assert "Western" in grouped
        assert "Eastern" in grouped

        assert len(grouped["Western"]) == 2
        assert len(grouped["Eastern"]) == 2

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_conference([])
        assert grouped == {}


class TestCalculateGroupStatistics:
    """Test calculating group statistics."""

    def test_calculate_statistics(self, sample_players: list[PlayerScore]) -> None:
        """Test calculating statistics for a group."""
        stats = calculate_group_statistics(sample_players)

        assert stats["player_count"] == 4
        assert stats["total_score"] == 161  # 35 + 42 + 40 + 44
        assert stats["average_score"] == 40.25
        assert stats["min_score"] == 35
        assert stats["max_score"] == 44
        assert stats["top_player"]["full_name"] == "William Nylander"

    def test_calculate_statistics_empty_list(self) -> None:
        """Test calculating statistics for empty list."""
        stats = calculate_group_statistics([])

        assert stats["player_count"] == 0
        assert stats["total_score"] == 0
        assert stats["average_score"] == 0.0
        assert stats["min_score"] == 0
        assert stats["max_score"] == 0
        assert stats["top_player"] is None

    def test_calculate_statistics_single_player(self) -> None:
        """Test calculating statistics for single player."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=15,
            full_score=25,
            team="TST",
            division="Test",
            conference="Test",
        )

        stats = calculate_group_statistics([player])

        assert stats["player_count"] == 1
        assert stats["total_score"] == 25
        assert stats["average_score"] == 25.0
        assert stats["min_score"] == 25
        assert stats["max_score"] == 25
        assert stats["top_player"]["full_name"] == "Test Player"


@pytest.fixture
def position_players() -> list[PlayerScore]:
    """Create sample players with position data for testing."""
    return [
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            position_code="C",
            position="Center",
            position_type="Forward",
        ),
        PlayerScore(
            first_name="Leon",
            last_name="Draisaitl",
            full_name="Leon Draisaitl",
            first_score=18,
            last_score=24,
            full_score=42,
            team="EDM",
            division="Pacific",
            conference="Western",
            position_code="L",
            position="Left Wing",
            position_type="Forward",
        ),
        PlayerScore(
            first_name="Cale",
            last_name="Makar",
            full_name="Cale Makar",
            first_score=11,
            last_score=16,
            full_score=27,
            team="COL",
            division="Central",
            conference="Western",
            position_code="D",
            position="Defense",
            position_type="Defense",
        ),
        PlayerScore(
            first_name="Connor",
            last_name="Hellebuyck",
            full_name="Connor Hellebuyck",
            first_score=20,
            last_score=26,
            full_score=46,
            team="WPG",
            division="Central",
            conference="Western",
            position_code="G",
            position="Goalie",
            position_type="Goalie",
        ),
        PlayerScore(
            first_name="David",
            last_name="Pastrnak",
            full_name="David Pastrnak",
            first_score=15,
            last_score=23,
            full_score=38,
            team="BOS",
            division="Atlantic",
            conference="Eastern",
            position_code="R",
            position="Right Wing",
            position_type="Forward",
        ),
    ]


class TestGroupByPosition:
    """Test grouping players by specific position (Center, Left Wing, etc.)."""

    def test_group_by_position(self, position_players: list[PlayerScore]) -> None:
        """Test grouping players by specific position."""
        grouped = group_by_position(position_players)

        assert "Center" in grouped
        assert "Left Wing" in grouped
        assert "Right Wing" in grouped
        assert "Defense" in grouped
        assert "Goalie" in grouped

        assert len(grouped["Center"]) == 1
        assert len(grouped["Left Wing"]) == 1
        assert len(grouped["Right Wing"]) == 1
        assert len(grouped["Defense"]) == 1
        assert len(grouped["Goalie"]) == 1

    def test_group_by_position_player_names(self, position_players: list[PlayerScore]) -> None:
        """Test that grouped players are correct."""
        grouped = group_by_position(position_players)

        assert grouped["Center"][0].full_name == "Connor McDavid"
        assert grouped["Left Wing"][0].full_name == "Leon Draisaitl"
        assert grouped["Defense"][0].full_name == "Cale Makar"
        assert grouped["Goalie"][0].full_name == "Connor Hellebuyck"
        assert grouped["Right Wing"][0].full_name == "David Pastrnak"

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_position([])
        assert grouped == {}

    def test_group_unknown_position(self) -> None:
        """Test grouping players with unknown position."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=10,
            full_score=20,
            team="TST",
            division="Test",
            conference="Test",
            position="",  # Unknown
        )

        grouped = group_by_position([player])
        assert "Unknown" in grouped
        assert len(grouped["Unknown"]) == 1


class TestGroupByPositionType:
    """Test grouping players by position type (Forward, Defense, Goalie)."""

    def test_group_by_position_type(self, position_players: list[PlayerScore]) -> None:
        """Test grouping players by position type."""
        grouped = group_by_position_type(position_players)

        assert "Forward" in grouped
        assert "Defense" in grouped
        assert "Goalie" in grouped

        # 3 forwards (Center, Left Wing, Right Wing)
        assert len(grouped["Forward"]) == 3
        assert len(grouped["Defense"]) == 1
        assert len(grouped["Goalie"]) == 1

    def test_group_by_position_type_player_names(
        self,
        position_players: list[PlayerScore],
    ) -> None:
        """Test that grouped players are correct."""
        grouped = group_by_position_type(position_players)

        forward_names = {p.full_name for p in grouped["Forward"]}
        assert "Connor McDavid" in forward_names
        assert "Leon Draisaitl" in forward_names
        assert "David Pastrnak" in forward_names

        assert grouped["Defense"][0].full_name == "Cale Makar"
        assert grouped["Goalie"][0].full_name == "Connor Hellebuyck"

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_position_type([])
        assert grouped == {}

    def test_group_unknown_position_type(self) -> None:
        """Test grouping players with unknown position type."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=10,
            full_score=20,
            team="TST",
            division="Test",
            conference="Test",
            position_type="",  # Unknown
        )

        grouped = group_by_position_type([player])
        assert "Unknown" in grouped
        assert len(grouped["Unknown"]) == 1


class TestGroupByPositionCode:
    """Test grouping players by position code (C, L, R, D, G)."""

    def test_group_by_position_code(self, position_players: list[PlayerScore]) -> None:
        """Test grouping players by position code."""
        grouped = group_by_position_code(position_players)

        assert "C" in grouped
        assert "L" in grouped
        assert "R" in grouped
        assert "D" in grouped
        assert "G" in grouped

        assert len(grouped["C"]) == 1
        assert len(grouped["L"]) == 1
        assert len(grouped["R"]) == 1
        assert len(grouped["D"]) == 1
        assert len(grouped["G"]) == 1

    def test_group_by_position_code_player_names(
        self,
        position_players: list[PlayerScore],
    ) -> None:
        """Test that grouped players are correct."""
        grouped = group_by_position_code(position_players)

        assert grouped["C"][0].full_name == "Connor McDavid"
        assert grouped["L"][0].full_name == "Leon Draisaitl"
        assert grouped["R"][0].full_name == "David Pastrnak"
        assert grouped["D"][0].full_name == "Cale Makar"
        assert grouped["G"][0].full_name == "Connor Hellebuyck"

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_by_position_code([])
        assert grouped == {}

    def test_group_unknown_position_code(self) -> None:
        """Test grouping players with unknown position code."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=10,
            full_score=20,
            team="TST",
            division="Test",
            conference="Test",
            position_code="",  # Unknown
        )

        grouped = group_by_position_code([player])
        assert "Unknown" in grouped
        assert len(grouped["Unknown"]) == 1
