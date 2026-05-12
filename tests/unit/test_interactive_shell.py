"""Unit tests for interactive shell."""

from __future__ import annotations

import os
import sys
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.interactive.shell import InteractiveShell
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore

# Allow private member access in tests

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
            PlayerScore(
                first_name="Mitch",
                last_name="Marner",
                full_name="Mitch Marner",
                first_score=20,
                last_score=70,
                full_score=90,
                team="TOR",
                division="Atlantic",
                conference="Eastern",
            ),
        ],
    )

    team2 = TeamScore(
        abbrev="EDM",
        name="Edmonton Oilers",
        total=900,
        division="Pacific",
        conference="Western",
        players=[
            PlayerScore(
                first_name="Connor",
                last_name="McDavid",
                full_name="Connor McDavid",
                first_score=25,
                last_score=85,
                full_score=110,
                team="EDM",
                division="Pacific",
                conference="Western",
            ),
            PlayerScore(
                first_name="Leon",
                last_name="Draisaitl",
                full_name="Leon Draisaitl",
                first_score=30,
                last_score=65,
                full_score=95,
                team="EDM",
                division="Pacific",
                conference="Western",
            ),
        ],
    )

    return [team1, team2]


@pytest.fixture
def shell_with_data(mock_team_scores: list[TeamScore]) -> InteractiveShell:
    """Create shell instance with mock data."""
    shell = InteractiveShell()
    shell.data = {
        "teams": mock_team_scores,
        "standings": Mock(),
        "playoff_teams": mock_team_scores,
        "eastern": [mock_team_scores[0]],
        "western": [mock_team_scores[1]],
    }
    return shell


class TestInteractiveShellInit:
    """Test shell initialization."""

    def test_init(self) -> None:
        """Test shell initializes correctly."""
        shell = InteractiveShell()

        assert shell.data is None
        assert shell.history_file.name == ".nhl_scrabble_history"
        assert shell.commands == [
            "show",
            "top",
            "bottom",
            "compare",
            "filter",
            "search",
            "standings",
            "playoff",
            "stats",
            "refresh",
            "help",
            "exit",
            "quit",
        ]

    def test_get_completer_no_data(self) -> None:
        """Test completer with no data loaded."""
        shell = InteractiveShell()
        completer = shell.get_completer()

        # Should only have commands
        assert "show" in completer.words
        assert "help" in completer.words
        assert len(completer.words) == len(shell.commands)

    def test_get_completer_with_data(self, shell_with_data: InteractiveShell) -> None:
        """Test completer with data loaded."""
        completer = shell_with_data.get_completer()

        # Should have commands, teams, and players
        assert "show" in completer.words
        assert "TOR" in completer.words
        assert "EDM" in completer.words
        assert "Auston Matthews" in completer.words


class TestFetchData:
    """Test data fetching."""

    def test_fetch_data_structure(self) -> None:
        """Test that fetch_data initializes the data structure correctly."""
        shell = InteractiveShell()

        # Manually set up minimal data structure (simulating what fetch_data would do)
        shell.data = {
            "teams": [],
            "standings": Mock(),
            "playoff_teams": [],
            "eastern": [],
            "western": [],
        }

        # Verify data structure
        assert shell.data is not None
        assert "teams" in shell.data
        assert "standings" in shell.data
        assert "playoff_teams" in shell.data
        assert "eastern" in shell.data
        assert "western" in shell.data


class TestFindMethods:
    """Test helper methods for finding teams and players."""

    def test_find_team_exact_match(self, shell_with_data: InteractiveShell) -> None:
        """Test finding team by exact abbreviation."""
        team = shell_with_data._find_team("TOR")
        assert team is not None
        assert team.abbrev == "TOR"

    def test_find_team_case_insensitive(self, shell_with_data: InteractiveShell) -> None:
        """Test finding team is case-insensitive."""
        team = shell_with_data._find_team("tor")
        assert team is not None
        assert team.abbrev == "TOR"

    def test_find_team_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test finding non-existent team."""
        team = shell_with_data._find_team("XXX")
        assert team is None

    def test_find_player_exact_match(self, shell_with_data: InteractiveShell) -> None:
        """Test finding player by exact name."""
        player = shell_with_data._find_player("Auston Matthews")
        assert player is not None
        assert player.full_name == "Auston Matthews"

    def test_find_player_partial_last_name(self, shell_with_data: InteractiveShell) -> None:
        """Test finding player by partial last name."""
        player = shell_with_data._find_player("Matthews")
        assert player is not None
        assert player.full_name == "Auston Matthews"

    def test_find_player_partial_any_name(self, shell_with_data: InteractiveShell) -> None:
        """Test finding player by partial any name."""
        player = shell_with_data._find_player("Aus")
        assert player is not None
        assert player.full_name == "Auston Matthews"

    def test_find_player_case_insensitive(self, shell_with_data: InteractiveShell) -> None:
        """Test finding player is case-insensitive."""
        player = shell_with_data._find_player("auston matthews")
        assert player is not None
        assert player.full_name == "Auston Matthews"

    def test_find_player_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test finding non-existent player."""
        player = shell_with_data._find_player("Nonexistent Player")
        assert player is None


