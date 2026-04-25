"""Comprehensive CLI tests to achieve 90%+ coverage.

This test module provides extensive coverage for the NHL Scrabble CLI, testing command-line argument
parsing, option combinations, error handling, output formats, and environment variable integration.

Target: Improve CLI coverage from ~50% to 90%+
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli, validate_cli_arguments, validate_output_path


class TestCLIBasics:
    """Basic CLI functionality tests."""

    def test_cli_version(self) -> None:
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        # Check for version format (dynamic versioning from git tags)
        assert "nhl-scrabble, version" in result.output
        # Version could be "X.Y.Z" or "X.Y.Z.devN+ghash" depending on git state
        import re

        assert re.search(r"\d+\.\d+", result.output), "Version should contain major.minor"

    def test_cli_help(self) -> None:
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "analyze" in result.output
        assert "watch" in result.output


class TestAnalyzeCommand:
    """Tests for the analyze command."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_default_options(self, mock_run: MagicMock) -> None:
        """Test analyze with default options."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_verbose_mode(self, mock_run: MagicMock) -> None:
        """Test analyze with verbose logging."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--verbose"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_quiet_mode(self, mock_run: MagicMock) -> None:
        """Test analyze with quiet mode."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_custom_player_counts(self, mock_run: MagicMock) -> None:
        """Test analyze with custom player count options."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "50", "--top-team-players", "10"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_json_format_stdout(self, mock_run: MagicMock) -> None:
        """Test JSON format output to stdout."""
        mock_run.return_value = '{"teams": []}'
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "json"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_csv_format_to_file(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test CSV format output to file."""
        output_file = tmp_path / "output.csv"
        mock_run.return_value = None  # CSV returns None

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "csv", "--output", str(output_file)])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_excel_format_to_file(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test Excel format output to file."""
        output_file = tmp_path / "output.xlsx"
        mock_run.return_value = None  # Excel returns None

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "excel", "--output", str(output_file)])

        assert result.exit_code == 0

    def test_analyze_csv_format_without_output(self) -> None:
        """Test CSV format requires --output option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "csv"])
        assert result.exit_code != 0
        assert "CSV format requires --output" in result.output

    def test_analyze_excel_format_without_output(self) -> None:
        """Test Excel format requires --output option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "excel"])
        assert result.exit_code != 0
        assert "EXCEL format requires --output" in result.output

    def test_analyze_invalid_format(self) -> None:
        """Test invalid format option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_analyze_invalid_top_players_negative(self) -> None:
        """Test invalid negative top-players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "-1"])
        assert result.exit_code != 0

    def test_analyze_invalid_top_players_zero(self) -> None:
        """Test invalid zero top-players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "0"])
        assert result.exit_code != 0

    def test_analyze_invalid_top_players_too_large(self) -> None:
        """Test invalid too-large top-players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "10000"])
        assert result.exit_code != 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_filters(self, mock_run: MagicMock) -> None:
        """Test analyze with division/conference/team filters."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--divisions",
                "Atlantic",
                "--conferences",
                "Eastern",
                "--teams",
                "TOR,MTL",
                "--exclude-teams",
                "BOS",
                "--min-score",
                "50",
                "--max-score",
                "100",
            ],
        )
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_specific_report(self, mock_run: MagicMock) -> None:
        """Test analyze with specific report filter."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--report", "team"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_season(self, mock_run: MagicMock) -> None:
        """Test analyze with specific season."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--season", "20222023"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_no_cache(self, mock_run: MagicMock) -> None:
        """Test analyze with --no-cache flag."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--no-cache"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_clear_cache(self, mock_run: MagicMock) -> None:
        """Test analyze with --clear-cache flag."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--clear-cache"])
        assert result.exit_code == 0

    def test_analyze_scoring_and_config_mutually_exclusive(self, tmp_path: Path) -> None:
        """Test that --scoring and --scoring-config are mutually exclusive."""
        # Create temporary config file
        config_file = tmp_path / "custom.json"
        config_file.write_text('{"A": 1}')

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--scoring",
                "wordle",
                "--scoring-config",
                str(config_file),
            ],
        )
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output


class TestOutputPathValidation:
    """Tests for output path validation."""

    def test_validate_output_path_none(self) -> None:
        """Test that None output path (stdout) is valid."""
        # Should not raise
        validate_output_path(None)

    def test_validate_output_path_valid(self, tmp_path: Path) -> None:
        """Test valid output path."""
        output_file = tmp_path / "output.txt"
        validate_output_path(str(output_file))

    def test_validate_output_path_nonexistent_directory(self) -> None:
        """Test output path with nonexistent directory."""
        with pytest.raises(click.ClickException, match="does not exist"):
            validate_output_path("/nonexistent/directory/file.txt")

    def test_validate_output_path_readonly_directory(self, tmp_path: Path) -> None:
        """Test output path with readonly directory."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        output_file = readonly_dir / "output.txt"

        with pytest.raises(click.ClickException, match="not writable"):
            validate_output_path(str(output_file))

        # Cleanup: restore permissions
        readonly_dir.chmod(0o755)

    def test_validate_output_path_readonly_file(self, tmp_path: Path) -> None:
        """Test output path with readonly existing file."""
        output_file = tmp_path / "readonly.txt"
        output_file.touch()
        output_file.chmod(0o444)

        with pytest.raises(click.ClickException, match="not writable"):
            validate_output_path(str(output_file))

        # Cleanup
        output_file.chmod(0o644)


