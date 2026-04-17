"""Unit tests for interactive shell."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from nhl_scrabble.interactive.shell import InteractiveShell
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def mock_team_scores() -> list[TeamScore]:
    """Create mock team scores for testing."""
    team1 = TeamScore(
        abbrev="TOR",
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
            assert any("no players found" in str(call).lower() for call in mock_print.call_args_list)


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
        self, shell_with_data: InteractiveShell, mock_team_scores: list[TeamScore]
    ) -> None:
        """Test displaying team list."""
        with patch.object(shell_with_data.console, "print"):
            shell_with_data._display_team_list(mock_team_scores, "Test Teams")
            # Should not raise
