"""Unit tests for data models."""

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore


class TestPlayerScore:
    """Tests for PlayerScore model."""

    def test_player_score_creation(self) -> None:
        """Test creating a PlayerScore instance."""
        player = PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=15,
            last_score=17,
            full_score=32,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert player.first_name == "Connor"
        assert player.last_name == "McDavid"
        assert player.full_score == 32
        assert player.team == "EDM"

    def test_player_score_repr(self, sample_player: PlayerScore) -> None:
        """Test PlayerScore string representation."""
        repr_str = repr(sample_player)
        assert "Connor McDavid" in repr_str
        assert "EDM" in repr_str


class TestTeamScore:
    """Tests for TeamScore model."""

    def test_team_score_creation(self, sample_player: PlayerScore) -> None:
        """Test creating a TeamScore instance."""
        team = TeamScore(
            abbrev="EDM",
            total=100,
            players=[sample_player],
            division="Pacific",
            conference="Western",
        )

        assert team.abbrev == "EDM"
        assert team.total == 100
        assert len(team.players) == 1
        assert team.division == "Pacific"

    def test_team_score_avg_calculation(self, sample_player: PlayerScore) -> None:
        """Test that avg_per_player is calculated automatically."""
        team = TeamScore(
            abbrev="EDM",
            total=100,
            players=[sample_player, sample_player],  # 2 players
            division="Pacific",
            conference="Western",
        )

        assert team.avg_per_player == 50.0  # 100 / 2

    def test_team_score_empty_players(self) -> None:
        """Test team with no players."""
        team = TeamScore(
            abbrev="EDM",
            total=0,
            players=[],
            division="Pacific",
            conference="Western",
        )

        assert team.avg_per_player == 0.0
        assert team.player_count == 0

    def test_team_score_player_count(self, sample_player: PlayerScore) -> None:
        """Test player_count property."""
        team = TeamScore(
            abbrev="EDM",
            total=100,
            players=[sample_player, sample_player, sample_player],
            division="Pacific",
            conference="Western",
        )

        assert team.player_count == 3


class TestDivisionStandings:
    """Tests for DivisionStandings model."""

    def test_division_standings_creation(self) -> None:
        """Test creating a DivisionStandings instance."""
        standings = DivisionStandings(
            name="Pacific",
            total=1000,
            teams=["EDM", "VAN", "CGY"],
            player_count=75,
            avg_per_team=333.33,
        )

        assert standings.name == "Pacific"
        assert standings.total == 1000
        assert len(standings.teams) == 3
        assert standings.avg_per_team == 333.33


class TestConferenceStandings:
    """Tests for ConferenceStandings model."""

    def test_conference_standings_creation(self) -> None:
        """Test creating a ConferenceStandings instance."""
        standings = ConferenceStandings(
            name="Western",
            total=5000,
            teams=["EDM", "VAN", "CGY", "SEA"],
            player_count=150,
            avg_per_team=1250.0,
        )

        assert standings.name == "Western"
        assert standings.total == 5000
        assert len(standings.teams) == 4


class TestPlayoffTeam:
    """Tests for PlayoffTeam model."""

    def test_playoff_team_creation(self) -> None:
        """Test creating a PlayoffTeam instance."""
        team = PlayoffTeam(
            abbrev="EDM",
            total=1500,
            players=25,
            avg=60.0,
            conference="Western",
            division="Pacific",
            seed_type="Pacific #1",
            in_playoffs=True,
            division_rank=1,
            status_indicator="y",
        )

        assert team.abbrev == "EDM"
        assert team.in_playoffs is True
        assert team.status_indicator == "y"
        assert team.seed_type == "Pacific #1"

    def test_playoff_team_defaults(self) -> None:
        """Test PlayoffTeam with default values."""
        team = PlayoffTeam(
            abbrev="EDM",
            total=1500,
            players=25,
            avg=60.0,
            conference="Western",
            division="Pacific",
        )

        assert team.seed_type == ""
        assert team.in_playoffs is False
        assert team.division_rank == 0
        assert team.status_indicator == ""