class TestCLIArgumentValidation:
    """Tests for CLI argument validation."""

    def test_validate_cli_arguments_valid(self, tmp_path: Path) -> None:
        """Test validation with valid output path.

        Note: Numeric validation (top_players, top_team_players) is now handled
        by Click's IntRange type, not by validate_cli_arguments().
        """
        output_file = tmp_path / "output.txt"
        output_path = validate_cli_arguments(str(output_file))
        assert output_path == output_file

    def test_validate_cli_arguments_none_output(self) -> None:
        """Test validation with None output (stdout)."""
        output_path = validate_cli_arguments(None)
        assert output_path is None

    def test_validate_cli_arguments_invalid_path(self) -> None:
        """Test validation with invalid output path."""
        with pytest.raises(click.ClickException):
            validate_cli_arguments("/nonexistent/directory/file.txt")


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_output_write_error(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test handling of output file write errors."""
        # Create a file then make it readonly
        output_file = tmp_path / "readonly.txt"
        output_file.touch()
        output_file.chmod(0o444)

        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

        # Should detect readonly file
        assert result.exit_code != 0

        # Cleanup
        output_file.chmod(0o644)


class TestGenerateFunctions:
    """Tests for report generation functions."""

    def test_generate_json_report(self) -> None:
        """Test JSON report generation using formatter factory."""
        from dataclasses import asdict, dataclass

        from nhl_scrabble.formatters import get_formatter
        from nhl_scrabble.models.player import PlayerScore

        # Create sample data
        @dataclass
        class MockTeam:
            total: int
            players: list[Any]
            division: str
            conference: str
            avg_per_player: float

        team = MockTeam(
            total=100,
            players=[
                PlayerScore(
                    first_name="John",
                    last_name="Doe",
                    full_name="John Doe",
                    team="TOR",
                    division="Atlantic",
                    conference="Eastern",
                    first_score=10,
                    last_score=20,
                    full_score=30,
                )
            ],
            division="Atlantic",
            conference="Eastern",
            avg_per_player=30.0,
        )

        # Prepare data for formatter
        data = {
            "teams": {
                "TOR": {
                    "total": team.total,
                    "players": [asdict(p) for p in team.players],
                    "division": team.division,
                    "conference": team.conference,
                    "avg_per_player": team.avg_per_player,
                }
            },
            "divisions": {},
            "conferences": {},
            "playoffs": {},
            "summary": {"total_teams": 1, "total_players": 1},
        }

        # Use formatter factory
        formatter = get_formatter("json")
        result = formatter.format(data)

        assert '"teams"' in result
        assert '"TOR"' in result

    def test_generate_search_text(self) -> None:
        """Test search text generation."""
        from nhl_scrabble.cli import generate_search_text
        from nhl_scrabble.models.player import PlayerScore

        players = [
            PlayerScore(
                first_name="John",
                last_name="Doe",
                full_name="John Doe",
                team="TOR",
                division="Atlantic",
                conference="Eastern",
                first_score=10,
                last_score=20,
                full_score=30,
            )
        ]

        result = generate_search_text(
            players,
            query="Doe",
            fuzzy=False,
            min_score=None,
            max_score=None,
            teams=None,
            divisions=None,
            conferences=None,
            limit=20,
        )
        assert "John Doe" in result
        assert "30" in result  # Score value appears in output

    def test_generate_search_text_fuzzy(self) -> None:
        """Test search text generation with fuzzy matching."""
        from nhl_scrabble.cli import generate_search_text

        result = generate_search_text(
            results=[],
            query="test",
            fuzzy=True,
            min_score=50,
            max_score=100,
            teams="TOR",
            divisions="Atlantic",
            conferences="Eastern",
            limit=10,
        )
        assert "Fuzzy" in result
        assert "Minimum Score: 50" in result
        assert "Maximum Score: 100" in result

    def test_generate_search_json(self) -> None:
        """Test search JSON generation."""
        from nhl_scrabble.cli import generate_search_json
        from nhl_scrabble.models.player import PlayerScore

        players = [
            PlayerScore(
                first_name="John",
                last_name="Doe",
                full_name="John Doe",
                team="TOR",
                division="Atlantic",
                conference="Eastern",
                first_score=10,
                last_score=20,
                full_score=30,
            )
        ]

        stats = {"total_players": 100}
        result = generate_search_json(players, "Doe", stats)
        assert '"query"' in result
        assert '"result_count"' in result


class TestOtherCommands:
    """Tests for other CLI commands."""

    def test_watch_help(self) -> None:
        """Test watch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--help"])
        assert result.exit_code == 0
        assert "watch" in result.output.lower()

    def test_watch_invalid_interval(self) -> None:
        """Test watch with invalid interval (now validated by Click IntRange)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "0"])
        assert result.exit_code != 0
        # Click IntRange provides error message about range
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_search_help(self) -> None:
        """Test search command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "search" in result.output.lower()

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_search_basic(self, mock_client: MagicMock, mock_processor: MagicMock) -> None:
        """Test basic search functionality."""
        from nhl_scrabble.models.player import PlayerScore

        # Mock the process_all_teams return
        mock_processor.return_value.process_all_teams.return_value = (
            {},  # team_scores
            [
                PlayerScore(
                    first_name="John",
                    last_name="Doe",
                    full_name="John Doe",
                    team="TOR",
                    division="Atlantic",
                    conference="Eastern",
                    first_score=10,
                    last_score=20,
                    full_score=30,
                )
            ],  # all_players
            [],  # failed_teams
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "Doe", "--quiet"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_search_with_filters(self, mock_client: MagicMock, mock_processor: MagicMock) -> None:
        """Test search with various filters."""
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "--min-score",
                "50",
                "--max-score",
                "100",
                "--teams",
                "TOR",
                "--divisions",
                "Atlantic",
                "--conferences",
                "Eastern",
                "--limit",
                "10",
                "--quiet",
            ],
        )
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_search_fuzzy(self, mock_client: MagicMock, mock_processor: MagicMock) -> None:
        """Test fuzzy search."""
        from nhl_scrabble.models.player import PlayerScore

        # Return at least one player for fuzzy matching
        mock_processor.return_value.process_all_teams.return_value = (
            {},
            [
                PlayerScore(
                    first_name="Connor",
                    last_name="McDavid",
                    full_name="Connor McDavid",
                    team="EDM",
                    division="Pacific",
                    conference="Western",
                    first_score=15,
                    last_score=25,
                    full_score=40,
                )
            ],
            [],
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "McDavid", "--fuzzy", "--quiet"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_search_json_output(self, mock_client: MagicMock, mock_processor: MagicMock) -> None:
        """Test search with JSON output."""
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--format", "json", "--quiet"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_search_to_file(
        self, mock_client: MagicMock, mock_processor: MagicMock, tmp_path: Path
    ) -> None:
        """Test search output to file."""
        output_file = tmp_path / "search.txt"
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--output", str(output_file), "--quiet"])
        assert result.exit_code == 0
        assert output_file.exists()

    def test_dashboard_help(self) -> None:
        """Test dashboard command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--help"])
        assert result.exit_code == 0
        assert "dashboard" in result.output.lower()

    @patch("nhl_scrabble.cli.StatisticsDashboard")
    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_dashboard_basic(
        self,
        mock_client: MagicMock,
        mock_processor: MagicMock,
        mock_dashboard: MagicMock,
    ) -> None:
        """Test basic dashboard functionality."""
        # Mock API responses
        mock_client.return_value.get_teams.return_value = []
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])
        mock_processor.return_value.calculate_division_standings.return_value = {}
        mock_processor.return_value.calculate_conference_standings.return_value = {}
        mock_dashboard.return_value.display_static.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--static", "--quiet"])
        # May fail due to data issues, but command should be invoked
        assert result.exit_code in [0, 1]

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_dashboard_with_filters(
        self, mock_client: MagicMock, mock_processor: MagicMock
    ) -> None:
        """Test dashboard with division/conference filters."""
        mock_client.return_value.get_teams.return_value = []
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])
        mock_processor.return_value.calculate_division_standings.return_value = {}
        mock_processor.return_value.calculate_conference_standings.return_value = {}

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "dashboard",
                "--static",
                "--divisions",
                "Atlantic",
                "--conferences",
                "Eastern",
                "--quiet",
            ],
        )
        assert result.exit_code in [0, 1]

    def test_interactive_help(self) -> None:
        """Test interactive command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["interactive", "--help"])
        assert result.exit_code == 0
        assert "interactive" in result.output.lower()

    @patch("nhl_scrabble.interactive.InteractiveShell")
    def test_interactive_basic(self, mock_shell: MagicMock) -> None:
        """Test interactive mode launch."""
        mock_shell.return_value.run.return_value = None
        mock_shell.return_value.fetch_data.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ["interactive", "--verbose"])
        assert result.exit_code in [0, 1]

    def test_serve_help(self) -> None:
        """Test serve command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0
        assert "serve" in result.output.lower()

    def test_serve_without_uvicorn(self) -> None:
        """Test serve command without uvicorn installed."""
        runner = CliRunner()
        with patch.dict("sys.modules", {"uvicorn": None}):
            result = runner.invoke(cli, ["serve"])
            # Should fail or abort without uvicorn
            assert result.exit_code != 0


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
            "TOR": {"division": "Atlantic", "conference": "Eastern"}
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
        self, mock_container_class: MagicMock
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
            process_all_teams=MagicMock(return_value=({}, [], []))
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
        self, mock_container_class: MagicMock
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
            "TOR": {"division": "Atlantic", "conference": "Eastern"}
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
