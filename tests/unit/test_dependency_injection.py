"""Tests for dependency injection pattern.

This module demonstrates how Protocol-based dependency injection makes testing easier
by allowing simple mock implementations without complex mocking frameworks.

Benefits demonstrated:
    - Clean mock implementations using Protocols
    - No need for complex mocking libraries (for simple cases)
    - Type-safe dependency injection
    - Easy to swap implementations
"""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.config import Config
from nhl_scrabble.di import DependencyContainer, create_dependencies
from nhl_scrabble.interfaces import APIClientProtocol, ScorerProtocol, TeamProcessorProtocol
from nhl_scrabble.models.player import PlayerScore


class MockAPIClient:
    """Simple mock API client for testing (no mocking framework needed).

    This demonstrates how Protocols enable simple, type-safe mocks without inheritance or complex
    mocking frameworks.
    """

    def __init__(self) -> None:
        """Initialize mock with default data."""
        self.teams_called = False
        self.roster_calls: list[str] = []
        self.closed = False

    def get_teams(self, season: str | None = None) -> dict[str, dict[str, str]]:
        """Return mock teams data."""
        self.teams_called = True
        return {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
            "MTL": {"division": "Atlantic", "conference": "Eastern"},
            "BOS": {"division": "Atlantic", "conference": "Eastern"},
        }

    def get_team_roster(self, team_abbrev: str, season: str | None = None) -> dict[str, Any]:
        """Return mock roster data."""
        self.roster_calls.append(team_abbrev)
        return {
            "forwards": [
                {"firstName": {"default": "John"}, "lastName": {"default": "Doe"}},
                {"firstName": {"default": "Jane"}, "lastName": {"default": "Smith"}},
            ],
            "defensemen": [
                {"firstName": {"default": "Bob"}, "lastName": {"default": "Wilson"}},
            ],
            "goalies": [
                {"firstName": {"default": "Tom"}, "lastName": {"default": "Jones"}},
            ],
        }

    def clear_cache(self) -> None:
        """Clear cache (no-op for mock)."""

    def close(self) -> None:
        """Mark as closed."""
        self.closed = True


class MockScorer:
    """Simple mock scorer for testing."""

    def __init__(self) -> None:
        """Initialize mock."""
        self.score_calls: list[tuple[str, str]] = []

    def score_player(
        self, player_data: dict[str, Any], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Return mock player score."""
        first_name = player_data["firstName"]["default"]
        last_name = player_data["lastName"]["default"]
        self.score_calls.append((first_name, last_name))

        return PlayerScore(
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            first_score=10,
            last_score=15,
            full_score=25,
            team=team,
            division=division,
            conference=conference,
        )


# Test Protocol compatibility (these should type-check)
def accepts_api_client(client: APIClientProtocol) -> None:
    """Test function that accepts any APIClientProtocol."""
    _ = client.get_teams()


def accepts_scorer(scorer: ScorerProtocol) -> None:
    """Test function that accepts any ScorerProtocol."""
    player_data = {"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}
    _ = scorer.score_player(player_data, "TOR", "Atlantic", "Eastern")


class TestProtocolCompatibility:
    """Test that mock implementations satisfy Protocol interfaces."""

    def test_mock_api_client_satisfies_protocol(self) -> None:
        """Mock API client should satisfy APIClientProtocol without inheritance."""
        mock_client = MockAPIClient()

        # This should not raise TypeError
        accepts_api_client(mock_client)

        # Verify it works
        assert mock_client.teams_called
        mock_client.close()
        assert mock_client.closed

    def test_mock_scorer_satisfies_protocol(self) -> None:
        """Mock scorer should satisfy ScorerProtocol without inheritance."""
        mock_scorer = MockScorer()

        # This should not raise TypeError
        accepts_scorer(mock_scorer)

        # Verify it works
        assert len(mock_scorer.score_calls) == 1
        assert mock_scorer.score_calls[0] == ("Test", "Player")


class TestDependencyContainer:
    """Test the DependencyContainer factory."""

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config.from_env()

    @pytest.fixture
    def container(self, config: Config) -> DependencyContainer:
        """Create dependency container."""
        return DependencyContainer(config)

    def test_create_api_client(self, container: DependencyContainer) -> None:
        """Container should create properly configured API client."""
        client = container.create_api_client()

        # Verify it's a valid API client
        assert hasattr(client, "get_teams")
        assert hasattr(client, "get_team_roster")
        assert hasattr(client, "close")

        # Clean up
        client.close()

    def test_create_api_client_with_cache_override(self, container: DependencyContainer) -> None:
        """Container should allow cache override."""
        client = container.create_api_client(cache_enabled=False)

        # Verify it's created
        assert hasattr(client, "get_teams")

        # Clean up
        client.close()

    def test_create_scorer(self, container: DependencyContainer) -> None:
        """Container should create properly configured scorer."""
        scorer = container.create_scorer()

        # Verify it's a valid scorer
        assert hasattr(scorer, "score_player")

        # Test it works
        player_data = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}
        result = scorer.score_player(player_data, "EDM", "Pacific", "Western")
        assert isinstance(result, PlayerScore)
        assert result.first_name == "Connor"
        assert result.last_name == "McDavid"

    def test_create_scorer_with_custom_values(self, container: DependencyContainer) -> None:
        """Container should create scorer with custom letter values."""
        # All letters worth 1 point
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = container.create_scorer(letter_values=custom_values)

        # Verify custom scoring works
        player_data = {"firstName": {"default": "ALEX"}, "lastName": {"default": "TEST"}}
        result = scorer.score_player(player_data, "TOR", "Atlantic", "Eastern")
        assert result.first_score == 4  # "ALEX" = 4 letters x 1 point
        assert result.last_score == 4  # "TEST" = 4 letters x 1 point

    def test_create_team_processor(self, container: DependencyContainer) -> None:
        """Container should create team processor with auto-created dependencies."""
        processor = container.create_team_processor()

        # Verify it's a valid processor
        assert hasattr(processor, "process_all_teams")
        assert hasattr(processor, "calculate_division_standings")
        assert hasattr(processor, "calculate_conference_standings")

    def test_create_team_processor_with_mocks(self, container: DependencyContainer) -> None:
        """Container should create team processor with injected mock dependencies."""
        # Create mock dependencies
        mock_client = MockAPIClient()
        mock_scorer = MockScorer()

        # Inject mocks
        processor = container.create_team_processor(
            api_client=mock_client,
            scorer=mock_scorer,
        )

        # Process teams using mocks
        teams, players, _failed = processor.process_all_teams()

        # Verify mocks were called
        assert mock_client.teams_called
        assert len(mock_client.roster_calls) > 0
        assert len(mock_scorer.score_calls) > 0

        # Verify results
        assert len(teams) > 0
        assert len(players) > 0


class TestCreateDependenciesHelper:
    """Test the create_dependencies convenience function."""

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config.from_env()

    def test_create_all_dependencies(self, config: Config) -> None:
        """Helper should create all core dependencies."""
        api_client, scorer, processor = create_dependencies(config)

        # Verify all dependencies created
        assert hasattr(api_client, "get_teams")
        assert hasattr(scorer, "score_player")
        assert hasattr(processor, "process_all_teams")

        # Clean up
        api_client.close()

    def test_create_with_custom_scoring(self, config: Config) -> None:
        """Helper should create dependencies with custom scoring."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        api_client, scorer, _processor = create_dependencies(
            config,
            scoring_values=custom_values,
        )

        # Verify custom scoring
        player_data = {"firstName": {"default": "TEST"}, "lastName": {"default": "NAME"}}
        result = scorer.score_player(player_data, "TOR", "Atlantic", "Eastern")
        assert result.first_score == 4  # 4 letters x 1 point
        assert result.last_score == 4  # 4 letters x 1 point

        # Clean up
        api_client.close()

    def test_create_with_cache_disabled(self, config: Config) -> None:
        """Helper should create dependencies with cache disabled."""
        api_client, _scorer, _processor = create_dependencies(
            config,
            cache_enabled=False,
        )

        # Verify dependencies created
        assert hasattr(api_client, "get_teams")

        # Clean up
        api_client.close()


