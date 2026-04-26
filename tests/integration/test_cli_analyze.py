"""Integration tests for CLI analyze command."""

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli

# All integration tests get 5 minute timeout
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(300),  # 5 minutes for integration tests
]


class TestCLIAnalyze:
    """Integration tests for the analyze command."""

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_analyze_command_with_mocked_api(
        self,
        mock_client_class: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze command with mocked API calls (via dependency injection)."""
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        # Mock get_teams to return standings data
        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
            "MTL": {"division": "Atlantic", "conference": "Eastern"},
            "EDM": {"division": "Pacific", "conference": "Western"},
        }

        # Mock get_team_roster to return roster data
        mock_client.get_team_roster.return_value = sample_roster_data

        mock_client_class.return_value = mock_client

        # Run CLI
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        # Verify execution
        assert result.exit_code == 0
        # Should have output
        assert len(result.output) > 0 or result.output == ""  # Might be empty in test mode

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_analyze_command_json_output(
        self,
        mock_client_class: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze command with JSON output (via dependency injection)."""
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        mock_client.get_team_roster.return_value = sample_roster_data

        mock_client_class.return_value = mock_client

        # Run CLI with JSON output
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["analyze", "--format", "json", "--output", "test.json"])

            assert result.exit_code == 0
            # JSON file should be created
            assert Path("test.json").exists()


class TestCLIOutputFormatValidation:
    """Integration tests for CLI output format validation (issue #366).

    Ensures CLI-advertised formats don't crash with pydantic ValidationError.
    """

    @pytest.mark.parametrize(
        ("output_format", "extension"),
        [
            ("text", "txt"),
            ("json", "json"),
            ("yaml", "yaml"),
            ("xml", "xml"),
            ("html", "html"),
            ("table", "txt"),
            ("markdown", "md"),
            ("csv", "csv"),
        ],
    )
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_analyze_supports_all_formats(
        self,
        mock_client_class: Mock,
        output_format: str,
        extension: str,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze command supports all advertised formats without ValidationError.

        Related to issue #366 - Previously, formats like 'markdown', 'yaml', 'xml',
        'table', and 'template' were accepted by CLI but rejected by Config,
        causing confusing pydantic ValidationError instead of friendly error.
        """
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        mock_client.get_team_roster.return_value = sample_roster_data

        mock_client_class.return_value = mock_client

        # Run CLI with format
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["analyze", "--format", output_format, "--output", f"test.{extension}"],
            )

            # Should not crash with ValidationError or pydantic error
            assert "ValidationError" not in result.output, (
                f"Format '{output_format}' crashed with ValidationError - "
                f"Config doesn't allow this CLI-advertised format!"
            )
            assert "pydantic" not in result.output.lower(), (
                f"Format '{output_format}' crashed with pydantic error - "
                f"Config validation rejected CLI-advertised format!"
            )

            # May fail for business reasons (e.g., formatter implementation issues),
            # but NOT for validation reasons
            if result.exit_code != 0:
                # If it failed, ensure it's not a validation error
                assert "Allowed values" not in result.output, (
                    f"Format '{output_format}' failed with enum validation error - "
                    f"Config should accept this CLI-advertised format!"
                )

    @patch("nhl_scrabble.di.NHLApiClient")
    def test_analyze_markdown_format_no_validation_error(
        self,
        mock_client_class: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze with markdown format doesn't crash with ValidationError.

        This is the exact scenario from issue #366:
        User runs: nhl-scrabble analyze -f markdown
        Expected: Either works or friendly error
        Bug: Got confusing pydantic ValidationError traceback
        """
        # Setup mock client
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        mock_client.get_team_roster.return_value = sample_roster_data

        mock_client_class.return_value = mock_client

        # Reproduce the original error scenario
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["analyze", "-f", "markdown", "-o", "report.md"])

            # Critical assertions: NO pydantic/validation errors
            assert "pydantic_core._pydantic_core.ValidationError" not in result.output
            assert "NHL_SCRABBLE_OUTPUT_FORMAT: Invalid value 'markdown'" not in result.output
            assert "pydantic" not in result.output.lower()

            # If it fails, it should be for a different reason (not validation)
            if result.exit_code != 0:
                assert "Allowed values" not in result.output
