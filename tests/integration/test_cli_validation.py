"""Integration tests for CLI input validation."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestCliOutputValidation:
    """Tests for CLI output path validation."""

    def test_valid_output_path(self, tmp_path: Path) -> None:
        """Test CLI accepts valid output path without validation errors."""
        output_file = tmp_path / "output.txt"
        runner = CliRunner()

        # Run with valid path - validation should pass
        # (Command may fail for other reasons like API errors, but validation should succeed)
        result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

        # Check that it didn't fail due to path validation
        # If exit code is 2, it's a click UsageError (validation failed)
        # If exit code is 1, it's runtime error (which is fine for this test)
        if result.exit_code == 2:
            # Validation error occurred
            assert (
                "path traversal" not in result.output.lower()
            ), "Path validation incorrectly rejected valid path"
            assert (
                "does not exist" not in result.output.lower()
            ), "Path validation incorrectly rejected valid directory"

    def test_path_traversal_blocked(self) -> None:
        """Test CLI rejects path traversal attempts."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", "../../../etc/passwd"])

        assert result.exit_code != 0
        # CLI validation uses validators.validate_file_path which detects path traversal
        assert (
            "suspicious pattern" in result.output.lower()
            or "path traversal" in result.output.lower()
        )

    def test_invalid_filename_characters(self, tmp_path: Path) -> None:
        """Test CLI rejects filenames with invalid characters."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", str(tmp_path / "file<>.txt")])

        assert result.exit_code != 0
        # After PR #201, validator reports specific invalid characters
        assert "invalid characters" in result.output.lower()

    def test_nonexistent_directory(self) -> None:
        """Test CLI rejects output to nonexistent directory."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/file.txt"])

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()


class TestCliNumericValidation:
    """Tests for CLI numeric parameter validation."""

    def test_valid_top_players(self) -> None:
        """Test CLI accepts valid top_players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "30"], catch_exceptions=False)

        # Should pass validation
        assert "cannot exceed" not in result.output.lower()
        assert "must be at least" not in result.output.lower()

    def test_top_players_too_high(self) -> None:
        """Test CLI rejects top_players value above maximum."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "999"])

        assert result.exit_code != 0
        # CLI validation uses validators.validate_integer_range which reports "cannot exceed"
        assert "cannot exceed" in result.output.lower() or "invalid" in result.output.lower()

    def test_top_players_too_low(self) -> None:
        """Test CLI rejects top_players value below minimum."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "0"])

        assert result.exit_code != 0
        # CLI validation uses validators.validate_integer_range which reports "must be at least"
        assert "must be at least" in result.output.lower() or "invalid" in result.output.lower()

    def test_top_players_non_integer(self) -> None:
        """Test CLI rejects non-integer top_players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "abc"])

        assert result.exit_code != 0
        # Click may reject this at the parameter level

    def test_valid_top_team_players(self) -> None:
        """Test CLI accepts valid top_team_players value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "10"], catch_exceptions=False)

        # Should pass validation
        assert "cannot exceed" not in result.output.lower()
        assert "must be at least" not in result.output.lower()

    def test_top_team_players_too_high(self) -> None:
        """Test CLI rejects top_team_players value above maximum."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "999"])

        assert result.exit_code != 0
        # CLI validation uses validators.validate_integer_range which reports "cannot exceed"
        assert "cannot exceed" in result.output.lower() or "invalid" in result.output.lower()


class TestEnvironmentVariableValidation:
    """Tests for environment variable validation in Config.from_env()."""

    def test_valid_environment_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test valid environment variables are accepted."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "15")
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "30")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"], catch_exceptions=False)

        # Should not have configuration errors
        assert "configuration error" not in result.output.lower()

    def test_api_timeout_too_high(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test API timeout above maximum is rejected."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "99999")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        # After PR #201, config_validators reports validation errors consistently
        assert "configuration error" in result.output.lower()
        assert "outside allowed range" in result.output.lower()

    def test_api_timeout_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test non-integer API timeout is rejected."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "not_a_number")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()

    def test_rate_limit_max_requests_too_high(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test rate limit max requests above maximum is rejected."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS", "9999")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        # After PR #201, config_validators reports validation errors consistently
        assert "configuration error" in result.output.lower()
        assert "outside allowed range" in result.output.lower()

    def test_top_players_too_high_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test top players count from env above maximum is rejected."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "9999")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        # After PR #201, config_validators reports validation errors consistently
        assert "configuration error" in result.output.lower()
        assert "outside allowed range" in result.output.lower()

    def test_invalid_output_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test invalid output format from env is rejected."""
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "invalid_format")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()


class TestCombinedValidation:
    """Tests for combined CLI and environment validation."""

    def test_cli_overrides_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CLI parameters override environment variables (and are validated)."""
        # Set valid env value
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "30")

        runner = CliRunner()
        # Override with invalid CLI value
        result = runner.invoke(cli, ["analyze", "--top-players", "999"])

        assert result.exit_code != 0
        # CLI validation uses Click IntRange
        assert (
            "invalid value" in result.output.lower() or "not in the range" in result.output.lower()
        )

    def test_environment_validation_before_cli(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test environment variables are validated even if CLI validation would pass."""
        # Invalid environment variable
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "99999")

        runner = CliRunner()
        # Valid CLI arguments
        result = runner.invoke(cli, ["analyze", "--output", str(tmp_path / "output.txt")])

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()
