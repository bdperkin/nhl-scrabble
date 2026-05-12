"""Comprehensive unit tests for CLI commands (watch, dashboard).

This module provides coverage for additional CLI commands beyond analyze,
focusing on watch mode with signal handling and dashboard command.

Target: Improve coverage of watch (lines 1690-1832), dashboard commands
"""

from __future__ import annotations

import signal
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble.cli import _interruptible_sleep, cli


class TestInterruptibleSleep:
    """Test _interruptible_sleep helper function."""

    def test_interruptible_sleep_normal(self) -> None:
        """Test interruptible sleep completes normally."""
        shutdown_flag = [False]
        # Sleep for 0 seconds (should return immediately)
        _interruptible_sleep(0, shutdown_flag)
        assert shutdown_flag[0] is False

    def test_interruptible_sleep_checks_flag_each_second(self) -> None:
        """Test that sleep checks shutdown flag every second."""
        shutdown_flag = [False]

        call_count = [0]

        def mock_sleep(_seconds: float) -> None:
            call_count[0] += 1
            if call_count[0] >= 3:
                shutdown_flag[0] = True

        with patch("nhl_scrabble.cli.time.sleep", side_effect=mock_sleep):
            _interruptible_sleep(10, shutdown_flag)

        # Should have checked 3 times before shutdown
        assert call_count[0] == 3


class TestWatchCommand:
    """Test watch command implementation."""

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli.time.sleep")
    def test_watch_basic_execution(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test basic watch command execution."""
        mock_run.return_value = "Test report"
        # Simulate Ctrl+C after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "1"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_interval(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with custom interval."""
        mock_run.return_value = "Test report"
        # Interrupt after first sleep
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "60"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_json_format(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with JSON output format."""
        mock_run.return_value = '{"teams": []}'
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--format", "json", "--interval", "1"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_report_filter(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with specific report filter."""
        mock_run.return_value = "Playoff report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--report", "playoff", "--interval", "1"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_quiet_mode(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command in quiet mode."""
        mock_run.return_value = "Test report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--quiet", "--interval", "1"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_verbose_mode(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with verbose logging."""
        mock_run.return_value = "Test report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--verbose", "--interval", "1"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_with_no_cache(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with caching disabled."""
        mock_run.return_value = "Test report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--no-cache", "--interval", "1"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_handles_api_error(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command handles API errors gracefully."""
        from nhl_scrabble.api.nhl_client import NHLApiError

        # First call raises error, second triggers interrupt
        mock_run.side_effect = [NHLApiError("API down"), KeyboardInterrupt()]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "1"])

        # Should exit cleanly even with API error
        assert result.exit_code == 0
        assert "API Error" in result.output or "error" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_handles_generic_exception(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command handles unexpected exceptions."""
        # First call raises error, second triggers interrupt
        mock_run.side_effect = [Exception("Unexpected error"), KeyboardInterrupt()]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "1"])

        assert result.exit_code == 0
        assert "error" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli.signal.signal")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_registers_signal_handler(
        self,
        mock_sleep: MagicMock,
        mock_signal: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command registers SIGINT handler."""
        mock_run.return_value = "Test report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        runner.invoke(cli, ["watch", "--interval", "1"])

        # Should have registered signal handler for SIGINT
        assert mock_signal.called
        # First argument should be signal.SIGINT
        assert mock_signal.call_args[0][0] == signal.SIGINT

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli._interruptible_sleep")
    def test_watch_custom_player_limits(
        self,
        mock_sleep: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test watch command with custom player display limits."""
        mock_run.return_value = "Test report"
        mock_sleep.side_effect = KeyboardInterrupt()

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["watch", "--top-players", "30", "--top-team-players", "10", "--interval", "1"],
        )

        assert result.exit_code == 0


class TestDashboardCommand:
    """Test dashboard command implementation."""

    @patch("nhl_scrabble.cli.fetch_dashboard_data")
    @patch("nhl_scrabble.cli.StatisticsDashboard")
    def test_dashboard_static_mode(
        self,
        mock_dashboard: MagicMock,
        mock_fetch: MagicMock,
    ) -> None:
        """Test dashboard command in static mode."""
        mock_fetch.return_value = {
            "team_scores": {},
            "all_players": [],
            "division_standings": {},
            "conference_standings": {},
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--static"])

        assert result.exit_code == 0
        assert mock_dashboard.return_value.display_static.called

    @patch("nhl_scrabble.cli.fetch_dashboard_data")
    @patch("nhl_scrabble.cli.StatisticsDashboard")
    def test_dashboard_with_duration(
        self,
        mock_dashboard: MagicMock,
        mock_fetch: MagicMock,
    ) -> None:
        """Test dashboard command with custom duration."""
        mock_fetch.return_value = {
            "team_scores": {},
            "all_players": [],
            "division_standings": {},
            "conference_standings": {},
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--duration", "30"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.fetch_dashboard_data")
    @patch("nhl_scrabble.cli.StatisticsDashboard")
    def test_dashboard_with_filters(
        self,
        mock_dashboard: MagicMock,
        mock_fetch: MagicMock,
    ) -> None:
        """Test dashboard command with division/conference filters."""
        mock_fetch.return_value = {
            "team_scores": {},
            "all_players": [],
            "division_standings": {},
            "conference_standings": {},
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--divisions", "Atlantic"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.fetch_dashboard_data")
    def test_dashboard_handles_fetch_failure(
        self,
        mock_fetch: MagicMock,
    ) -> None:
        """Test dashboard handles data fetch failures."""
        mock_fetch.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--static"])

        assert result.exit_code == 1
        assert "Failed to fetch data" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling for various commands."""

    def test_invalid_interval_watch(self) -> None:
        """Test watch command with invalid interval."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "0"])

        assert result.exit_code != 0

    def test_invalid_format_watch(self) -> None:
        """Test watch command with invalid format."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--format", "invalid"])

        assert result.exit_code != 0
