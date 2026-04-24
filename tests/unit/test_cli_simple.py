"""Simplified unit tests for CLI module to improve coverage."""

import signal
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self) -> None:
        """Test that CLI help displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Scrabble" in result.output

    def test_cli_version(self) -> None:
        """Test that CLI version flag works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0

    def test_analyze_help(self) -> None:
        """Test that analyze command help displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
        assert "--format" in result.output
        assert "--output" in result.output
        assert "--verbose" in result.output

    def test_watch_help(self) -> None:
        """Test that watch command help displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--help"])

        assert result.exit_code == 0
        assert "watch" in result.output.lower()
        assert "--interval" in result.output
        assert "--format" in result.output
        assert "auto" in result.output.lower() or "refresh" in result.output.lower()

    def test_watch_invalid_interval(self) -> None:
        """Test that watch command rejects invalid interval."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "0"])

        assert result.exit_code != 0
        # Click IntRange validation provides error message
        assert (
            "invalid value" in result.output.lower() or "not in the range" in result.output.lower()
        )

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli.time.sleep")
    def test_watch_basic_iteration(self, mock_sleep: MagicMock, mock_run: MagicMock) -> None:
        """Test watch mode basic iteration.

        This test verifies that watch mode:
        1. Runs analysis at least once
        2. Displays proper output
        3. Exits gracefully when interrupted
        """
        # Configure mocks
        mock_run.return_value = "Test report output"

        # Simulate Ctrl+C after first iteration
        def raise_keyboard_interrupt(*args: object, **kwargs: object) -> None:
            raise KeyboardInterrupt

        mock_sleep.side_effect = raise_keyboard_interrupt

        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "1"])

        # Should exit cleanly
        assert result.exit_code == 0

        # Should run analysis at least once
        assert mock_run.call_count >= 1

        # Should display watch mode header
        assert "Watch Mode" in result.output or "watch" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli.signal.signal")
    def test_watch_signal_handler(self, mock_signal: MagicMock, mock_run: MagicMock) -> None:
        """Test watch mode registers signal handler."""
        mock_run.side_effect = KeyboardInterrupt

        runner = CliRunner()
        runner.invoke(cli, ["watch", "--interval", "1"])

        # Should register SIGINT handler
        mock_signal.assert_called_once_with(signal.SIGINT, mock_signal.call_args[0][1])