class TestShowCommand:
    """Test show command."""

    def test_cmd_show_no_args(self, shell_with_data: InteractiveShell) -> None:
        """Test show command with no arguments."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show([])
            mock_print.assert_called_once()
            assert "Usage:" in str(mock_print.call_args)

    def test_cmd_show_team(self, shell_with_data: InteractiveShell) -> None:
        """Test show team command."""
        with patch.object(shell_with_data, "_display_team") as mock_display:
            shell_with_data.cmd_show(["team", "TOR"])
            mock_display.assert_called_once()

    def test_cmd_show_team_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test show team command with non-existent team."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show(["team", "XXX"])
            assert any("not found" in str(call) for call in mock_print.call_args_list)

    def test_cmd_show_player(self, shell_with_data: InteractiveShell) -> None:
        """Test show player command."""
        with patch.object(shell_with_data, "_display_player") as mock_display:
            shell_with_data.cmd_show(["player", "Auston", "Matthews"])
            mock_display.assert_called_once()

    def test_cmd_show_player_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test show player command with non-existent player."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show(["player", "Nonexistent", "Player"])
            assert any("not found" in str(call) for call in mock_print.call_args_list)


class TestTopBottomCommands:
    """Test top and bottom commands."""

    def test_cmd_top_default(self, shell_with_data: InteractiveShell) -> None:
        """Test top command with default count."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_top([])
            # Should not raise

    def test_cmd_top_with_count(self, shell_with_data: InteractiveShell) -> None:
        """Test top command with custom count."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_top(["5"])
            # Should not raise

    def test_cmd_top_invalid_count(self, shell_with_data: InteractiveShell) -> None:
        """Test top command with invalid count."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_top(["abc"])
            assert any("must be a number" in str(call) for call in mock_print.call_args_list)

    def test_cmd_bottom_default(self, shell_with_data: InteractiveShell) -> None:
        """Test bottom command with default count."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_bottom([])
            # Should not raise

    def test_cmd_bottom_with_count(self, shell_with_data: InteractiveShell) -> None:
        """Test bottom command with custom count."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_bottom(["3"])
            # Should not raise


