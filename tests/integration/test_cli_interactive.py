"""Integration tests for interactive CLI command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI runner."""
    return CliRunner()


class TestInteractiveCommand:
    """Test interactive command integration."""

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_basic(self, mock_shell_class: MagicMock, runner: CliRunner) -> None:
        """Test basic interactive command execution."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell_class.return_value = mock_shell

        # Run command
        result = runner.invoke(cli, ["interactive", "--no-fetch"])

        # Verify
        assert result.exit_code == 0
        mock_shell_class.assert_called_once()
        mock_shell.fetch_data.assert_not_called()
        mock_shell.run.assert_called_once()

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_with_fetch(self, mock_shell_class: MagicMock, runner: CliRunner) -> None:
        """Test interactive command with data fetching."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell_class.return_value = mock_shell

        # Run command
        result = runner.invoke(cli, ["interactive"])

        # Verify
        assert result.exit_code == 0
        mock_shell.fetch_data.assert_called_once()
        mock_shell.run.assert_called_once()

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_with_verbose(self, mock_shell_class: MagicMock, runner: CliRunner) -> None:
        """Test interactive command with verbose logging."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell_class.return_value = mock_shell

        # Run command
        result = runner.invoke(cli, ["interactive", "--verbose", "--no-fetch"])

        # Verify
        assert result.exit_code == 0
        mock_shell.run.assert_called_once()

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_keyboard_interrupt(
        self, mock_shell_class: MagicMock, runner: CliRunner
    ) -> None:
        """Test interactive command handles keyboard interrupt."""
        # Setup mock to raise KeyboardInterrupt
        mock_shell = MagicMock()
        mock_shell.run.side_effect = KeyboardInterrupt()
        mock_shell_class.return_value = mock_shell

        # Run command
        result = runner.invoke(cli, ["interactive", "--no-fetch"])

        # Verify clean exit
        assert result.exit_code == 0
        assert "Goodbye" in result.output or result.exit_code == 0

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_unexpected_error(
        self, mock_shell_class: MagicMock, runner: CliRunner
    ) -> None:
        """Test interactive command handles unexpected errors."""
        # Setup mock to raise error
        mock_shell = MagicMock()
        mock_shell.run.side_effect = RuntimeError("Test error")
        mock_shell_class.return_value = mock_shell

        # Run command
        result = runner.invoke(cli, ["interactive", "--no-fetch"])

        # Verify error handling
        assert result.exit_code == 1
        assert "error" in result.output.lower() or result.exit_code == 1
