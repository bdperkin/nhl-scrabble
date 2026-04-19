"""Tests for to_dict() methods on dataclasses."""

import json
from dataclasses import asdict

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def sample_player() -> PlayerScore:
    """Create a sample player for testing."""
    return PlayerScore(
        first_name="Alexander",
        last_name="Ovechkin",
        full_name="Alexander Ovechkin",
        first_score=22,
        last_score=34,
        full_score=56,
        team="WSH",
        division="Metropolitan",
        conference="Eastern",
    )


@pytest.fixture
def sample_team(sample_player: PlayerScore) -> TeamScore:
    """Create a sample team for testing."""
    return TeamScore(
        abbrev="WSH",
        total=250,
        players=[sample_player],
        division="Metropolitan",
        conference="Eastern",
    )


@pytest.fixture
def sample_division_standings() -> DivisionStandings:
    """Create sample division standings."""
    return DivisionStandings(
        name="Metropolitan",
        total=5000,
        teams=["WSH", "NYR", "PHI"],
        player_count=75,
        avg_per_team=1666.67,
    )


@pytest.fixture
def sample_conference_standings() -> ConferenceStandings:
    """Create sample conference standings."""
    return ConferenceStandings(
        name="Eastern",
        total=10000,
        teams=["WSH", "NYR", "PHI", "TOR", "BOS", "TBL"],
        player_count=150,
        avg_per_team=1666.67,
    )


@pytest.fixture
def sample_playoff_team() -> PlayoffTeam:
    """Create a sample playoff team."""
    return PlayoffTeam(
        abbrev="WSH",
        total=250,
        players=25,
        avg=10.0,
        conference="Eastern",
        division="Metropolitan",
        seed_type="Metropolitan #1",
        in_playoffs=True,
        division_rank=1,
        status_indicator="y",
    )


class TestPlayerScoreToDict:
    """Tests for PlayerScore.to_dict()."""

    def test_to_dict_matches_asdict(self, sample_player: PlayerScore) -> None:
        """Verify to_dict() produces same output as asdict()."""
        manual_dict = sample_player.to_dict()
        asdict_output = asdict(sample_player)

        # Should be identical
        assert manual_dict == asdict_output

    def test_to_dict_contains_all_fields(self, sample_player: PlayerScore) -> None:
        """Verify to_dict() includes all expected fields."""
        result = sample_player.to_dict()

        expected_fields = {
            "first_name",
            "last_name",
            "full_name",
            "first_score",
            "last_score",
            "full_score",
            "team",
            "division",
            "conference",
        }

        assert set(result.keys()) == expected_fields

    def test_to_dict_values_correct(self, sample_player: PlayerScore) -> None:
        """Verify to_dict() values match object attributes."""
        result = sample_player.to_dict()

        assert result["first_name"] == "Alexander"
        assert result["last_name"] == "Ovechkin"
        assert result["full_name"] == "Alexander Ovechkin"
        assert result["first_score"] == 22
        assert result["last_score"] == 34
        assert result["full_score"] == 56
        assert result["team"] == "WSH"
        assert result["division"] == "Metropolitan"
        assert result["conference"] == "Eastern"

    def test_to_dict_json_serializable(self, sample_player: PlayerScore) -> None:
        """Verify to_dict() output is JSON-serializable."""
        player_dict = sample_player.to_dict()

        # Should not raise
        json_str = json.dumps(player_dict)
        assert isinstance(json_str, str)

        # Should be able to round-trip
        loaded = json.loads(json_str)
        assert loaded == player_dict


class TestTeamScoreToDict:
    """Tests for TeamScore.to_dict()."""

    def test_to_dict_with_players(self, sample_team: TeamScore) -> None:
        """Verify to_dict() includes players when requested."""
        result = sample_team.to_dict(include_players=True)

        assert "players" in result
        assert len(result["players"]) == 1
        assert result["players"][0]["full_name"] == "Alexander Ovechkin"

    def test_to_dict_without_players(self, sample_team: TeamScore) -> None:
        """Verify to_dict() excludes players when requested."""
        result = sample_team.to_dict(include_players=False)

        assert "players" not in result
        assert "player_count" in result
        assert result["player_count"] == 1

    def test_to_dict_default_includes_players(self, sample_team: TeamScore) -> None:
        """Verify to_dict() includes players by default."""
        result = sample_team.to_dict()

        assert "players" in result
        assert len(result["players"]) == 1

    def test_to_dict_contains_expected_fields(self, sample_team: TeamScore) -> None:
        """Verify to_dict() includes all expected fields."""
        result = sample_team.to_dict()

        expected_base_fields = {
            "abbrev",
            "total",
            "division",
            "conference",
            "avg_per_player",
            "player_count",
            "players",
        }

        assert set(result.keys()) == expected_base_fields

    def test_to_dict_values_correct(self, sample_team: TeamScore) -> None:
        """Verify to_dict() values match object attributes."""
        result = sample_team.to_dict()

        assert result["abbrev"] == "WSH"
        assert result["total"] == 250
        assert result["division"] == "Metropolitan"
        assert result["conference"] == "Eastern"
        assert result["avg_per_player"] == 250.0
        assert result["player_count"] == 1

    def test_to_dict_json_serializable(self, sample_team: TeamScore) -> None:
        """Verify to_dict() output is JSON-serializable."""
        team_dict = sample_team.to_dict()

        # Should not raise
        json_str = json.dumps(team_dict)
        assert isinstance(json_str, str)

        # Should be able to round-trip
        loaded = json.loads(json_str)
        assert loaded == team_dict

    def test_to_dict_nested_players_are_dicts(self, sample_team: TeamScore) -> None:
        """Verify players are converted to dicts, not PlayerScore objects."""
        result = sample_team.to_dict()

        assert isinstance(result["players"], list)
        assert len(result["players"]) > 0
        assert isinstance(result["players"][0], dict)
        assert not isinstance(result["players"][0], PlayerScore)  # type: ignore[unreachable]


