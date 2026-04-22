"""Unit tests for CLI short options.

Tests verify that short options work correctly and provide same functionality as their long option
equivalents.
"""

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestShortOptions:
    """Tests for CLI short options."""

    def test_version_short_option(self) -> None:
        """Test -V shows version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["-V"])

        assert result.exit_code == 0
        assert "2.0.0" in result.output
        assert "nhl-scrabble" in result.output.lower()

    def test_version_long_option(self) -> None:
        """Test --version shows version (backwards compatibility)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "2.0.0" in result.output
        assert "nhl-scrabble" in result.output.lower()

    def test_version_options_equivalent(self) -> None:
        """Test -V and --version produce identical output."""
        runner = CliRunner()
        short_result = runner.invoke(cli, ["-V"])
        long_result = runner.invoke(cli, ["--version"])

        assert short_result.output == long_result.output

    def test_help_short_option_main(self) -> None:
        """Test -h shows help for main command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["-h"])

        assert result.exit_code == 0
        assert "NHL Roster Scrabble Score Analyzer" in result.output
        assert "-V, --version" in result.output
        assert "-h, --help" in result.output

    def test_help_long_option_main(self) -> None:
        """Test --help shows help for main command (backwards compatibility)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "NHL Roster Scrabble Score Analyzer" in result.output

    def test_help_options_equivalent_main(self) -> None:
        """Test -h and --help produce identical output for main command."""
        runner = CliRunner()
        short_result = runner.invoke(cli, ["-h"])
        long_result = runner.invoke(cli, ["--help"])

        assert short_result.output == long_result.output

    def test_analyze_help_short_option(self) -> None:
        """Test analyze -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "-h"])

        assert result.exit_code == 0
        assert "analyze" in result.output.lower()
        assert "-f, --format" in result.output
        assert "-o, --output" in result.output
        assert "-v, --verbose" in result.output
        assert "-h, --help" in result.output

    def test_analyze_help_options_equivalent(self) -> None:
        """Test analyze -h and --help produce identical output."""
        runner = CliRunner()
        short_result = runner.invoke(cli, ["analyze", "-h"])
        long_result = runner.invoke(cli, ["analyze", "--help"])

        assert short_result.output == long_result.output

    def test_analyze_format_short_option_shows_in_help(self) -> None:
        """Test -f, --format is shown in analyze help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "-f, --format" in result.output

    def test_watch_help_short_option(self) -> None:
        """Test watch -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "-h"])

        assert result.exit_code == 0
        assert "watch" in result.output.lower()
        assert "-f, --format" in result.output
        assert "-v, --verbose" in result.output
        assert "-h, --help" in result.output

    def test_watch_format_short_option_shows_in_help(self) -> None:
        """Test -f, --format is shown in watch help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--help"])

        assert result.exit_code == 0
        assert "-f, --format" in result.output

    def test_search_help_short_option(self) -> None:
        """Test search -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "-h"])

        assert result.exit_code == 0
        assert "search" in result.output.lower()
        assert "-f, --fuzzy" in result.output
        assert "-o, --output" in result.output
        assert "-v, --verbose" in result.output
        assert "-h, --help" in result.output

    def test_search_format_no_short_option(self) -> None:
        """Test search --format has NO short option (conflict with --fuzzy -f)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--help"])

        assert result.exit_code == 0
        # Should show --format WITHOUT -f prefix
        assert "--format" in result.output
        # Should show -f, --fuzzy (short option used for fuzzy)
        assert "-f, --fuzzy" in result.output

    def test_interactive_help_short_option(self) -> None:
        """Test interactive -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["interactive", "-h"])

        assert result.exit_code == 0
        assert "interactive" in result.output.lower()
        assert "-v, --verbose" in result.output
        assert "-h, --help" in result.output

    def test_serve_help_short_option(self) -> None:
        """Test serve -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "-h"])

        assert result.exit_code == 0
        assert "serve" in result.output.lower()
        assert "-h, --help" in result.output

    def test_dashboard_help_short_option(self) -> None:
        """Test dashboard -h shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "-h"])

        assert result.exit_code == 0
        assert "dashboard" in result.output.lower()
        assert "-v, --verbose" in result.output
        assert "-q, --quiet" in result.output
        assert "-h, --help" in result.output

    def test_verbose_short_option_exists(self) -> None:
        """Test -v, --verbose short option already existed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "-v, --verbose" in result.output

    def test_output_short_option_exists(self) -> None:
        """Test -o, --output short option already existed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "-o, --output" in result.output

    def test_quiet_short_option_exists(self) -> None:
        """Test -q, --quiet short option already existed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "-q, --quiet" in result.output
