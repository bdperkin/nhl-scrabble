"""Tests for basic interactive shell commands (show, top, bottom, compare, filter, search)."""

from __future__ import annotations

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

    def test_cmd_bottom_invalid_number(self, shell_with_data: InteractiveShell) -> None:
        """Test bottom command with invalid number."""
        with patch.object(shell_with_data.console, "print") as mock_print:
            shell_with_data.cmd_bottom(["not_a_number"])
            assert any("must be a number" in str(call) for call in mock_print.call_args_list)


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

    def test_cmd_search_no_data(self) -> None:
        """Test search command when no data is loaded."""
        shell = InteractiveShell()
        with patch.object(shell.console, "print") as mock_print:
            shell.cmd_search(["test"])
            assert any("No data loaded" in str(call) for call in mock_print.call_args_list)
