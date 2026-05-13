"""Tests for advanced interactive shell commands (standings, playoff, stats, refresh, help)."""

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