class TestDependencyInjectionBenefits:
    """Demonstrate the benefits of dependency injection for testing."""

    def test_easy_mocking_without_framework(self) -> None:
        """Protocol-based DI enables simple mocks without mocking frameworks."""
        # No need for Mock(), MagicMock(), patch(), etc.
        # Just create a simple class that implements the Protocol

        mock_api_client = MockAPIClient()
        mock_scorer = MockScorer()

        # Use mocks directly - they satisfy the Protocol interfaces
        from nhl_scrabble.processors.team_processor import TeamProcessor

        processor = TeamProcessor(mock_api_client, mock_scorer)

        # Call the real code with mock dependencies
        teams, _players, _failed = processor.process_all_teams()

        # Verify behavior
        assert mock_api_client.teams_called
        assert len(mock_api_client.roster_calls) == 3  # TOR, MTL, BOS
        assert len(mock_scorer.score_calls) == 12  # 4 players x 3 teams

        # Verify results
        assert len(teams) == 3
        assert "TOR" in teams
        assert "MTL" in teams
        assert "BOS" in teams

    def test_type_safe_dependency_injection(self) -> None:
        """Type checker ensures dependencies satisfy Protocol contracts."""
        # This code would fail type checking if mock doesn't satisfy Protocol
        mock_client: APIClientProtocol = MockAPIClient()
        mock_scorer: ScorerProtocol = MockScorer()

        # Type-safe injection
        from nhl_scrabble.processors.team_processor import TeamProcessor

        processor: TeamProcessorProtocol = TeamProcessor(mock_client, mock_scorer)

        # All type-safe!
        assert processor is not None

    def test_easy_to_swap_implementations(self) -> None:
        """DI makes it easy to swap between implementations."""
        from nhl_scrabble.api.nhl_client import NHLApiClient
        from nhl_scrabble.config import Config
        from nhl_scrabble.processors.team_processor import TeamProcessor
        from nhl_scrabble.scoring.scrabble import ScrabbleScorer

        config = Config.from_env()

        # Production: use real implementations
        prod_client: APIClientProtocol = NHLApiClient(
            base_url=config.api_base_url,
            timeout=config.api_timeout,
        )
        prod_scorer: ScorerProtocol = ScrabbleScorer()

        # Testing: use mock implementations
        test_client: APIClientProtocol = MockAPIClient()
        test_scorer: ScorerProtocol = MockScorer()

        # Same processor code works with both!
        prod_processor = TeamProcessor(prod_client, prod_scorer)
        test_processor = TeamProcessor(test_client, test_scorer)

        assert prod_processor is not None
        assert test_processor is not None

        # Clean up
        prod_client.close()

    def test_reduced_coupling(self) -> None:
        """DI reduces coupling - components depend on interfaces, not implementations."""
        from nhl_scrabble.processors.team_processor import TeamProcessor

        # TeamProcessor doesn't need to know about NHLApiClient or ScrabbleScorer
        # It only depends on the Protocol interfaces
        # This means we can change implementations without changing TeamProcessor

        mock_client = MockAPIClient()
        mock_scorer = MockScorer()

        processor = TeamProcessor(mock_client, mock_scorer)

        # Processor works with any implementation that satisfies the Protocols
        teams, _players, _failed = processor.process_all_teams()
        assert len(teams) > 0
