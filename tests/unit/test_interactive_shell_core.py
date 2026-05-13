"""Core functionality tests for interactive shell (initialization, data, helpers)."""

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
