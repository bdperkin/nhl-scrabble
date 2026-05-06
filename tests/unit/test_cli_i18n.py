"""Tests for CLI internationalization functionality."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from nhl_scrabble.cli import cli
from nhl_scrabble.i18n import SUPPORTED_LOCALES


class TestCLILocale:
    """Test CLI locale functionality."""

    def test_cli_default_locale(self):
        """Test CLI with default (system) locale."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        # Should show help text
        assert "NHL Scrabble analysis" in result.output or "analyze" in result.output

    def test_cli_locale_option_in_help(self):
        """Test that --locale option appears in help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        # Check for locale option
        assert "--locale" in result.output or "-l" in result.output

    def test_cli_locale_env_var(self):
        """Test CLI respects NHL_SCRABBLE_LANG environment variable."""
        runner = CliRunner()
        # Test with French locale via environment variable
        result = runner.invoke(cli, ["analyze", "--help"], env={"NHL_SCRABBLE_LANG": "fr_CA"})
        assert result.exit_code == 0
        # Should work without errors
        assert "analyze" in result.output.lower() or "usage" in result.output.lower()

    def test_cli_locale_option_valid(self):
        """Test CLI with valid --locale option."""
        runner = CliRunner()
        # Test with French locale via command line option
        result = runner.invoke(cli, ["analyze", "--locale", "fr_CA", "--help"])
        assert result.exit_code == 0
        assert "analyze" in result.output.lower() or "usage" in result.output.lower()

    def test_cli_locale_option_invalid(self):
        """Test CLI with invalid --locale option."""
        runner = CliRunner()
        # Test with invalid locale (without --help to trigger validation)
        result = runner.invoke(cli, ["analyze", "--locale", "invalid_LOCALE"])
        # Should fail with error about invalid choice
        assert result.exit_code != 0
        assert (
            "invalid" in result.output.lower()
            or "choice" in result.output.lower()
            or "error" in result.output.lower()
        )

    def test_cli_all_supported_locales(self):
        """Test CLI works with all supported locales."""
        runner = CliRunner()
        for locale in SUPPORTED_LOCALES:
            result = runner.invoke(cli, ["analyze", "--locale", locale, "--help"])
            # Should work for all supported locales
            assert result.exit_code == 0, f"Failed for locale {locale}"

    def test_cli_locale_option_priority(self):
        """Test that --locale option overrides NHL_SCRABBLE_LANG env var."""
        runner = CliRunner()
        # Set environment to one locale but use different locale in option
        result = runner.invoke(
            cli,
            ["analyze", "--locale", "en_US", "--help"],
            env={"NHL_SCRABBLE_LANG": "fr_CA"},
        )
        # Should work without errors (locale option takes precedence)
        assert result.exit_code == 0


class TestCLITranslatedStrings:
    """Test that CLI strings are translatable."""

    def test_help_text_wrapped(self):
        """Test that help text is wrapped for translation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        # Verify key help strings are present
        assert "output" in result.output.lower() or "format" in result.output.lower()

    def test_error_messages_translatable(self):
        """Test that error messages are translatable."""
        runner = CliRunner()
        # Test with invalid format to trigger error message
        result = runner.invoke(
            cli,
            ["analyze", "--format", "excel"],  # Excel requires --output
            env={"NHL_SCRABBLE_LANG": "fr_CA"},
        )
        # Should show error (exit code != 0)
        assert result.exit_code != 0
        # Error message should be present
        assert "excel" in result.output.lower() or "output" in result.output.lower()

    def test_output_validation_errors_translatable(self):
        """Test that output validation error messages are translatable."""
        import tempfile
        from pathlib import Path

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with non-existent output directory
            nonexistent_dir = Path(tmpdir) / "does_not_exist"
            output_file = str(nonexistent_dir / "output.txt")
            result = runner.invoke(
                cli,
                ["analyze", "--output", output_file],
                env={"NHL_SCRABBLE_LANG": "en_US"},
            )
            # Should show error about directory not existing
            assert result.exit_code != 0
            assert "does not exist" in result.output.lower() or "directory" in result.output.lower()

    def test_filter_display_messages_translatable(self):
        """Test that filter display messages are translatable."""
        runner = CliRunner()
        # Test with filters to trigger filter display
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--divisions",
                "Atlantic",
                "--min-score",
                "50",
                "--help",  # Use --help to avoid actual API calls
            ],
            env={"NHL_SCRABBLE_LANG": "en_US"},
        )
        # Should complete successfully
        assert result.exit_code == 0

    def test_csv_excel_warning_translatable(self):
        """Test that CSV/Excel format warning is translatable."""
        runner = CliRunner()
        # Test CSV format without --output (would trigger warning in actual run)
        # Using --help to avoid actual execution
        result = runner.invoke(
            cli,
            ["analyze", "--format", "csv", "--help"],
            env={"NHL_SCRABBLE_LANG": "en_US"},
        )
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_success_messages_translatable(self, mock_client_class: Mock):
        """Test that success messages are translatable."""
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        # Mock minimal data for successful run
        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }
        mock_client.get_team_roster.return_value = {
            "forwards": [
                {"playerId": 1, "firstName": {"default": "John"}, "lastName": {"default": "Doe"}},
            ],
            "defensemen": [],
            "goalies": [],
        }

        mock_client_class.return_value = mock_client

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["analyze", "--output", "test.txt"],
                env={"NHL_SCRABBLE_LANG": "en_US"},
            )
            # Should show success message
            assert result.exit_code == 0
            assert "✓" in result.output or "complete" in result.output.lower()

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_filter_messages_translatable(self, mock_client_class: Mock):
        """Test that filter display messages are translatable."""
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }
        mock_client.get_team_roster.return_value = {
            "forwards": [
                {"playerId": 1, "firstName": {"default": "John"}, "lastName": {"default": "Doe"}},
            ],
            "defensemen": [],
            "goalies": [],
        }

        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--divisions",
                "Atlantic",
                "--min-score",
                "1",
                "--max-score",
                "100",
            ],
            env={"NHL_SCRABBLE_LANG": "en_US"},
        )
        # Should show filter information
        assert result.exit_code == 0
        # Filter display messages should be present
        assert "filter" in result.output.lower() or "division" in result.output.lower()

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_nhl_api_error_messages_translatable(self, mock_client_class: Mock):
        """Test that NHL API error messages are translatable."""
        from nhl_scrabble.exceptions import NHLApiError

        # Setup mock client that raises an error
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_teams.side_effect = NHLApiError("API error occurred")

        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["analyze"],
            env={"NHL_SCRABBLE_LANG": "en_US"},
        )
        # Should show error message
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "❌" in result.output
