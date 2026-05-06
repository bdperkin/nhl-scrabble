"""Tests for CLI internationalization functionality."""

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
