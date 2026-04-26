"""Tests for lazy report generation.

Note: These tests access private members (_*_report) to verify lazy evaluation behavior. This is
intentional and necessary for testing the caching mechanism.
"""

# Private member access required for lazy evaluation testing

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.reports.generator import ReportGenerator

# Type alias for test fixture
SampleData = tuple[dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]]


@pytest.fixture
def sample_data() -> SampleData:
    """Create sample data for testing.

    Returns:
        Tuple of (team_scores, all_players, division_standings,
                  conference_standings, playoff_standings)
    """
    # For lazy evaluation tests, we just need non-None data
    # The actual content doesn't matter since we'll mock the generate methods
    team_scores = {"PIT": Mock(), "EDM": Mock()}
    all_players = [Mock(), Mock()]
    division_standings = {"Metropolitan": Mock(), "Pacific": Mock()}
    conference_standings = {"Eastern": Mock(), "Western": Mock()}
    playoff_standings = {"Eastern": [Mock()], "Western": [Mock()]}

    return team_scores, all_players, division_standings, conference_standings, playoff_standings


class TestReportGenerator:
    """Test suite for ReportGenerator lazy evaluation."""

    def test_initialization(self, sample_data: SampleData) -> None:
        """Test report generator initializes with None cached reports."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Verify all reports start as None (not yet generated)
        assert generator._conference_report is None
        assert generator._division_report is None
        assert generator._playoff_report is None
        assert generator._team_report is None
        assert generator._stats_report is None

    def test_lazy_team_report_generation(self, sample_data: SampleData) -> None:
        """Test team report is generated lazily."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method to avoid processing
        with patch.object(generator._team_reporter, "generate", return_value="Team Report"):
            # Before accessing, report should be None
            assert generator._team_report is None

            # Access team report
            report = generator.team_report

            # After accessing, report should be cached
            assert generator._team_report is not None
            assert isinstance(report, str)  # type: ignore[unreachable]
            assert report == "Team Report"

            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._stats_report is None

    def test_lazy_playoff_report_generation(self, sample_data: SampleData) -> None:
        """Test playoff report is generated lazily."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method
        with patch.object(generator._playoff_reporter, "generate", return_value="Playoff Report"):
            # Access only playoff report
            report = generator.playoff_report

            # Verify playoff report is cached
            assert generator._playoff_report is not None
            assert isinstance(report, str)
            assert report == "Playoff Report"

            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_lazy_stats_report_generation(self, sample_data: SampleData) -> None:
        """Test stats report is generated lazily."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method
        with patch.object(generator._stats_reporter, "generate", return_value="Stats Report"):
            # Access only stats report
            report = generator.stats_report

            # Verify stats report is cached
            assert generator._stats_report is not None
            assert isinstance(report, str)
            assert report == "Stats Report"

            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None

    def test_report_caching(self, sample_data: SampleData) -> None:
        """Test that reports are cached and not regenerated."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the reporter to track calls
        with patch.object(generator._team_reporter, "generate") as mock_generate:
            mock_generate.return_value = "Mock Report"

            # First access
            report1 = generator.team_report
            assert mock_generate.call_count == 1

            # Second access (should use cache)
            report2 = generator.team_report
            assert mock_generate.call_count == 1  # No additional call
            assert report1 == report2

    def test_get_report_with_filter(self, sample_data: SampleData) -> None:
        """Test get_report with specific filter."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method
        with patch.object(generator._team_reporter, "generate", return_value="Team Report"):
            # Get only team report
            report = generator.get_report("team")
            assert isinstance(report, str)
            assert report == "Team Report"

            # Verify only team report was generated
            assert generator._team_report is not None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._stats_report is None

    def test_get_report_invalid_filter(self, sample_data: SampleData) -> None:
        """Test get_report with invalid filter raises ValueError."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with pytest.raises(ValueError, match="Unknown report type: invalid"):
            generator.get_report("invalid")

    def test_get_report_no_filter_generates_all(self, sample_data: SampleData) -> None:
        """Test get_report with no filter generates all reports."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock all generate methods
        with (
            patch.object(
                generator._conference_reporter,
                "generate",
                return_value="Conference Report",
            ),
            patch.object(generator._division_reporter, "generate", return_value="Division Report"),
            patch.object(generator._playoff_reporter, "generate", return_value="Playoff Report"),
            patch.object(generator._team_reporter, "generate", return_value="Team Report"),
            patch.object(generator._stats_reporter, "generate", return_value="Stats Report"),
        ):
            # Get full report
            report = generator.get_report(None)
            assert isinstance(report, str)

            # Verify all reports were generated
            assert generator._conference_report is not None
            assert generator._division_report is not None
            assert generator._playoff_report is not None
            assert generator._team_report is not None
            assert generator._stats_report is not None

    def test_full_report_property(self, sample_data: SampleData) -> None:
        """Test full_report property generates all reports."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock all generate methods
        with (
            patch.object(
                generator._conference_reporter,
                "generate",
                return_value="Conference Report",
            ),
            patch.object(generator._division_reporter, "generate", return_value="Division Report"),
            patch.object(generator._playoff_reporter, "generate", return_value="Playoff Report"),
            patch.object(generator._team_reporter, "generate", return_value="Team Report"),
            patch.object(generator._stats_reporter, "generate", return_value="Stats Report"),
        ):
            # Get full report via property
            report = generator.full_report
            assert isinstance(report, str)

            # Verify all reports were generated
            assert generator._conference_report is not None
            assert generator._division_report is not None
            assert generator._playoff_report is not None
            assert generator._team_report is not None
            assert generator._stats_report is not None

    def test_lazy_conference_report_generation(self, sample_data: SampleData) -> None:
        """Test conference report is generated lazily."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method
        with patch.object(
            generator._conference_reporter,
            "generate",
            return_value="Conference Report",
        ):
            # Access only conference report
            report = generator.conference_report

            # Verify conference report is cached
            assert generator._conference_report is not None
            assert isinstance(report, str)
            assert report == "Conference Report"

            # Other reports should still be None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_lazy_division_report_generation(self, sample_data: SampleData) -> None:
        """Test division report is generated lazily."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        # Mock the generate method
        with patch.object(generator._division_reporter, "generate", return_value="Division Report"):
            # Access only division report
            report = generator.division_report

            # Verify division report is cached
            assert generator._division_report is not None
            assert isinstance(report, str)
            assert report == "Division Report"

            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_custom_top_counts(self, sample_data: SampleData) -> None:
        """Test custom top player counts are passed to reporters."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
            top_players_count=50,
            top_team_players_count=10,
        )

        # Verify reporters have correct counts
        assert generator._team_reporter.top_players_per_team == 10
        assert generator._stats_reporter.top_players_count == 50
