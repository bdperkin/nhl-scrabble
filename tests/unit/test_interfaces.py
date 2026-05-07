"""Tests for Protocol interfaces.

This module tests that Protocol interfaces are properly defined and that concrete implementations
correctly satisfy the protocols.
"""

from __future__ import annotations

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.interfaces import (
    APIClientProtocol,
    ScorerProtocol,
    TeamProcessorProtocol,
)
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class TestAPIClientProtocol:
    """Test APIClientProtocol interface compliance."""

    def test_nhl_api_client_implements_protocol(self) -> None:
        """Test that NHLApiClient satisfies APIClientProtocol."""
        client = NHLApiClient()
        assert isinstance(client, APIClientProtocol)

    def test_protocol_has_get_teams_method(self) -> None:
        """Test that APIClientProtocol defines get_teams method."""
        assert hasattr(APIClientProtocol, "get_teams")

    def test_protocol_has_get_team_roster_method(self) -> None:
        """Test that APIClientProtocol defines get_team_roster method."""
        assert hasattr(APIClientProtocol, "get_team_roster")

    def test_protocol_has_clear_cache_method(self) -> None:
        """Test that APIClientProtocol defines clear_cache method."""
        assert hasattr(APIClientProtocol, "clear_cache")

    def test_protocol_has_close_method(self) -> None:
        """Test that APIClientProtocol defines close method."""
        assert hasattr(APIClientProtocol, "close")

    def test_protocol_has_context_manager_methods(self) -> None:
        """Test that APIClientProtocol defines __enter__ and __exit__ methods."""
        assert hasattr(APIClientProtocol, "__enter__")
        assert hasattr(APIClientProtocol, "__exit__")

    def test_api_client_context_manager(self) -> None:
        """Test that APIClientProtocol can be used as context manager."""
        with NHLApiClient() as client:
            assert isinstance(client, APIClientProtocol)

    def test_api_client_clear_cache(self) -> None:
        """Test that clear_cache method exists and is callable."""
        client = NHLApiClient()
        # Should not raise exception
        client.clear_cache()
        client.close()


class TestScorerProtocol:
    """Test ScorerProtocol interface compliance."""

    def test_scrabble_scorer_implements_protocol(self) -> None:
        """Test that ScrabbleScorer satisfies ScorerProtocol."""
        scorer = ScrabbleScorer()
        assert isinstance(scorer, ScorerProtocol)

    def test_protocol_has_score_player_method(self) -> None:
        """Test that ScorerProtocol defines score_player method."""
        assert hasattr(ScorerProtocol, "score_player")

    def test_scorer_can_score_player(self) -> None:
        """Test that scorer can score a player using protocol interface."""
        scorer = ScrabbleScorer()
        player_data = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
        }

        score = scorer.score_player(
            player_data=player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert score.first_name == "Connor"
        assert score.last_name == "McDavid"
        assert score.full_score > 0


class TestTeamProcessorProtocol:
    """Test TeamProcessorProtocol interface compliance."""

    def test_team_processor_implements_protocol(self) -> None:
        """Test that TeamProcessor satisfies TeamProcessorProtocol."""
        api_client = NHLApiClient()
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client=api_client, scorer=scorer)

        assert isinstance(processor, TeamProcessorProtocol)
        api_client.close()

    def test_protocol_has_process_all_teams_method(self) -> None:
        """Test that TeamProcessorProtocol defines process_all_teams method."""
        assert hasattr(TeamProcessorProtocol, "process_all_teams")

    def test_protocol_has_calculate_division_standings_method(self) -> None:
        """Test that TeamProcessorProtocol defines calculate_division_standings method."""
        assert hasattr(TeamProcessorProtocol, "calculate_division_standings")

    def test_protocol_has_calculate_conference_standings_method(self) -> None:
        """Test that TeamProcessorProtocol defines calculate_conference_standings method."""
        assert hasattr(TeamProcessorProtocol, "calculate_conference_standings")


class TestProtocolTypeChecking:
    """Test that protocols work correctly with type checking."""

    def test_protocol_accepts_conforming_implementation(self) -> None:
        """Test that a function accepting a protocol works with conforming classes."""

        def use_api_client(client: APIClientProtocol) -> None:
            """Accept APIClientProtocol and verify required methods."""
            assert hasattr(client, "get_teams")
            assert hasattr(client, "get_team_roster")

        # Should work with NHLApiClient
        client = NHLApiClient()
        use_api_client(client)
        client.close()

    def test_protocol_accepts_mock_implementation(self) -> None:
        """Test that protocols accept mock implementations for testing."""

        class MockAPIClient:
            """Mock API client for testing."""

            def get_teams(self, season: str | None = None) -> dict[str, dict[str, str]]:
                """Mock get_teams method."""
                return {"TOR": {"division": "Atlantic", "conference": "Eastern"}}

            def get_team_roster(
                self, team_abbrev: str, season: str | None = None,
            ) -> dict[str, list[dict[str, object]]]:
                """Mock get_team_roster method."""
                return {"forwards": [], "defensemen": [], "goalies": []}

            def clear_cache(self) -> None:
                """Mock clear_cache method."""

            def close(self) -> None:
                """Mock close method."""

            def __enter__(self) -> APIClientProtocol:
                """Mock context manager entry."""
                return self  # type: ignore[return-value]

            def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
                """Mock context manager exit."""

        # Should satisfy the protocol
        mock = MockAPIClient()
        assert isinstance(mock, APIClientProtocol)


class TestProtocolDocumentation:
    """Test that protocols have proper documentation."""

    def test_api_client_protocol_docstring(self) -> None:
        """Test that APIClientProtocol has documentation."""
        assert APIClientProtocol.__doc__ is not None
        assert "NHL API client" in APIClientProtocol.__doc__

    def test_scorer_protocol_docstring(self) -> None:
        """Test that ScorerProtocol has documentation."""
        assert ScorerProtocol.__doc__ is not None
        assert "scoring operations" in ScorerProtocol.__doc__

    def test_team_processor_protocol_docstring(self) -> None:
        """Test that TeamProcessorProtocol has documentation."""
        assert TeamProcessorProtocol.__doc__ is not None
        assert "team processing" in TeamProcessorProtocol.__doc__
