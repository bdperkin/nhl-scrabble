"""Integration tests for CLI progress bars."""

from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestCLIProgress:
    """Test suite for CLI progress bar integration."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_cli_default_shows_progress(self, mock_run_analysis: Mock) -> None:
        """Test CLI shows progress bars by default."""
        mock_run_analysis.return_value = "Test report output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        # Should succeed
        assert result.exit_code == 0

        # Should have called run_analysis with quiet=False (default)
        mock_run_analysis.assert_called_once()
        call_kwargs = mock_run_analysis.call_args[1]
        assert call_kwargs["quiet"] is False

    @patch("nhl_scrabble.cli.run_analysis")
    def test_cli_quiet_mode(self, mock_run_analysis: Mock) -> None:
        """Test CLI --quiet suppresses progress."""
        mock_run_analysis.return_value = "Test report output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--quiet"])

        # Should succeed
        assert result.exit_code == 0

        # Should have called run_analysis with quiet=True
        mock_run_analysis.assert_called_once()
        call_kwargs = mock_run_analysis.call_args[1]
        assert call_kwargs["quiet"] is True

    @patch("nhl_scrabble.cli.run_analysis")
    def test_cli_quiet_short_flag(self, mock_run_analysis: Mock) -> None:
        """Test CLI -q short flag suppresses progress."""
        mock_run_analysis.return_value = "Test report output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "-q"])

        # Should succeed
        assert result.exit_code == 0

        # Should have called run_analysis with quiet=True
        mock_run_analysis.assert_called_once()
        call_kwargs = mock_run_analysis.call_args[1]
        assert call_kwargs["quiet"] is True

    @patch("nhl_scrabble.cli.run_analysis")
    def test_cli_verbose_with_progress(self, mock_run_analysis: Mock) -> None:
        """Test CLI verbose mode still shows progress."""
        mock_run_analysis.return_value = "Test report output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--verbose"])

        # Should succeed
        assert result.exit_code == 0

        # Should have called run_analysis with quiet=False
        mock_run_analysis.assert_called_once()
        call_kwargs = mock_run_analysis.call_args[1]
        assert call_kwargs["quiet"] is False

    @patch("nhl_scrabble.cli.run_analysis")
    def test_cli_verbose_and_quiet(self, mock_run_analysis: Mock) -> None:
        """Test CLI --verbose --quiet combination (quiet wins)."""
        mock_run_analysis.return_value = "Test report output"

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--verbose", "--quiet"])

        # Should succeed
        assert result.exit_code == 0

        # Should have called run_analysis with quiet=True
        mock_run_analysis.assert_called_once()
        call_kwargs = mock_run_analysis.call_args[1]
        assert call_kwargs["quiet"] is True

    @patch("nhl_scrabble.cli.NHLApiClient")
    @patch("nhl_scrabble.cli.ProgressManager")
    def test_progress_manager_created_with_quiet_flag(
        self, mock_progress_manager: Mock, mock_api_client: Mock
    ) -> None:
        """Test ProgressManager is created with correct enabled flag."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        mock_client_instance.get_teams.return_value = {}

        mock_mgr_instance = MagicMock()
        mock_progress_manager.return_value = mock_mgr_instance
        mock_mgr_instance.track_api_fetching.return_value.__enter__.return_value = lambda x: None
        mock_mgr_instance.track_report_generation.return_value.__enter__.return_value = lambda x: (
            None
        )

        runner = CliRunner()

        # Test with quiet=True
        runner.invoke(cli, ["analyze", "--quiet"])
        mock_progress_manager.assert_called_with(enabled=False)

        # Reset mock
        mock_progress_manager.reset_mock()

        # Test with quiet=False (default)
        runner.invoke(cli, ["analyze"])
        mock_progress_manager.assert_called_with(enabled=True)

    @patch("nhl_scrabble.cli.NHLApiClient")
    @patch("nhl_scrabble.cli.TeamProcessor")
    @patch("nhl_scrabble.cli.ProgressManager")
    def test_progress_callback_passed_to_team_processor(
        self,
        mock_progress_manager: Mock,
        mock_team_processor: Mock,
        mock_api_client: Mock,
    ) -> None:
        """Test TeamProcessor.process_all_teams() is called without progress callback.

        Note: With concurrent processing, progress is logged internally by TeamProcessor
        rather than via callback, as we can't predict the order teams will complete.
        """
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        mock_client_instance.get_teams.return_value = {}

        mock_processor_instance = MagicMock()
        mock_team_processor.return_value = mock_processor_instance
        mock_processor_instance.process_all_teams.return_value = ({}, [], [])
        mock_processor_instance.calculate_division_standings.return_value = {}
        mock_processor_instance.calculate_conference_standings.return_value = {}

        # Setup progress manager mock
        mock_mgr_instance = MagicMock()
        mock_progress_manager.return_value = mock_mgr_instance
        mock_callback = MagicMock()
        mock_mgr_instance.track_api_fetching.return_value.__enter__.return_value = mock_callback
        mock_mgr_instance.track_report_generation.return_value.__enter__.return_value = lambda x: (
            None
        )

        runner = CliRunner()
        runner.invoke(cli, ["analyze"])

        # Verify process_all_teams was called with season=None
        # (concurrent processing logs progress internally, no callback needed)
        mock_processor_instance.process_all_teams.assert_called_once_with(season=None)
