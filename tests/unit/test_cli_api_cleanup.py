"""Comprehensive CLI tests to achieve 90%+ coverage.

This test module provides extensive coverage for the NHL Scrabble CLI, testing command-line argument
parsing, option combinations, error handling, output formats, and environment variable integration.

Target: Improve CLI coverage from ~50% to 90%+
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli, validate_cli_arguments, validate_output_path




class TestAPIClientSessionCleanup:
    """Tests for API client session cleanup using context manager."""

    @patch("nhl_scrabble.cli.PlayoffCalculator")
    @patch("nhl_scrabble.cli.DependencyContainer")
    @patch("nhl_scrabble.cli.ReportGenerator")
    def test_run_analysis_uses_api_client_context_manager(
        self,
        mock_report_gen: MagicMock,
        mock_container_class: MagicMock,
        mock_playoff_calc: MagicMock,
    ) -> None:
        """Test that run_analysis uses api_client as context manager for automatic cleanup.

        This test verifies that the API client session is properly closed via context manager
        (__enter__/__exit__), not relying on the destructor (__del__). This prevents the "session
        was not explicitly closed" warning.
        """
        from nhl_scrabble.cli import run_analysis
        from nhl_scrabble.config import Config

        # Create mock api_client with context manager support
        mock_api_client = MagicMock()
        mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
        mock_api_client.__exit__ = MagicMock(return_value=None)
        mock_api_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        # Create mock container
        mock_container = MagicMock()
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_container.create_team_processor.return_value = MagicMock(
            process_all_teams=MagicMock(return_value=({}, [], [])),
            calculate_division_standings=MagicMock(return_value={}),
            calculate_conference_standings=MagicMock(return_value={}),
        )
        mock_container_class.return_value = mock_container

        # Mock PlayoffCalculator
        mock_playoff_calc.return_value.calculate_playoff_standings.return_value = {}

        # Mock ReportGenerator
        mock_report_gen.return_value.get_report.return_value = "Test Report"

        # Create config
        config = Config(
            verbose=False,
            output_format="text",
            top_players_count=20,
            top_team_players_count=5,
        )

        # Run analysis
        result = run_analysis(config, quiet=True)

        # Verify context manager was used
        mock_api_client.__enter__.assert_called_once()
        mock_api_client.__exit__.assert_called_once()

        # Verify result
        assert result == "Test Report"

    @patch("nhl_scrabble.cli.DependencyContainer")
    def test_search_command_uses_api_client_context_manager(
        self,
        mock_container_class: MagicMock,
    ) -> None:
        """Test that search command uses api_client as context manager.

        Ensures search command also properly closes API client sessions.
        """
        # Create mock api_client with context manager support
        mock_api_client = MagicMock()
        mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
        mock_api_client.__exit__ = MagicMock(return_value=None)

        # Create mock container
        mock_container = MagicMock()
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_container.create_team_processor.return_value = MagicMock(
            process_all_teams=MagicMock(return_value=({}, [], [])),
        )
        mock_container_class.return_value = mock_container

        # Run search command
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "McDavid", "--quiet"])

        # Search command should succeed (exit code 0 or 1 for no results)
        assert result.exit_code in [0, 1]

        # Verify context manager was used
        mock_api_client.__enter__.assert_called_once()
        mock_api_client.__exit__.assert_called_once()

    @patch("nhl_scrabble.cli.DependencyContainer")
    def test_fetch_dashboard_data_uses_api_client_context_manager(
        self,
        mock_container_class: MagicMock,
    ) -> None:
        """Test that fetch_dashboard_data uses api_client as context manager.

        Ensures dashboard data fetching also properly closes API client sessions.
        """
        from nhl_scrabble.cli import fetch_dashboard_data
        from nhl_scrabble.config import Config

        # Create mock api_client with context manager support
        mock_api_client = MagicMock()
        mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
        mock_api_client.__exit__ = MagicMock(return_value=None)
        mock_api_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        # Create mock container
        mock_container = MagicMock()
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_container.create_team_processor.return_value = MagicMock(
            process_all_teams=MagicMock(return_value=({}, [], [])),
            calculate_division_standings=MagicMock(return_value={}),
            calculate_conference_standings=MagicMock(return_value={}),
        )
        mock_container_class.return_value = mock_container

        # Create config
        config = Config(
            verbose=False,
            output_format="text",
            top_players_count=20,
            top_team_players_count=5,
        )

        # Fetch dashboard data
        result = fetch_dashboard_data(config, quiet=True)

        # Verify context manager was used
        mock_api_client.__enter__.assert_called_once()
        mock_api_client.__exit__.assert_called_once()

        # Verify result structure
        assert result is not None
        assert "team_scores" in result
        assert "all_players" in result
