"""Comprehensive unit tests for CLI analyze command.

This module tests the analyze command's option validation, error handling,
and various execution paths to improve coverage.

Target: Improve coverage of analyze command (lines 566-900+)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestAnalyzeCommandValidation:
    """Test analyze command option validation."""

    def test_analyze_scoring_options_mutually_exclusive(self, tmp_path: Path) -> None:
        """Test that --scoring and --scoring-config are mutually exclusive."""
        scoring_config = tmp_path / "scoring.json"
        scoring_config.write_text('{"A": 1}')

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["analyze", "--scoring", "wordle", "--scoring-config", str(scoring_config)],
        )

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()

    def test_analyze_csv_requires_output(self) -> None:
        """Test that CSV format requires --output option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "csv"])

        assert result.exit_code != 0
        assert (
            "requires --output" in result.output.lower()
            or "requires output" in result.output.lower()
        )

    def test_analyze_excel_requires_output(self) -> None:
        """Test that Excel format requires --output option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "excel"])

        assert result.exit_code != 0
        assert (
            "requires --output" in result.output.lower()
            or "requires output" in result.output.lower()
        )

    def test_analyze_template_requires_template_file(self) -> None:
        """Test that template format requires --template option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "template"])

        assert result.exit_code != 0
        assert "requires --template" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    @patch("nhl_scrabble.cli.ScoringConfig")
    def test_analyze_with_custom_scoring_config(
        self,
        mock_scoring_config: MagicMock,
        mock_run: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test analyze with custom scoring configuration file."""
        scoring_config = tmp_path / "scoring.json"
        scoring_config.write_text('{"A": 1, "B": 2}')

        # Mock ScoringConfig.load_from_file to return valid config
        mock_scoring_config.load_from_file.return_value = {"A": 1, "B": 2}
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--scoring-config", str(scoring_config)])

        assert result.exit_code == 0
        assert mock_run.called

    def test_analyze_with_invalid_scoring_config(self, tmp_path: Path) -> None:
        """Test analyze with invalid scoring config file."""
        scoring_config = tmp_path / "invalid.json"
        scoring_config.write_text("not valid json")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--scoring-config", str(scoring_config)])

        assert result.exit_code != 0
        assert "error" in result.output.lower()

    def test_analyze_with_nonexistent_scoring_config(self) -> None:
        """Test analyze with nonexistent scoring config file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--scoring-config", "/nonexistent/file.json"])

        # Click validates path existence
        assert result.exit_code != 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_wordle_scoring(self, mock_run: MagicMock) -> None:
        """Test analyze with built-in wordle scoring system."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--scoring", "wordle"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_uniform_scoring(self, mock_run: MagicMock) -> None:
        """Test analyze with built-in uniform scoring system."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--scoring", "uniform"])

        assert result.exit_code == 0
        assert mock_run.called


class TestAnalyzeCommandOptions:
    """Test analyze command various options."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_locale_option(self, mock_run: MagicMock) -> None:
        """Test analyze with locale option."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--locale", "fr_CA"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_divisions_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with divisions filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--divisions", "Atlantic,Metropolitan"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_conferences_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with conferences filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--conferences", "Eastern"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_teams_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with teams filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--teams", "TOR,MTL,BOS"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_exclude_teams(self, mock_run: MagicMock) -> None:
        """Test analyze with exclude teams option."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--exclude-teams", "NYR,PHI"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_countries_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with countries filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--countries", "CAN,USA,SWE"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_positions_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with positions filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--positions", "C,L,R"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_min_max_score(self, mock_run: MagicMock) -> None:
        """Test analyze with min/max score filters."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--min-score", "50", "--max-score", "100"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_group_by(self, mock_run: MagicMock) -> None:
        """Test analyze with group-by option."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--group-by", "division"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_report_filter(self, mock_run: MagicMock) -> None:
        """Test analyze with specific report filter."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--report", "playoff"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_season(self, mock_run: MagicMock) -> None:
        """Test analyze with specific season."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--season", "20222023"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_top_players_custom(self, mock_run: MagicMock) -> None:
        """Test analyze with custom top players count."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "50"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_top_team_players_custom(self, mock_run: MagicMock) -> None:
        """Test analyze with custom top team players count."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "10"])

        assert result.exit_code == 0
        assert mock_run.called


class TestAnalyzeCommandOutputHandling:
    """Test analyze command output handling."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_output_file(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Test analyze writing to output file."""
        output_file = tmp_path / "output.txt"
        mock_run.return_value = "Test report"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Test report" in output_file.read_text()

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_invalid_output_path(self, mock_run: MagicMock) -> None:
        """Test analyze with invalid output path."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/output.txt"])

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "error" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_verbose_flag(self, mock_run: MagicMock) -> None:
        """Test analyze with verbose logging."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--verbose"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_quiet_flag(self, mock_run: MagicMock) -> None:
        """Test analyze with quiet mode."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_clear_cache_flag(self, mock_run: MagicMock) -> None:
        """Test analyze with clear cache flag."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--clear-cache"])

        assert result.exit_code == 0
        assert mock_run.called
        # Verify clear_cache was passed to run_analysis
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["clear_cache"] is True

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_with_no_cache_flag(self, mock_run: MagicMock) -> None:
        """Test analyze with no-cache flag."""
        mock_run.return_value = "Test output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--no-cache"])

        assert result.exit_code == 0
        assert mock_run.called


class TestAnalyzeCommandErrorHandling:
    """Test analyze command error handling."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_handles_api_error(self, mock_run: MagicMock) -> None:
        """Test analyze handles API errors gracefully."""
        from nhl_scrabble.api.nhl_client import NHLApiError

        mock_run.side_effect = NHLApiError("API unavailable")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        assert "error" in result.output.lower() or "api" in result.output.lower()

    @patch("nhl_scrabble.cli.run_analysis")
    def test_analyze_handles_generic_exception(self, mock_run: MagicMock) -> None:
        """Test analyze handles generic exceptions."""
        mock_run.side_effect = Exception("Unexpected error")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0

    def test_analyze_top_players_out_of_range(self) -> None:
        """Test analyze with top-players out of valid range."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "101"])

        # Click validates IntRange
        assert result.exit_code != 0

    def test_analyze_top_team_players_out_of_range(self) -> None:
        """Test analyze with top-team-players out of valid range."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "51"])

        # Click validates IntRange
        assert result.exit_code != 0