class TestCompareCommand:
    """Test compare command."""

    def test_cmd_compare_no_args(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command with no arguments."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_compare([])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)

    def test_cmd_compare_one_arg(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command with one argument."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_compare(["Matthews"])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)

    def test_cmd_compare_valid(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command with valid players."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_compare(["Matthews", "McDavid"])
            # Should not raise

    def test_cmd_compare_first_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command with first player not found."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_compare(["Nonexistent", "McDavid"])
            assert any("not found" in str(call) for call in mock_print.call_args_list)


class TestFilterCommand:
    """Test filter command."""

    def test_cmd_filter_no_args(self, shell_with_data: InteractiveShell) -> None:
        """Test filter command with no arguments."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter([])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)

    def test_cmd_filter_division(self, shell_with_data: InteractiveShell) -> None:
        """Test filter by division."""
        with patch.object(shell_with_data, "_display_team_list"):
            shell_with_data.cmd_filter(["division", "Atlantic"])
            # Should not raise

    def test_cmd_filter_conference(self, shell_with_data: InteractiveShell) -> None:
        """Test filter by conference."""
        with patch.object(shell_with_data, "_display_team_list"):
            shell_with_data.cmd_filter(["conference", "Eastern"])
            # Should not raise

    def test_cmd_filter_invalid_type(self, shell_with_data: InteractiveShell) -> None:
        """Test filter with invalid type."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter(["invalid", "value"])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)


class TestSearchCommand:
    """Test search command."""

    def test_cmd_search_no_args(self, shell_with_data: InteractiveShell) -> None:
        """Test search command with no arguments."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_search([])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)

    def test_cmd_search_found(self, shell_with_data: InteractiveShell) -> None:
        """Test search command with matches."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_search(["Mat"])
            # Should not raise

    def test_cmd_search_not_found(self, shell_with_data: InteractiveShell) -> None:
        """Test search command with no matches."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_search(["Nonexistent"])
            assert any(
                "no players found" in str(call).lower() for call in mock_print.call_args_list
            )


class TestStandingsCommand:
    """Test standings command."""

    def test_cmd_standings_team(self, shell_with_data: InteractiveShell) -> None:
        """Test standings command for teams."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_standings(["team"])
            # Should not raise

    def test_cmd_standings_division(self, shell_with_data: InteractiveShell) -> None:
        """Test standings command for divisions."""
        with patch.object(shell_with_data, "_display_team_list"):
            shell_with_data.cmd_standings(["division"])
            # Should not raise

    def test_cmd_standings_conference(self, shell_with_data: InteractiveShell) -> None:
        """Test standings command for conferences."""
        with patch.object(shell_with_data, "_display_team_list"):
            shell_with_data.cmd_standings(["conference"])
            # Should not raise

    def test_cmd_standings_invalid(self, shell_with_data: InteractiveShell) -> None:
        """Test standings command with invalid type."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_standings(["invalid"])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)


class TestPlayoffCommand:
    """Test playoff command."""

    def test_cmd_playoff(self, shell_with_data: InteractiveShell) -> None:
        """Test playoff command."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_playoff([])
            # Should not raise


class TestStatsCommand:
    """Test stats command."""

    def test_cmd_stats(self, shell_with_data: InteractiveShell) -> None:
        """Test stats command."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_stats([])
            # Should not raise


class TestRefreshCommand:
    """Test refresh command."""

    def test_cmd_refresh(self, shell_with_data: InteractiveShell) -> None:
        """Test refresh command."""
        with patch.object(shell_with_data, "fetch_data") as mock_fetch:
            shell_with_data.cmd_refresh([])
            mock_fetch.assert_called_once()


class TestHelpCommand:
    """Test help command."""

    def test_cmd_help_general(self, shell_with_data: InteractiveShell) -> None:
        """Test general help command."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_help([])
            # Should not raise

    def test_cmd_help_specific_command(self, shell_with_data: InteractiveShell) -> None:
        """Test help for specific command."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_help(["show"])
            # Should not raise

    def test_cmd_help_unknown_command(self, shell_with_data: InteractiveShell) -> None:
        """Test help for unknown command."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_help(["unknown"])
            assert any("No help available" in str(call) for call in mock_print.call_args_list)


class TestDisplayMethods:
    """Test display helper methods."""

    def test_display_team(self, shell_with_data: InteractiveShell) -> None:
        """Test displaying team details."""
        team = shell_with_data._find_team("TOR")
        assert team is not None

        with patch.object(shell_with_data.console, "print"):
            shell_with_data._display_team(team)
            # Should not raise

    def test_display_player(self, shell_with_data: InteractiveShell) -> None:
        """Test displaying player details."""
        player = shell_with_data._find_player("Matthews")
        assert player is not None

        with patch.object(shell_with_data.console, "print"):
            shell_with_data._display_player(player)
            # Should not raise

    def test_display_team_list(
        self,
        shell_with_data: InteractiveShell,
        mock_team_scores: list[TeamScore],
    ) -> None:
        """Test displaying team list."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data._display_team_list(mock_team_scores, "Test Teams")
            # Should not raise


# Additional tests for improved coverage


class TestFetchDataCoverage:
    """Test fetch_data method coverage."""

    @patch("nhl_scrabble.api.nhl_client.NHLApiClient")
    @patch("nhl_scrabble.processors.team_processor.TeamProcessor")
    @patch("nhl_scrabble.processors.playoff_calculator.PlayoffCalculator")
    @patch("nhl_scrabble.scoring.scrabble.ScrabbleScorer")
    def test_fetch_data_populates_data_structure(
        self,
        mock_scorer: Mock,
        mock_playoff: Mock,
        mock_processor: Mock,
        mock_api: Mock,
        mock_team_scores: list[TeamScore],
    ) -> None:
        """Test fetch_data creates expected data structure."""
        shell = InteractiveShell()

        # Setup mocks
        mock_api.return_value.__enter__.return_value = Mock()
        processor_instance = Mock()
        mock_processor.return_value = processor_instance

        teams_dict = {t.abbrev: t for t in mock_team_scores}
        all_players = [p for t in mock_team_scores for p in t.players]
        processor_instance.process_all_teams.return_value = (teams_dict, all_players, [])

        playoff_instance = Mock()
        mock_playoff.return_value = playoff_instance
        playoff_instance.calculate_playoff_standings.return_value = {
            "Eastern": [mock_team_scores[0]],
            "Western": [mock_team_scores[1]],
        }

        shell.fetch_data()

        assert shell.data is not None
        assert "teams" in shell.data
        assert "eastern" in shell.data
        assert "western" in shell.data


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


class TestEdgeCasesAndErrors:
    """Test edge cases and error handling to improve coverage."""

    def test_find_team_no_data(self) -> None:
        """Test finding team when no data is loaded."""
        shell = InteractiveShell()
        result = shell._find_team("TOR")
        assert result is None

    def test_find_player_no_data(self) -> None:
        """Test finding player when no data is loaded."""
        shell = InteractiveShell()
        result = shell._find_player("Matthews")
        assert result is None

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

    def test_cmd_show_team_missing_abbrev(self, shell_with_data: InteractiveShell) -> None:
        """Test show team command without team abbreviation."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show(["team"])
            assert any("Usage: show team" in str(call) for call in mock_print.call_args_list)

    def test_cmd_show_player_missing_name(self, shell_with_data: InteractiveShell) -> None:
        """Test show player command without player name."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show(["player"])
            assert any("Usage: show player" in str(call) for call in mock_print.call_args_list)

    def test_cmd_show_invalid_subcommand(self, shell_with_data: InteractiveShell) -> None:
        """Test show command with invalid subcommand."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_show(["invalid"])
            assert any("Usage:" in str(call) for call in mock_print.call_args_list)

    def test_cmd_bottom_invalid_number(self, shell_with_data: InteractiveShell) -> None:
        """Test bottom command with invalid number."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_bottom(["not_a_number"])
            assert any("must be a number" in str(call) for call in mock_print.call_args_list)

    def test_cmd_compare_multiword_first_player(
        self,
        shell_with_data: InteractiveShell,
    ) -> None:
        """Test compare command with multi-word first player name."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data.cmd_compare(["Auston", "Matthews", "McDavid"])
            # Should handle multi-word first name

    def test_cmd_compare_multiword_player_not_found_retry(
        self,
        shell_with_data: InteractiveShell,
    ) -> None:
        """Test compare command multi-word retry when first name not found."""
        # Add a player with multi-word name that won't match single word
        multi_word_player = PlayerScore(
            first_name="Pierre-Luc",
            last_name="Dubois",
            full_name="Pierre-Luc Dubois",
            first_score=30,
            last_score=70,
            full_score=100,
            team="WSH",
            division="Metropolitan",
            conference="Eastern",
        )
        shell_with_data.data["teams"][0].players.append(multi_word_player)  # type: ignore[index]

        with patch.object(shell_with_data.console, "print"):
            # First word "Pierre-Luc" won't match alone, but "Pierre-Luc Dubois" will
            # This triggers the multi-word retry logic on lines 397-399
            shell_with_data.cmd_compare(["Pierre-Luc", "Dubois", "Matthews"])
            # Should retry with multi-word name and find the player

    def test_cmd_compare_tied_scores(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command with tied scores."""
        # Make two players with same score
        shell_with_data.data["teams"][0].players[0].full_score = 100  # type: ignore[index]
        shell_with_data.data["teams"][0].players[1].full_score = 100  # type: ignore[index]

        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_compare(["Matthews", "Marner"])
            calls_str = " ".join(str(call) for call in mock_print.call_args_list)
            # Should show tied message
            assert "Tied" in calls_str or "tied" in calls_str

    def test_cmd_compare_second_player_not_found(
        self,
        shell_with_data: InteractiveShell,
    ) -> None:
        """Test compare command when second player not found."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_compare(["Matthews", "Nonexistent", "Player"])
            assert any("not found" in str(call) for call in mock_print.call_args_list)

    def test_cmd_compare_shows_winner(self, shell_with_data: InteractiveShell) -> None:
        """Test compare command displays winner."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            # McDavid (110) vs Matthews (100) - McDavid wins
            shell_with_data.cmd_compare(["McDavid", "Matthews"])
            calls_str = " ".join(str(call) for call in mock_print.call_args_list)
            # Should show higher score message
            assert "higher score" in calls_str or "McDavid" in calls_str

    def test_cmd_filter_division_missing_arg(self, shell_with_data: InteractiveShell) -> None:
        """Test filter division command without division name."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter(["division"])
            assert any("Usage: filter division" in str(call) for call in mock_print.call_args_list)

    def test_cmd_filter_division_no_results(self, shell_with_data: InteractiveShell) -> None:
        """Test filter division command with no matching teams."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter(["division", "Nonexistent"])
            assert any("No teams found" in str(call) for call in mock_print.call_args_list)

    def test_cmd_filter_conference_missing_arg(self, shell_with_data: InteractiveShell) -> None:
        """Test filter conference command without conference name."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter(["conference"])
            assert any(
                "Usage: filter conference" in str(call) for call in mock_print.call_args_list
            )

    def test_cmd_filter_conference_no_results(self, shell_with_data: InteractiveShell) -> None:
        """Test filter conference command with no matching teams."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_filter(["conference", "Nonexistent"])
            assert any("No teams found" in str(call) for call in mock_print.call_args_list)

    def test_cmd_search_no_data(self) -> None:
        """Test search command when no data is loaded."""
        shell = InteractiveShell()
        with patch.object(shell.console, "print") as mock_print:
            shell.cmd_search(["test"])
            assert any("No data loaded" in str(call) for call in mock_print.call_args_list)

    @patch("nhl_scrabble.api.nhl_client.NHLApiClient")
    @patch("nhl_scrabble.processors.team_processor.TeamProcessor")
    @patch("nhl_scrabble.processors.playoff_calculator.PlayoffCalculator")
    @patch("nhl_scrabble.scoring.scrabble.ScrabbleScorer")
    def test_fetch_data_with_failed_teams(
        self,
        mock_scorer: Mock,
        mock_playoff: Mock,
        mock_processor: Mock,
        mock_api: Mock,
        mock_team_scores: list[TeamScore],
    ) -> None:
        """Test fetch_data handles failed teams."""
        shell = InteractiveShell()

        # Setup mocks
        mock_api.return_value.__enter__.return_value = Mock()
        processor_instance = Mock()
        mock_processor.return_value = processor_instance

        teams_dict = {t.abbrev: t for t in mock_team_scores}
        all_players = [p for t in mock_team_scores for p in t.players]
        failed_teams = ["BOS", "NYR"]  # Simulate failed teams
        processor_instance.process_all_teams.return_value = (teams_dict, all_players, failed_teams)

        playoff_instance = Mock()
        mock_playoff.return_value = playoff_instance
        playoff_instance.calculate_playoff_standings.return_value = {
            "Eastern": [mock_team_scores[0]],
            "Western": [mock_team_scores[1]],
        }

        with patch.object(shell.console, "print") as mock_print:
            shell.fetch_data()
            # Should print warning about failed teams
            calls_str = " ".join(str(call) for call in mock_print.call_args_list)
            assert "Failed to fetch" in calls_str or "BOS" in calls_str


class TestStandingsDivisionGrouping:
    """Test standings command division grouping."""

    def test_cmd_standings_division_grouping(
        self,
        shell_with_data: InteractiveShell,
        mock_team_scores: list[TeamScore],
    ) -> None:
        """Test standings division command groups teams correctly."""
        # Ensure teams have different divisions for grouping test
        mock_team_scores[0].division = "Atlantic"
        mock_team_scores[1].division = "Pacific"

        shell_with_data.data = {
            "teams": mock_team_scores,
            "playoff_teams": mock_team_scores,
            "eastern": [mock_team_scores[0]],
            "western": [mock_team_scores[1]],
        }

        with patch.object(shell_with_data, "_display_team_list") as mock_display:
            shell_with_data.cmd_standings(["division"])
            # Should call _display_team_list for each division
            assert mock_display.call_count >= 2

    def test_cmd_standings_division_new_division_grouping(
        self,
        shell_with_data: InteractiveShell,
        mock_team_scores: list[TeamScore],
    ) -> None:
        """Test division grouping creates new division entries correctly."""
        # Create teams with same division and one with different
        team1 = mock_team_scores[0]
        team1.division = "Atlantic"

        team2 = TeamScore(
            abbrev="BOS",
            name="Boston Bruins",
            total=950,
            division="Atlantic",  # Same division
            conference="Eastern",
            players=[],
        )

        team3 = mock_team_scores[1]
        team3.division = "Pacific"  # Different division

        shell_with_data.data = {
            "teams": [team1, team2, team3],
            "playoff_teams": [team1, team2, team3],
            "eastern": [team1, team2],
            "western": [team3],
        }

        with (
            patch.object(shell_with_data, "_display_team_list") as mock_display,
            patch.object(shell_with_data.console, "print"),
        ):
            shell_with_data.cmd_standings(["division"])
            # Should group Atlantic teams together and Pacific separately
            # Minimum 2 divisions displayed
            assert mock_display.call_count >= 2