class TestDivisionStandingsToDict:
    """Tests for DivisionStandings.to_dict()."""

    def test_to_dict_matches_asdict(self, sample_division_standings: DivisionStandings) -> None:
        """Verify to_dict() produces same output as asdict()."""
        manual_dict = sample_division_standings.to_dict()
        asdict_output = asdict(sample_division_standings)

        assert manual_dict == asdict_output

    def test_to_dict_contains_all_fields(
        self, sample_division_standings: DivisionStandings
    ) -> None:
        """Verify to_dict() includes all expected fields."""
        result = sample_division_standings.to_dict()

        expected_fields = {"name", "total", "teams", "player_count", "avg_per_team"}

        assert set(result.keys()) == expected_fields

    def test_to_dict_json_serializable(self, sample_division_standings: DivisionStandings) -> None:
        """Verify to_dict() output is JSON-serializable."""
        standings_dict = sample_division_standings.to_dict()

        # Should not raise
        json_str = json.dumps(standings_dict)
        assert isinstance(json_str, str)


class TestConferenceStandingsToDict:
    """Tests for ConferenceStandings.to_dict()."""

    def test_to_dict_matches_asdict(self, sample_conference_standings: ConferenceStandings) -> None:
        """Verify to_dict() produces same output as asdict()."""
        manual_dict = sample_conference_standings.to_dict()
        asdict_output = asdict(sample_conference_standings)

        assert manual_dict == asdict_output

    def test_to_dict_contains_all_fields(
        self, sample_conference_standings: ConferenceStandings
    ) -> None:
        """Verify to_dict() includes all expected fields."""
        result = sample_conference_standings.to_dict()

        expected_fields = {"name", "total", "teams", "player_count", "avg_per_team"}

        assert set(result.keys()) == expected_fields

    def test_to_dict_json_serializable(
        self, sample_conference_standings: ConferenceStandings
    ) -> None:
        """Verify to_dict() output is JSON-serializable."""
        standings_dict = sample_conference_standings.to_dict()

        # Should not raise
        json_str = json.dumps(standings_dict)
        assert isinstance(json_str, str)


class TestPlayoffTeamToDict:
    """Tests for PlayoffTeam.to_dict()."""

    def test_to_dict_matches_asdict(self, sample_playoff_team: PlayoffTeam) -> None:
        """Verify to_dict() produces same output as asdict()."""
        manual_dict = sample_playoff_team.to_dict()
        asdict_output = asdict(sample_playoff_team)

        assert manual_dict == asdict_output

    def test_to_dict_contains_all_fields(self, sample_playoff_team: PlayoffTeam) -> None:
        """Verify to_dict() includes all expected fields."""
        result = sample_playoff_team.to_dict()

        expected_fields = {
            "abbrev",
            "total",
            "players",
            "avg",
            "conference",
            "division",
            "seed_type",
            "in_playoffs",
            "division_rank",
            "status_indicator",
        }

        assert set(result.keys()) == expected_fields

    def test_to_dict_values_correct(self, sample_playoff_team: PlayoffTeam) -> None:
        """Verify to_dict() values match object attributes."""
        result = sample_playoff_team.to_dict()

        assert result["abbrev"] == "WSH"
        assert result["total"] == 250
        assert result["players"] == 25
        assert result["avg"] == 10.0
        assert result["conference"] == "Eastern"
        assert result["division"] == "Metropolitan"
        assert result["seed_type"] == "Metropolitan #1"
        assert result["in_playoffs"] is True
        assert result["division_rank"] == 1
        assert result["status_indicator"] == "y"

    def test_to_dict_json_serializable(self, sample_playoff_team: PlayoffTeam) -> None:
        """Verify to_dict() output is JSON-serializable."""
        team_dict = sample_playoff_team.to_dict()

        # Should not raise
        json_str = json.dumps(team_dict)
        assert isinstance(json_str, str)

        # Should be able to round-trip
        loaded = json.loads(json_str)
        assert loaded == team_dict


class TestToJsonIntegration:
    """Integration tests for JSON serialization with to_dict()."""

    def test_full_json_dump(
        self,
        sample_player: PlayerScore,
        sample_team: TeamScore,
        sample_division_standings: DivisionStandings,
        sample_conference_standings: ConferenceStandings,
        sample_playoff_team: PlayoffTeam,
    ) -> None:
        """Test full JSON dump with all dataclasses."""
        data = {
            "teams": {"WSH": sample_team.to_dict()},
            "divisions": {"Metropolitan": sample_division_standings.to_dict()},
            "conferences": {"Eastern": sample_conference_standings.to_dict()},
            "playoffs": {"Eastern": [sample_playoff_team.to_dict()]},
        }

        # Should serialize without errors
        json_str = json.dumps(data, indent=2)
        assert isinstance(json_str, str)

        # Should be able to parse back
        loaded = json.loads(json_str)
        assert loaded == data
