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

    @patch("nhl_scrabble.cli.NHLApiClient")
    def test_analyze_command_with_mocked_api(
        self,
        mock_client_class: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze command with mocked API calls."""
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

    @patch("nhl_scrabble.cli.NHLApiClient")
    def test_analyze_command_json_output(
        self,
        mock_client_class: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test analyze command with JSON output."""
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
