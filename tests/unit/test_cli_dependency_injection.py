"""Tests demonstrating dependency injection benefits in CLI."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from nhl_scrabble.cli import run_analysis
from nhl_scrabble.config import Config
from nhl_scrabble.container import Container
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.protocols import (
    APIClientProtocol,
    PlayoffCalculatorProtocol,
    TeamProcessorProtocol,
)


class TestCLIDependencyInjection:
    """Test CLI with dependency injection for easier testing."""

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration.

        Returns:
            Test configuration instance
        """
        return Config(
            api_timeout=10,
            api_retries=3,
            rate_limit_delay=0.3,
            top_players_count=20,
            top_team_players_count=5,
            output_format="text",
        )

    @pytest.fixture
    def mock_team_scores(self) -> dict[str, TeamScore]:
        """Create mock team scores for testing.

        Returns:
            Dictionary of mock team scores
        """
        return {
            "TOR": TeamScore(
                abbrev="TOR",
                total=500,
                players=[
                    PlayerScore(
                        first_name="John",
                        last_name="Tavares",
                        full_name="John Tavares",
                        first_score=15,
                        last_score=30,
                        full_score=45,
                        team="TOR",
                        division="Atlantic",
                        conference="Eastern",
                    )
                ],
                division="Atlantic",
                conference="Eastern",
            ),
            "BOS": TeamScore(
                abbrev="BOS",
                total=450,
                players=[
                    PlayerScore(
                        first_name="Brad",
                        last_name="Marchand",
                        full_name="Brad Marchand",
                        first_score=12,
                        last_score=28,
                        full_score=40,
                        team="BOS",
                        division="Atlantic",
                        conference="Eastern",
                    )
                ],
                division="Atlantic",
                conference="Eastern",
            ),
        }

    @pytest.fixture
    def mock_players(self) -> list[PlayerScore]:
        """Create mock player list for testing.

        Returns:
            List of mock player scores
        """
        return [
            PlayerScore(
                first_name="John",
                last_name="Tavares",
                full_name="John Tavares",
                first_score=15,
                last_score=30,
                full_score=45,
                team="TOR",
                division="Atlantic",
                conference="Eastern",
            ),
            PlayerScore(
                first_name="Brad",
                last_name="Marchand",
                full_name="Brad Marchand",
                first_score=12,
                last_score=28,
                full_score=40,
                team="BOS",
                division="Atlantic",
                conference="Eastern",
            ),
        ]

    @pytest.fixture
    def mock_division_standings(self) -> dict[str, DivisionStandings]:
        """Create mock division standings for testing.

        Returns:
            Dictionary of mock division standings
        """
        return {
            "Atlantic": DivisionStandings(
                name="Atlantic",
                total=950,
                teams=["TOR", "BOS"],
                player_count=2,
                avg_per_team=475.0,
            )
        }

    @pytest.fixture
    def mock_conference_standings(self) -> dict[str, ConferenceStandings]:
        """Create mock conference standings for testing.

        Returns:
            Dictionary of mock conference standings
        """
        return {
            "Eastern": ConferenceStandings(
                name="Eastern",
                total=950,
                teams=["TOR", "BOS"],
                player_count=2,
                avg_per_team=475.0,
            )
        }

    @pytest.fixture
    def mock_playoff_standings(self) -> dict[str, list[PlayoffTeam]]:
        """Create mock playoff standings for testing.

        Returns:
            Dictionary of mock playoff standings
        """
        return {
            "Eastern": [
                PlayoffTeam(
                    abbrev="TOR",
                    total=500,
                    players=20,
                    avg=25.0,
                    division="Atlantic",
                    conference="Eastern",
                    seed_type="Atlantic #1",
                    in_playoffs=True,
                    division_rank=1,
                    status_indicator="y",
                ),
                PlayoffTeam(
                    abbrev="BOS",
                    total=450,
                    players=20,
                    avg=22.5,
                    division="Atlantic",
                    conference="Eastern",
                    seed_type="Atlantic #2",
                    in_playoffs=True,
                    division_rank=2,
                    status_indicator="x",
                ),
            ],
            "Western": [],
        }

    def test_run_analysis_with_mocked_dependencies(
        self,
        config: Config,
        mock_team_scores: dict[str, TeamScore],
        mock_players: list[PlayerScore],
        mock_division_standings: dict[str, DivisionStandings],
        mock_conference_standings: dict[str, ConferenceStandings],
        mock_playoff_standings: dict[str, list[PlayoffTeam]],
    ) -> None:
        """Test run_analysis with completely mocked dependencies.

        This demonstrates how dependency injection makes testing easier by allowing
        us to inject mocks instead of making real API calls.

        Args:
            config: Test configuration fixture
            mock_team_scores: Mock team scores fixture
            mock_players: Mock player list fixture
            mock_division_standings: Mock division standings fixture
            mock_conference_standings: Mock conference standings fixture
            mock_playoff_standings: Mock playoff standings fixture
        """
        # Create mock API client
        mock_api_client = Mock(spec=APIClientProtocol)
        mock_api_client.clear_cache = Mock()

        # Create mock team processor
        mock_team_processor = Mock(spec=TeamProcessorProtocol)
        mock_team_processor.process_all_teams.return_value = (
            mock_team_scores,
            mock_players,
            [],  # no failed teams
        )
        mock_team_processor.calculate_division_standings.return_value = mock_division_standings
        mock_team_processor.calculate_conference_standings.return_value = mock_conference_standings

        # Create mock playoff calculator
        mock_playoff_calculator = Mock(spec=PlayoffCalculatorProtocol)
        mock_playoff_calculator.calculate_playoff_standings.return_value = mock_playoff_standings

        # Create container with mocks
        container = Container(
            config,
            api_client=mock_api_client,
            team_processor=mock_team_processor,
            playoff_calculator=mock_playoff_calculator,
        )

        # Run analysis with mocked container
        result = run_analysis(config, container=container)

        # Verify report was generated
        assert isinstance(result, str)
        assert len(result) > 0

        # Verify mocks were called
        mock_team_processor.process_all_teams.assert_called_once()
        mock_team_processor.calculate_division_standings.assert_called_once_with(mock_team_scores)
        mock_team_processor.calculate_conference_standings.assert_called_once_with(mock_team_scores)
        mock_playoff_calculator.calculate_playoff_standings.assert_called_once_with(
            mock_team_scores
        )

    def test_run_analysis_with_clear_cache(
        self,
        config: Config,
        mock_team_scores: dict[str, TeamScore],
        mock_players: list[PlayerScore],
    ) -> None:
        """Test that clear_cache flag calls API client's clear_cache method.

        Args:
            config: Test configuration fixture
            mock_team_scores: Mock team scores fixture
            mock_players: Mock player list fixture
        """
        # Create mock API client
        mock_api_client = Mock(spec=APIClientProtocol)
        mock_api_client.clear_cache = Mock()

        # Create mock team processor
        mock_team_processor = Mock(spec=TeamProcessorProtocol)
        mock_team_processor.process_all_teams.return_value = (
            mock_team_scores,
            mock_players,
            [],
        )
        mock_team_processor.calculate_division_standings.return_value = {}
        mock_team_processor.calculate_conference_standings.return_value = {}

        # Create mock playoff calculator
        mock_playoff_calculator = Mock(spec=PlayoffCalculatorProtocol)
        mock_playoff_calculator.calculate_playoff_standings.return_value = {
            "Eastern": [],
            "Western": [],
        }

        # Create container with mocks
        container = Container(
            config,
            api_client=mock_api_client,
            team_processor=mock_team_processor,
            playoff_calculator=mock_playoff_calculator,
        )

        # Run analysis with clear_cache=True
        run_analysis(config, clear_cache=True, container=container)

        # Verify clear_cache was called
        mock_api_client.clear_cache.assert_called_once()

    def test_dependency_injection_reduces_coupling(self, config: Config) -> None:
        """Test that dependency injection reduces coupling between components.

        This test demonstrates that we can easily swap implementations without
        modifying the CLI code, showing reduced coupling.

        Args:
            config: Test configuration fixture
        """
        # Create first container with one set of implementations
        container1 = Container(config)
        processor1 = container1.team_processor()

        # Create second container with different implementations (mocks)
        mock_processor = Mock(spec=TeamProcessorProtocol)
        container2 = Container(config, team_processor=mock_processor)
        processor2 = container2.team_processor()

        # Verify we got different instances
        assert processor1 is not processor2
        assert processor2 is mock_processor

        # Both can be used with run_analysis without modifying the code
        # This demonstrates loose coupling through dependency injection
