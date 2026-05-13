"""Comprehensive unit tests for CLI search and serve commands.

This module tests the search and serve commands for player search functionality
and web server startup.

Target: Improve coverage of search (lines 1186-1291) and serve (lines 1293-1401)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestSearchCommand:
    """Test search command implementation."""

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_basic_execution(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test basic search command execution."""
        # Setup config
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        # Setup container and components
        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()

        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        # Setup search
        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results"

        runner = CliRunner()
        result = runner.invoke(cli, ["search"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_json")
    def test_search_json_format(
        self,
        mock_gen_json: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search with JSON output format."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_json.return_value = '{"results": []}'

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--format", "json"])

        assert result.exit_code == 0
        assert mock_gen_json.called

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_with_query(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search with query string."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results"

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "Ovechkin"])

        assert result.exit_code == 0
        # Verify search was called with query
        mock_search.search.assert_called_once()

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_with_fuzzy_matching(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search with fuzzy matching enabled."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results"

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--fuzzy", "Ovechkn"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_with_score_filters(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search with min/max score filters."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results"

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--min-score", "50", "--max-score", "100"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_with_limit(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search with result limit."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        # Return many results to test limiting
        many_results = [MagicMock() for _ in range(100)]
        mock_team_processor.process_all_teams.return_value = ({}, many_results, [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = many_results
        mock_search.get_stats.return_value = {"total": 100}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results"

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "10"])

        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    @patch("nhl_scrabble.cli.commands.search.generate_search_text")
    def test_search_with_output_file(
        self,
        mock_gen_text: MagicMock,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test search writing to output file."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        mock_gen_text.return_value = "Search results content"

        output_file = tmp_path / "search_results.txt"
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Search results content" in output_file.read_text()

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    def test_search_handles_api_error(
        self,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search handles API errors gracefully."""
        from nhl_scrabble.api.nhl_client import NHLApiError

        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.side_effect = NHLApiError("API down")
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        runner = CliRunner()
        result = runner.invoke(cli, ["search"])

        assert result.exit_code == 1
        assert "error" in result.output.lower() or "api" in result.output.lower()

    @patch("nhl_scrabble.cli.commands.search.Config")
    def test_search_config_validation_error(self, mock_config_class: MagicMock) -> None:
        """Test search handles config validation errors."""
        mock_config_class.from_env.side_effect = ValueError("Invalid config")

        runner = CliRunner()
        result = runner.invoke(cli, ["search"])

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()

    @patch("nhl_scrabble.cli.commands.search.Config")
    @patch("nhl_scrabble.cli.commands.search.DependencyContainer")
    @patch("nhl_scrabble.cli.commands.search.PlayerSearch")
    def test_search_with_quiet_mode(
        self,
        mock_search_class: MagicMock,
        mock_container_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test search in quiet mode."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config_class.from_env.return_value = mock_config

        mock_container = MagicMock()
        mock_api_client = MagicMock()
        mock_api_client.__enter__.return_value = mock_api_client
        mock_api_client.__exit__.return_value = None
        mock_container.create_api_client.return_value = mock_api_client
        mock_container.create_scorer.return_value = MagicMock()
        mock_team_processor = MagicMock()
        mock_team_processor.process_all_teams.return_value = ({}, [], [])
        mock_container.create_team_processor.return_value = mock_team_processor
        mock_container_class.return_value = mock_container

        mock_search = MagicMock()
        mock_search.search.return_value = []
        mock_search.get_stats.return_value = {"total": 0}
        mock_search_class.return_value = mock_search

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--quiet"])

        assert result.exit_code == 0
