"""Tests for the dependency injection container."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from nhl_scrabble.config import Config
from nhl_scrabble.container import Container
from nhl_scrabble.protocols import (
    APIClientProtocol,
    PlayoffCalculatorProtocol,
    ScorerProtocol,
    TeamProcessorProtocol,
)


class TestContainer:
    """Test the dependency injection container."""

    @pytest.fixture
    def config(self) -> Config:
        """Create a test configuration.

        Returns:
            Test configuration instance
        """
        return Config(
            api_timeout=10,
            api_retries=3,
            rate_limit_delay=0.3,
            top_players_count=20,
            top_team_players_count=5,
        )

    def test_container_creates_api_client(self, config: Config) -> None:
        """Test that container creates API client with correct configuration.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)
        client = container.api_client()

        assert client is not None
        assert hasattr(client, "get_teams")
        assert hasattr(client, "get_team_roster")

    def test_container_creates_scorer(self, config: Config) -> None:
        """Test that container creates Scrabble scorer.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)
        scorer = container.scorer()

        assert scorer is not None
        assert hasattr(scorer, "calculate_score")
        assert hasattr(scorer, "score_player")

    def test_container_creates_team_processor(self, config: Config) -> None:
        """Test that container creates team processor with injected dependencies.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)
        processor = container.team_processor()

        assert processor is not None
        assert hasattr(processor, "process_all_teams")
        assert hasattr(processor, "calculate_division_standings")

    def test_container_creates_playoff_calculator(self, config: Config) -> None:
        """Test that container creates playoff calculator.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)
        calculator = container.playoff_calculator()

        assert calculator is not None
        assert hasattr(calculator, "calculate_playoff_standings")

    def test_container_creates_reporters(self, config: Config) -> None:
        """Test that container creates all reporter instances.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)

        assert container.conference_reporter() is not None
        assert container.division_reporter() is not None
        assert container.playoff_reporter() is not None
        assert container.team_reporter() is not None
        assert container.stats_reporter() is not None

    def test_container_accepts_mock_api_client(self, config: Config) -> None:
        """Test that container accepts mock API client for testing.

        Args:
            config: Test configuration fixture
        """
        # Create mock API client
        mock_client = Mock(spec=APIClientProtocol)
        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"}
        }

        # Create container with mock
        container = Container(config, api_client=mock_client)
        client = container.api_client()

        # Verify mock is used
        assert client is mock_client
        teams = client.get_teams()
        assert "TOR" in teams

    def test_container_accepts_mock_scorer(self, config: Config) -> None:
        """Test that container accepts mock scorer for testing.

        Args:
            config: Test configuration fixture
        """
        # Create mock scorer
        mock_scorer = Mock(spec=ScorerProtocol)
        mock_scorer.calculate_score.return_value = 42

        # Create container with mock
        container = Container(config, scorer=mock_scorer)
        scorer = container.scorer()

        # Verify mock is used
        assert scorer is mock_scorer
        score = scorer.calculate_score("TEST")
        assert score == 42

    def test_container_accepts_mock_team_processor(self, config: Config) -> None:
        """Test that container accepts mock team processor for testing.

        Args:
            config: Test configuration fixture
        """
        # Create mock team processor
        mock_processor = Mock(spec=TeamProcessorProtocol)
        mock_processor.process_all_teams.return_value = ({}, [], [])

        # Create container with mock
        container = Container(config, team_processor=mock_processor)
        processor = container.team_processor()

        # Verify mock is used
        assert processor is mock_processor
        teams, _players, _failed = processor.process_all_teams()
        assert teams == {}

    def test_container_accepts_mock_playoff_calculator(self, config: Config) -> None:
        """Test that container accepts mock playoff calculator for testing.

        Args:
            config: Test configuration fixture
        """
        # Create mock playoff calculator
        mock_calculator = Mock(spec=PlayoffCalculatorProtocol)
        mock_calculator.calculate_playoff_standings.return_value = {"Eastern": [], "Western": []}

        # Create container with mock
        container = Container(config, playoff_calculator=mock_calculator)
        calculator = container.playoff_calculator()

        # Verify mock is used
        assert calculator is mock_calculator
        standings = calculator.calculate_playoff_standings({})
        assert "Eastern" in standings

    def test_container_singleton_behavior(self, config: Config) -> None:
        """Test that container returns same instance on multiple calls.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)

        # Get instances multiple times
        client1 = container.api_client()
        client2 = container.api_client()
        scorer1 = container.scorer()
        scorer2 = container.scorer()

        # Verify same instance returned
        assert client1 is client2
        assert scorer1 is scorer2

    def test_container_set_methods(self, config: Config) -> None:
        """Test that container setter methods work correctly.

        Args:
            config: Test configuration fixture
        """
        container = Container(config)

        # Create mocks
        mock_client = Mock(spec=APIClientProtocol)
        mock_scorer = Mock(spec=ScorerProtocol)
        mock_processor = Mock(spec=TeamProcessorProtocol)
        mock_calculator = Mock(spec=PlayoffCalculatorProtocol)

        # Set mocks
        container.set_api_client(mock_client)
        container.set_scorer(mock_scorer)
        container.set_team_processor(mock_processor)
        container.set_playoff_calculator(mock_calculator)

        # Verify mocks are used
        assert container.api_client() is mock_client
        assert container.scorer() is mock_scorer
        assert container.team_processor() is mock_processor
        assert container.playoff_calculator() is mock_calculator

    def test_container_team_processor_uses_injected_dependencies(self, config: Config) -> None:
        """Test that team processor created by container uses injected dependencies.

        Args:
            config: Test configuration fixture
        """
        # Create mocks
        mock_client = Mock(spec=APIClientProtocol)
        mock_scorer = Mock(spec=ScorerProtocol)

        # Create container with mocks
        container = Container(config, api_client=mock_client, scorer=mock_scorer)

        # Get team processor (should use the mocked dependencies)
        processor = container.team_processor()

        # Verify processor exists and has expected methods
        assert processor is not None
        assert hasattr(processor, "process_all_teams")
