"""Comprehensive unit tests for CLI run_analysis() function.

This module provides extensive coverage for the run_analysis() function,
which orchestrates the complete NHL Scrabble analysis workflow.

Target: Improve coverage of run_analysis() function (lines 240-420)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import pytest

# CRITICAL: Import cli module and run_analysis to ensure coverage
from nhl_scrabble.cli import generate_excel_report, run_analysis
from nhl_scrabble.config import Config
from nhl_scrabble.filters import AnalysisFilters
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration object."""
    config = Mock(spec=Config)
    config.output_format = "text"
    config.top_players_count = 10
    config.top_team_players_count = 5
    config.api_timeout = 30
    config.api_retries = 3
    config.api_rate_limit_delay = 0.3
    return config


@pytest.fixture
def mock_team_scores() -> dict[str, TeamScore]:
    """Create mock team scores data."""
    player1 = PlayerScore(
        first_name="Alex",
        last_name="Ovechkin",
        full_name="Alex Ovechkin",
        first_score=15,
        last_score=27,
        full_score=42,
        team="WSH",
        division="Metropolitan",
        conference="Eastern",
        position_code="LW",
        position="Left Wing",
        position_type="Forward",
    )
    player2 = PlayerScore(
        first_name="Sidney",
        last_name="Crosby",
        full_name="Sidney Crosby",
        first_score=20,
        last_score=25,
        full_score=45,
        team="PIT",
        division="Metropolitan",
        conference="Eastern",
        position_code="C",
        position="Center",
        position_type="Forward",
    )

    team1 = TeamScore(
        abbrev="WSH",
        name="Capitals",
        total=420,
        players=[player1],
        division="Metropolitan",
        conference="Eastern",
    )
    team2 = TeamScore(
        abbrev="PIT",
        name="Penguins",
        total=450,
        players=[player2],
        division="Metropolitan",
        conference="Eastern",
    )

    return {"WSH": team1, "PIT": team2}


@pytest.fixture
def mock_division_standings() -> dict[str, DivisionStandings]:
    """Create mock division standings."""
    return {}


@pytest.fixture
def mock_conference_standings() -> dict[str, ConferenceStandings]:
    """Create mock conference standings."""
    return {}


@pytest.fixture
def mock_playoff_standings() -> dict[str, list[PlayoffTeam]]:
    """Create mock playoff standings."""
    return {}


class TestRunAnalysisBasics:
    """Test basic run_analysis() function behavior."""

    @patch("nhl_scrabble.cli.DependencyContainer")
    @patch("nhl_scrabble.cli.ProgressManager")
    @patch("nhl_scrabble.cli.PlayoffCalculator")
    @patch("nhl_scrabble.cli.ReportGenerator")
    def test_run_analysis_basic_text_format(
        self,
        mock_report_gen: MagicMock,
        mock_playoff_calc: MagicMock,
        mock_progress: MagicMock,
        mock_container: MagicMock,
        mock_config: Config,
        mock_team_scores: dict[str, TeamScore],
    ) -> None:
        """Test run_analysis with text format (default)."""
        # Setup mocks
        mock_api_client = MagicMock()
        mock_api_client.get_teams.return_value = [{"abbrev": "WSH"}, {"abbrev": "PIT"}]
        mock_container.return_value.create_api_client.return_value.__enter__.return_value = (
            mock_api_client
        )
        mock_container.return_value.create_api_client.return_value.__exit__.return_value = False

        mock_scorer = MagicMock()
        mock_container.return_value.create_scorer.return_value = mock_scorer

        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = (
            mock_team_scores,
            [],  # all_players
            [],  # failed_teams
        )
        mock_team_processor.calculate_division_standings.return_value = {}
        mock_team_processor.calculate_conference_standings.return_value = {}
        mock_container.return_value.create_team_processor.return_value = mock_team_processor

        mock_playoff_calc.return_value.calculate_playoff_standings.return_value = {}

        mock_report_gen.return_value.get_report.return_value = "Test Report"

        # Run analysis
        result = run_analysis(mock_config, quiet=True)

        # Verify
        assert result == "Test Report"
        mock_api_client.get_teams.assert_called_once()
        mock_team_processor.process_all_teams.assert_called_once()

    @patch("nhl_scrabble.cli.DependencyContainer")
    @patch("nhl_scrabble.cli.ProgressManager")
    @patch("nhl_scrabble.cli.PlayoffCalculator")
    def test_run_analysis_clear_cache(
        self,
        mock_playoff_calc: MagicMock,
        mock_progress: MagicMock,
        mock_container: MagicMock,
        mock_config: Config,
    ) -> None:
        """Test run_analysis with clear_cache=True."""
        # Setup mocks
        mock_api_client = MagicMock()
        mock_api_client.get_teams.return_value = []
        mock_container.return_value.create_api_client.return_value.__enter__.return_value = (
            mock_api_client
        )
        mock_container.return_value.create_api_client.return_value.__exit__.return_value = False

        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_team_processor.calculate_division_standings.return_value = {}
        mock_team_processor.calculate_conference_standings.return_value = {}
        mock_container.return_value.create_team_processor.return_value = mock_team_processor

        mock_container.return_value.create_scorer.return_value = MagicMock()
        mock_playoff_calc.return_value.calculate_playoff_standings.return_value = {}

        # Run analysis with clear_cache
        with patch("nhl_scrabble.cli.ReportGenerator") as mock_report_gen:
            mock_report_gen.return_value.get_report.return_value = "Test"
            run_analysis(mock_config, clear_cache=True, quiet=True)

        # Verify cache was cleared
        mock_api_client.clear_cache.assert_called_once()

    @patch("nhl_scrabble.cli.DependencyContainer")
    @patch("nhl_scrabble.cli.ProgressManager")
    @patch("nhl_scrabble.cli.PlayoffCalculator")
    def test_run_analysis_with_season(
        self,
        mock_playoff_calc: MagicMock,
        mock_progress: MagicMock,
        mock_container: MagicMock,
        mock_config: Config,
    ) -> None:
        """Test run_analysis with specific season."""
        # Setup mocks
        mock_api_client = MagicMock()
        mock_api_client.get_teams.return_value = []
        mock_container.return_value.create_api_client.return_value.__enter__.return_value = (
            mock_api_client
        )
        mock_container.return_value.create_api_client.return_value.__exit__.return_value = False

        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_team_processor.calculate_division_standings.return_value = {}
        mock_team_processor.calculate_conference_standings.return_value = {}
        mock_container.return_value.create_team_processor.return_value = mock_team_processor

        mock_container.return_value.create_scorer.return_value = MagicMock()
        mock_playoff_calc.return_value.calculate_playoff_standings.return_value = {}

        # Run analysis with specific season
        with patch("nhl_scrabble.cli.ReportGenerator") as mock_report_gen:
            mock_report_gen.return_value.get_report.return_value = "Test"
            run_analysis(mock_config, season="20222023", quiet=True)

        # Verify season was passed
        mock_api_client.get_teams.assert_called_with(season="20222023")
        mock_team_processor.process_all_teams.assert_called_with(season="20222023")
