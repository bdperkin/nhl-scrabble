"""Tests for interactive shell run method and i18n support."""

from __future__ import annotations

import os
import sys
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.interactive.shell import InteractiveShell
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore

# Skip all tests in this module on Windows due to prompt_toolkit requiring console
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="prompt_toolkit requires Windows console (not available in GitHub Actions CI)",
)


@pytest.fixture
def mock_team_scores() -> list[TeamScore]:
    """Create mock team scores for testing."""
    team1 = TeamScore(
        abbrev="TOR",
        name="Toronto Maple Leafs",
        total=1000,
        division="Atlantic",
        conference="Eastern",
        players=[
            PlayerScore(
                first_name="Auston",
                last_name="Matthews",
                full_name="Auston Matthews",
                first_score=12,
                last_score=88,
                full_score=100,
                team="TOR",
                division="Atlantic",
                conference="Eastern",
            ),
        ],
    )
    return [team1]


@pytest.fixture
def shell_with_data(mock_team_scores: list[TeamScore]) -> InteractiveShell:
    """Create shell instance with mock data."""
    shell = InteractiveShell()
    shell.data = {
        "teams": mock_team_scores,
        "standings": Mock(),
        "playoff_teams": mock_team_scores,
        "eastern": [mock_team_scores[0]],
        "western": [],
    }
    return shell


class TestRunMethodCoverage:
    """Test run() method coverage."""

    def test_run_exits_on_exit_command(self) -> None:
        """Test run exits on exit command."""
        shell = InteractiveShell()
        shell.data = {"teams": []}

        with (
            patch.object(shell.session, "prompt", return_value="exit"),
            patch.object(shell.console, "print"),
        ):
            shell.run()

    def test_run_executes_help_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes help command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["help", "exit"]),
            patch.object(shell_with_data, "cmd_help") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_show_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes show command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["show team TOR", "exit"]),
            patch.object(shell_with_data, "cmd_show") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_top_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes top command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["top", "exit"]),
            patch.object(shell_with_data, "cmd_top") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_bottom_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes bottom command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["bottom", "exit"]),
            patch.object(shell_with_data, "cmd_bottom") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_compare_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes compare command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["compare A B", "exit"]),
            patch.object(shell_with_data, "cmd_compare") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_filter_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes filter command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["filter div A", "exit"]),
            patch.object(shell_with_data, "cmd_filter") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_search_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes search command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["search M", "exit"]),
            patch.object(shell_with_data, "cmd_search") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_standings_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes standings command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["standings", "exit"]),
            patch.object(shell_with_data, "cmd_standings") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_playoff_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes playoff command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["playoff", "exit"]),
            patch.object(shell_with_data, "cmd_playoff") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_stats_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes stats command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["stats", "exit"]),
            patch.object(shell_with_data, "cmd_stats") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_executes_refresh_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run executes refresh command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["refresh", "exit"]),
            patch.object(shell_with_data, "cmd_refresh") as mock_cmd,
        ):
            shell_with_data.run()
            mock_cmd.assert_called()

    def test_run_handles_unknown_command(self, shell_with_data: InteractiveShell) -> None:
        """Test run handles unknown command."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["unknown", "exit"]),
            patch.object(shell_with_data.console, "print") as mock_print,
        ):
            shell_with_data.run()
            assert any("Unknown command" in str(call) for call in mock_print.call_args_list)

    def test_run_handles_no_data(self) -> None:
        """Test run handles no data loaded."""
        shell = InteractiveShell()

        with (
            patch.object(shell.session, "prompt", side_effect=["show team TOR", "exit"]),
            patch.object(shell.console, "print") as mock_print,
        ):
            shell.run()
            assert any("No data loaded" in str(call) for call in mock_print.call_args_list)

    def test_run_handles_keyboard_interrupt(self, shell_with_data: InteractiveShell) -> None:
        """Test run continues on Ctrl+C."""
        with (
            patch.object(
                shell_with_data.session,
                "prompt",
                side_effect=[KeyboardInterrupt(), "exit"],
            ),
            patch.object(shell_with_data.console, "print"),
        ):
            shell_with_data.run()

    def test_run_handles_eof(self, shell_with_data: InteractiveShell) -> None:
        """Test run exits on EOF."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=EOFError()),
            patch.object(shell_with_data.console, "print"),
        ):
            shell_with_data.run()

    def test_run_empty_input(self, shell_with_data: InteractiveShell) -> None:
        """Test run handles empty input."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=["", "exit"]),
            patch.object(shell_with_data.console, "print"),
        ):
            shell_with_data.run()
            # Should not raise

    def test_run_invalid_shlex_syntax(self, shell_with_data: InteractiveShell) -> None:
        """Test run handles invalid shlex syntax."""
        with (
            patch.object(shell_with_data.session, "prompt", side_effect=['show "unclosed', "exit"]),
            patch.object(shell_with_data.console, "print") as mock_print,
        ):
            shell_with_data.run()
            assert any("Invalid command syntax" in str(call) for call in mock_print.call_args_list)


class TestI18nSupport:
    """Test internationalization support in interactive shell."""

    def test_translator_is_initialized(self) -> None:
        """Test that translator function is available."""
        # Import the translator from the shell module
        from nhl_scrabble.interactive import shell

        # Verify _ function exists and is callable
        assert hasattr(shell, "_")
        assert callable(shell._)

    def test_shell_uses_translations(self, shell_with_data: InteractiveShell) -> None:
        """Test that shell commands use translation function."""
        # Test that help command uses translations
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_help([])
            # Should print translated help text
            assert mock_print.called

    @patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"})
    def test_shell_respects_locale_setting(self) -> None:
        """Test that shell respects NHL_SCRABBLE_LANG environment variable."""
        # Create a new shell with locale set
        shell = InteractiveShell()
        # Shell should initialize without errors
        assert shell is not None

    def test_welcome_message_is_translatable(self) -> None:
        """Test that welcome message uses translation."""
        shell = InteractiveShell()
        shell.data = {"teams": []}

        with (
            patch.object(shell.session, "prompt", side_effect=["exit"]),
            patch.object(shell.console, "print") as mock_print,
        ):
            shell.run()
            # Should print welcome message
            calls = [str(call) for call in mock_print.call_args_list]
            # Check that some form of welcome/help message was printed
            assert any(call for call in calls if call)  # At least one print call
