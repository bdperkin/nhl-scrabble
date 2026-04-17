"""Unit tests for progress bar management."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from nhl_scrabble.ui.progress import ProgressManager


class TestProgressManager:
    """Test suite for ProgressManager class."""

    def test_init_enabled(self) -> None:
        """Test ProgressManager initialization with enabled=True."""
        mgr = ProgressManager(enabled=True)
        assert mgr.enabled is True
        assert mgr._progress is None  # noqa: SLF001

    def test_init_disabled(self) -> None:
        """Test ProgressManager initialization with enabled=False."""
        mgr = ProgressManager(enabled=False)
        assert mgr.enabled is False
        assert mgr._progress is None  # noqa: SLF001

    def test_init_default(self) -> None:
        """Test ProgressManager initialization with default settings."""
        mgr = ProgressManager()
        assert mgr.enabled is True  # Default is enabled

    def test_create_progress_disabled(self) -> None:
        """Test create_progress when disabled returns None."""
        mgr = ProgressManager(enabled=False)

        with mgr.create_progress() as progress:
            assert progress is None

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_create_progress_enabled(self, mock_progress_class: Mock) -> None:
        """Test create_progress when enabled returns Progress instance."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)

        with mgr.create_progress() as progress:
            assert progress is mock_progress
            mock_progress.start.assert_called_once()

        mock_progress.stop.assert_called_once()

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_create_progress_cleanup_on_exception(self, mock_progress_class: Mock) -> None:
        """Test create_progress cleans up even when exception occurs."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)

        try:
            with mgr.create_progress():
                raise ValueError("test error")
        except ValueError:
            pass  # Expected exception

        # Should still call stop even after exception
        mock_progress.stop.assert_called_once()

    def test_track_api_fetching_disabled(self) -> None:
        """Test track_api_fetching when disabled does nothing."""
        mgr = ProgressManager(enabled=False)

        teams_fetched = []
        with mgr.track_api_fetching(3) as update:
            for team in ["TOR", "MTL", "BOS"]:
                teams_fetched.append(team)
                update(team)  # Should not raise error

        assert len(teams_fetched) == 3

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_track_api_fetching_enabled(self, mock_progress_class: Mock) -> None:
        """Test track_api_fetching when enabled tracks progress."""
        mock_progress = MagicMock()
        mock_task_id = "task-1"
        mock_progress.add_task.return_value = mock_task_id
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)

        teams = ["TOR", "MTL", "BOS"]
        with mgr.track_api_fetching(len(teams)) as update:
            for team in teams:
                update(team)

        # Verify add_task called with correct params
        mock_progress.add_task.assert_called_once_with("Fetching team rosters", total=3, status="")

        # Verify update called for each team
        assert mock_progress.update.call_count == 3
        update_calls = mock_progress.update.call_args_list

        # Check each call
        for i, team in enumerate(teams):
            call_args = update_calls[i]
            assert call_args[0][0] == mock_task_id  # First positional arg is task_id
            assert call_args[1]["advance"] == 1
            assert team in call_args[1]["status"]

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_track_score_calculation_enabled(self, mock_progress_class: Mock) -> None:
        """Test track_score_calculation when enabled tracks progress."""
        mock_progress = MagicMock()
        mock_task_id = "task-2"
        mock_progress.add_task.return_value = mock_task_id
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)

        total_players = 5
        with mgr.track_score_calculation(total_players) as update:
            for _ in range(total_players):
                update()

        # Verify add_task called
        mock_progress.add_task.assert_called_once_with(
            "Calculating Scrabble scores", total=5, status=""
        )

        # Verify update called for each player
        assert mock_progress.update.call_count == 5

    def test_track_score_calculation_disabled(self) -> None:
        """Test track_score_calculation when disabled does nothing."""
        mgr = ProgressManager(enabled=False)

        count = 0
        with mgr.track_score_calculation(5) as update:
            for _ in range(5):
                count += 1
                update()  # Should not raise error

        assert count == 5

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_track_report_generation_enabled(self, mock_progress_class: Mock) -> None:
        """Test track_report_generation when enabled tracks progress."""
        mock_progress = MagicMock()
        mock_task_id = "task-3"
        mock_progress.add_task.return_value = mock_task_id
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)

        reports = ["Conference", "Division", "Playoff", "Team", "Stats"]
        with mgr.track_report_generation(len(reports)) as update:
            for report_name in reports:
                update(report_name)

        # Verify add_task called
        mock_progress.add_task.assert_called_once_with("Generating reports", total=5, status="")

        # Verify update called for each report
        assert mock_progress.update.call_count == 5
        update_calls = mock_progress.update.call_args_list

        # Check each call
        for i, report_name in enumerate(reports):
            call_args = update_calls[i]
            assert call_args[0][0] == mock_task_id
            assert call_args[1]["advance"] == 1
            assert report_name in call_args[1]["status"]

    def test_track_report_generation_disabled(self) -> None:
        """Test track_report_generation when disabled does nothing."""
        mgr = ProgressManager(enabled=False)

        reports_generated = []
        with mgr.track_report_generation(3) as update:
            for report_name in ["Conference", "Division", "Playoff"]:
                reports_generated.append(report_name)
                update(report_name)  # Should not raise error

        assert len(reports_generated) == 3

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_progress_manager_stores_instance(self, mock_progress_class: Mock) -> None:
        """Test that ProgressManager stores Progress instance while active."""
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress

        mgr = ProgressManager(enabled=True)
        assert mgr._progress is None  # noqa: SLF001

        with mgr.create_progress() as progress:
            # Progress instance should be stored and match mock
            assert mgr._progress is progress  # noqa: SLF001
            assert progress is mock_progress

        # Should be cleared after context exit
        assert mgr._progress is None  # noqa: SLF001  # type: ignore

    @patch("nhl_scrabble.ui.progress.Progress")
    def test_multiple_progress_contexts_sequential(self, mock_progress_class: Mock) -> None:
        """Test using multiple progress contexts sequentially."""
        mock_progress_1 = MagicMock()
        mock_progress_2 = MagicMock()
        mock_progress_class.side_effect = [mock_progress_1, mock_progress_2]

        mgr = ProgressManager(enabled=True)

        # First context
        with mgr.create_progress() as progress1:
            assert progress1 is mock_progress_1

        assert mgr._progress is None  # noqa: SLF001

        # Second context
        with mgr.create_progress() as progress2:
            assert progress2 is mock_progress_2

        assert mgr._progress is None  # noqa: SLF001
