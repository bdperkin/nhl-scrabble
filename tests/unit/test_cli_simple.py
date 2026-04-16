"""Simplified unit tests for CLI module to improve coverage."""

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self) -> None:
        """Test that CLI help displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Scrabble" in result.output

    def test_cli_version(self) -> None:
        """Test that CLI version flag works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0

    def test_analyze_help(self) -> None:
        """Test that analyze command help displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
        assert "--format" in result.output
        assert "--output" in result.output
        assert "--verbose" in result.output
