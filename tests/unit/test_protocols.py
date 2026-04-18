"""Tests demonstrating Protocol interfaces enable duck typing and mocking."""

from __future__ import annotations

from typing import Any

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.protocols import (
    APIClientProtocol,
    PlayoffCalculatorProtocol,
    ScorerProtocol,
    TeamProcessorProtocol,
)


class FakeAPIClient:
    """Fake API client for testing - implements APIClientProtocol without inheritance."""

    def __init__(self) -> None:
        """Initialize fake API client."""
        self.cache_cleared = False

    def get_teams(self) -> dict[str, dict[str, Any]]:
        """Return fake teams data.

        Returns:
            Dictionary of fake team data
        """
        return {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
            "BOS": {"division": "Atlantic", "conference": "Eastern"},
        }

    def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
        """Return fake roster data.

        Args:
            team_abbrev: Team abbreviation

        Returns:
            Dictionary of fake roster data
        """
        return {
            "forwards": [{"firstName": "John", "lastName": "Doe"}],
            "defensemen": [],
            "goalies": [],
        }

    def clear_cache(self) -> None:
        """Record that cache was cleared."""
        self.cache_cleared = True

    def close(self) -> None:
        """No-op close for fake client."""


class FakeScorer:
    """Fake scorer for testing - implements ScorerProtocol without inheritance."""

    def calculate_score(self, text: str) -> int:
        """Return fake score.

        Args:
            text: Text to score

        Returns:
            Fake score (always 42)
        """
        return 42

    def score_player(
        self, player_data: dict[str, Any], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Return fake player score.

        Args:
            player_data: Dictionary with 'firstName' and 'lastName' keys
            team: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            Fake PlayerScore object
        """
        first_name = player_data.get("firstName", {}).get("default", "Test")
        last_name = player_data.get("lastName", {}).get("default", "Player")
        return PlayerScore(
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            first_score=20,
            last_score=22,
            full_score=42,
            team=team,
            division=division,
            conference=conference,
        )


class FakeTeamProcessor:
    """Fake team processor for testing - implements TeamProcessorProtocol."""

    def __init__(self, api_client: APIClientProtocol, scorer: ScorerProtocol) -> None:
        """Initialize fake team processor.

        Args:
            api_client: API client to use
            scorer: Scorer to use
        """
        self.api_client = api_client
        self.scorer = scorer

    def process_all_teams(
        self,
    ) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
        """Return fake processing results.

        Returns:
            Tuple of fake team scores, players, and failed teams
        """
        return {}, [], []

    def calculate_division_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, DivisionStandings]:
        """Return fake division standings.

        Args:
            team_scores: Team scores dictionary

        Returns:
            Dictionary of fake division standings
        """
        return {}

    def calculate_conference_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, ConferenceStandings]:
        """Return fake conference standings.

        Args:
            team_scores: Team scores dictionary

        Returns:
            Dictionary of fake conference standings
        """
        return {}


class FakePlayoffCalculator:
    """Fake playoff calculator for testing - implements PlayoffCalculatorProtocol."""

    def calculate_playoff_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, list[PlayoffTeam]]:
        """Return fake playoff standings.

        Args:
            team_scores: Team scores dictionary

        Returns:
            Dictionary of fake playoff standings
        """
        return {"Eastern": [], "Western": []}


class TestProtocols:
    """Test that Protocol interfaces enable duck typing without inheritance."""

    def test_fake_api_client_satisfies_protocol(self) -> None:
        """Test that FakeAPIClient can be used as APIClientProtocol."""
        # Create fake client (no inheritance needed!)
        client: APIClientProtocol = FakeAPIClient()

        # Verify protocol methods work
        teams = client.get_teams()
        assert "TOR" in teams
        assert "BOS" in teams

        roster = client.get_team_roster("TOR")
        assert "forwards" in roster

        client.clear_cache()
        assert client.cache_cleared  # type: ignore[attr-defined]

    def test_fake_scorer_satisfies_protocol(self) -> None:
        """Test that FakeScorer can be used as ScorerProtocol."""
        # Create fake scorer (no inheritance needed!)
        scorer: ScorerProtocol = FakeScorer()

        # Verify protocol methods work
        score = scorer.calculate_score("TEST")
        assert score == 42

        player_data = {"firstName": {"default": "John"}, "lastName": {"default": "Doe"}}
        player_score = scorer.score_player(player_data, "TOR", "Atlantic", "Eastern")
        assert player_score.full_score == 42
        assert player_score.first_name == "John"

    def test_fake_team_processor_satisfies_protocol(self) -> None:
        """Test that FakeTeamProcessor can be used as TeamProcessorProtocol."""
        # Create fake dependencies
        client: APIClientProtocol = FakeAPIClient()
        scorer: ScorerProtocol = FakeScorer()

        # Create fake processor (no inheritance needed!)
        processor: TeamProcessorProtocol = FakeTeamProcessor(client, scorer)

        # Verify protocol methods work
        teams, players, failed = processor.process_all_teams()
        assert teams == {}
        assert players == []
        assert failed == []

    def test_fake_playoff_calculator_satisfies_protocol(self) -> None:
        """Test that FakePlayoffCalculator can be used as PlayoffCalculatorProtocol."""
        # Create fake calculator (no inheritance needed!)
        calculator: PlayoffCalculatorProtocol = FakePlayoffCalculator()

        # Verify protocol methods work
        standings = calculator.calculate_playoff_standings({})
        assert "Eastern" in standings
        assert "Western" in standings

    def test_protocols_enable_dependency_injection_without_inheritance(self) -> None:
        """Test that protocols enable DI without requiring inheritance.

        This demonstrates the key benefit of Protocol: we can use any class
        that implements the required methods, without forcing inheritance or
        modifying the class to declare it implements the protocol.
        """
        # Create fake implementations (no inheritance!)
        fake_client = FakeAPIClient()
        fake_scorer = FakeScorer()

        # These can be used anywhere that expects the protocol
        def process_with_dependencies(
            client: APIClientProtocol, scorer: ScorerProtocol
        ) -> tuple[dict[str, dict[str, Any]], int]:
            """Process with protocol dependencies.

            Args:
                client: API client protocol
                scorer: Scorer protocol

            Returns:
                Tuple of teams and sample score
            """
            teams = client.get_teams()
            score = scorer.calculate_score("TEST")
            return teams, score

        # Works with fake implementations
        teams, score = process_with_dependencies(fake_client, fake_scorer)
        assert "TOR" in teams
        assert score == 42

    def test_protocols_enable_testing_without_mocking_framework(self) -> None:
        """Test that protocols enable testing without mock framework.

        While mocking frameworks like unittest.mock are useful, protocols make it easy to create
        simple fake implementations for testing without any mocking library dependencies.
        """

        # Create simple fake for testing
        class SimpleTestScorer:
            """Minimal test scorer implementation."""

            def calculate_score(self, text: str) -> int:
                """Return length of text as score.

                Args:
                    text: Text to score

                Returns:
                    Length of text
                """
                return len(text)

            def score_player(
                self,
                player_data: dict[str, Any],
                team: str,
                division: str,
                conference: str,
            ) -> PlayerScore:
                """Return player score based on name lengths.

                Args:
                    player_data: Dictionary with 'firstName' and 'lastName' keys
                    team: Team abbreviation
                    division: Division name
                    conference: Conference name

                Returns:
                    PlayerScore with scores based on name lengths
                """
                first_name = player_data["firstName"]["default"]
                last_name = player_data["lastName"]["default"]
                first_score = len(first_name)
                last_score = len(last_name)
                return PlayerScore(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=f"{first_name} {last_name}",
                    first_score=first_score,
                    last_score=last_score,
                    full_score=first_score + last_score,
                    team=team,
                    division=division,
                    conference=conference,
                )

        # Use simple test scorer (no mocking framework needed!)
        scorer: ScorerProtocol = SimpleTestScorer()
        assert scorer.calculate_score("HELLO") == 5
        assert scorer.calculate_score("TEST") == 4

        player_data = {"firstName": {"default": "John"}, "lastName": {"default": "Doe"}}
        player = scorer.score_player(player_data, "TOR", "Atlantic", "Eastern")
        assert player.full_score == 7  # 4 + 3
