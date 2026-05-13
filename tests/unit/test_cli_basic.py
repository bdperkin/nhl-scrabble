"""Basic CLI functionality tests (version, help, basic analyze options)."""

import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli


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
