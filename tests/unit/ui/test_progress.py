"""Tests for progress bar management."""

from nhl_scrabble.ui.progress import ProgressManager


class TestProgressManagerInit:
    """Test ProgressManager initialization."""

    def test_init_enabled_by_default(self) -> None:
        """Test manager is enabled by default."""
        manager = ProgressManager()
        assert manager.enabled is True
        assert manager._progress is None

    def test_init_disabled(self) -> None:
        """Test manager can be disabled."""
        manager = ProgressManager(enabled=False)
        assert manager.enabled is False
        assert manager._progress is None


class TestProgressManagerCreateProgress:
    """Test create_progress context manager."""

    def test_create_progress_enabled(self) -> None:
        """Test creating progress when enabled."""
        manager = ProgressManager(enabled=True)

        with manager.create_progress() as progress:
            assert progress is not None
            # Progress should be started
            assert manager._progress is progress

        # After context, progress should be stopped and cleared
        assert manager._progress is None

    def test_create_progress_disabled(self) -> None:
        """Test creating progress when disabled returns None."""
        manager = ProgressManager(enabled=False)

        with manager.create_progress() as progress:
            assert progress is None
            assert manager._progress is None

        # Should still be None after context
        assert manager._progress is None


class TestProgressManagerTrackApiFetching:
    """Test track_api_fetching context manager."""

    def test_track_api_fetching_enabled(self) -> None:
        """Test tracking API fetching when enabled."""
        manager = ProgressManager(enabled=True)

        with manager.track_api_fetching(total_teams=32) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Should be able to call update function
            update_func("TOR")
            update_func("MTL")

    def test_track_api_fetching_disabled(self) -> None:
        """Test tracking API fetching when disabled."""
        manager = ProgressManager(enabled=False)

        with manager.track_api_fetching(total_teams=32) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Update function should be a no-op
            update_func("TOR")  # Should not raise

    def test_track_api_fetching_all_teams(self) -> None:
        """Test tracking all teams."""
        manager = ProgressManager(enabled=True)

        teams = ["TOR", "MTL", "BOS", "NYR"]
        with manager.track_api_fetching(total_teams=len(teams)) as update_func:
            for team in teams:
                update_func(team)


class TestProgressManagerTrackScoreCalculation:
    """Test track_score_calculation context manager."""

    def test_track_score_calculation_enabled(self) -> None:
        """Test tracking score calculation when enabled."""
        manager = ProgressManager(enabled=True)

        with manager.track_score_calculation(total_players=100) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Should be able to call update function
            update_func()
            update_func()

    def test_track_score_calculation_disabled(self) -> None:
        """Test tracking score calculation when disabled."""
        manager = ProgressManager(enabled=False)

        with manager.track_score_calculation(total_players=100) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Update function should be a no-op
            update_func()  # Should not raise

    def test_track_score_calculation_all_players(self) -> None:
        """Test tracking all players."""
        manager = ProgressManager(enabled=True)

        total_players = 50
        with manager.track_score_calculation(total_players=total_players) as update_func:
            for _ in range(total_players):
                update_func()


class TestProgressManagerTrackReportGeneration:
    """Test track_report_generation context manager."""

    def test_track_report_generation_enabled(self) -> None:
        """Test tracking report generation when enabled."""
        manager = ProgressManager(enabled=True)

        with manager.track_report_generation(total_reports=5) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Should be able to call update function
            update_func("standings.txt")
            update_func("playoff_bracket.txt")

    def test_track_report_generation_disabled(self) -> None:
        """Test tracking report generation when disabled."""
        manager = ProgressManager(enabled=False)

        with manager.track_report_generation(total_reports=5) as update_func:
            assert update_func is not None
            assert callable(update_func)

            # Update function should be a no-op
            update_func("standings.txt")  # Should not raise

    def test_track_report_generation_all_reports(self) -> None:
        """Test tracking all reports."""
        manager = ProgressManager(enabled=True)

        reports = ["standings", "divisions", "conferences", "playoffs", "top_players"]
        with manager.track_report_generation(total_reports=len(reports)) as update_func:
            for report in reports:
                update_func(report)


class TestProgressManagerIntegration:
    """Integration tests for ProgressManager."""

    def test_multiple_progress_contexts_sequential(self) -> None:
        """Test using multiple progress contexts sequentially."""
        manager = ProgressManager(enabled=True)

        # First context
        with manager.track_api_fetching(total_teams=5) as update_func:
            update_func("TOR")

        # Second context
        with manager.track_score_calculation(total_players=10) as update_func:
            update_func()

        # Third context
        with manager.track_report_generation(total_reports=3) as update_func:
            update_func("report1")

    def test_disabled_manager_all_contexts(self) -> None:
        """Test all contexts work correctly when manager is disabled."""
        manager = ProgressManager(enabled=False)

        with manager.track_api_fetching(total_teams=5) as update_func:
            update_func("TOR")

        with manager.track_score_calculation(total_players=10) as update_func:
            update_func()

        with manager.track_report_generation(total_reports=3) as update_func:
            update_func("report1")

        # All should complete without errors
