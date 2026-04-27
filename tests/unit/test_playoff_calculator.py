"""Unit tests for playoff calculator."""

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator


class TestPlayoffCalculator:
    """Tests for PlayoffCalculator class."""

    @pytest.fixture
    def calculator(self) -> PlayoffCalculator:
        """Return a PlayoffCalculator instance."""
        return PlayoffCalculator()

    @pytest.fixture
    def sample_teams(self) -> dict[str, TeamScore]:
        """Create sample teams for testing."""
        # Create some players
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

        teams = {
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
            "TBL": TeamScore(
                "TBL",
                "Tampa Bay Lightning",
                380,
                [player1] * 25,
                "Atlantic",
                "Eastern",
            ),
            "EDM": TeamScore("EDM", "Edmonton Oilers", 520, [player3] * 25, "Pacific", "Western"),
            "VAN": TeamScore("VAN", "Vancouver Canucks", 480, [player3] * 25, "Pacific", "Western"),
            "CGY": TeamScore("CGY", "Calgary Flames", 440, [player3] * 25, "Pacific", "Western"),
            "SEA": TeamScore("SEA", "Seattle Kraken", 420, [player3] * 25, "Pacific", "Western"),
        }

        return teams

    def test_calculate_playoff_standings(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test basic playoff standings calculation."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        assert "Eastern" in standings
        assert "Western" in standings
        assert len(standings["Eastern"]) > 0
        assert len(standings["Western"]) > 0

    def test_division_leaders_make_playoffs(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that top 3 from each division make playoffs."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        eastern_teams = standings["Eastern"]
        western_teams = standings["Western"]

        # Count playoff teams
        eastern_playoff = sum(1 for t in eastern_teams if t.in_playoffs)
        western_playoff = sum(1 for t in western_teams if t.in_playoffs)

        # Each conference should have at least 3 playoff teams (top 3 from one division)
        assert eastern_playoff >= 3
        assert western_playoff >= 3

    def test_presidents_trophy_assigned(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that Presidents' Trophy is assigned to team with highest points."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        all_teams = standings["Eastern"] + standings["Western"]
        presidents_teams = [t for t in all_teams if t.status_indicator == "p"]

        # Exactly one team should have Presidents' Trophy
        assert len(presidents_teams) == 1

        # It should be EDM with 520 points
        assert presidents_teams[0].abbrev == "EDM"
        assert presidents_teams[0].total == 520

    def test_division_leaders_get_y_indicator(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that division leaders get 'y' status (unless they have higher status)."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        all_teams = standings["Eastern"] + standings["Western"]

        # TOR should be Atlantic leader (500 points, highest in Atlantic)
        tor = next(t for t in all_teams if t.abbrev == "TOR")
        # TOR should have 'y' or higher ('z' or 'p')
        assert tor.status_indicator in ["y", "z", "p"]
        assert tor.division_rank == 1

    def test_eliminated_teams_get_e_indicator(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that eliminated teams get 'e' status."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        all_teams = standings["Eastern"] + standings["Western"]
        eliminated_teams = [t for t in all_teams if not t.in_playoffs]

        for team in eliminated_teams:
            assert team.status_indicator == "e"

    def test_playoff_teams_get_x_or_higher(
        self,
        calculator: PlayoffCalculator,
        sample_teams: dict[str, TeamScore],
    ) -> None:
        """Test that playoff teams have at least 'x' status."""
        standings = calculator.calculate_playoff_standings(sample_teams)

        all_teams = standings["Eastern"] + standings["Western"]
        playoff_teams = [t for t in all_teams if t.in_playoffs]

        for team in playoff_teams:
            # Status should be one of: x (playoff), y (division), z (conference), p (presidents)
            assert team.status_indicator in ["x", "y", "z", "p"]
