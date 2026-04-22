"""Tests for ReportGenerator.get_report() method with all report types."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.reports.generator import ReportGenerator


@pytest.fixture
def sample_data() -> tuple[
    dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    """Create sample data for testing.

    Returns:
        Tuple of (team_scores, all_players, division_standings,
                  conference_standings, playoff_standings)
    """
    team_scores = {"PIT": Mock(), "EDM": Mock()}
    all_players = [Mock(), Mock()]
    division_standings = {"Metropolitan": Mock(), "Pacific": Mock()}
    conference_standings = {"Eastern": Mock(), "Western": Mock()}
    playoff_standings = {"Eastern": [Mock()], "Western": [Mock()]}

    return team_scores, all_players, division_standings, conference_standings, playoff_standings


class TestGetReportMethod:
    """Test get_report() method with all report type options."""

    def test_get_report_conference(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with 'conference' type."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(
            generator._conference_reporter, "generate", return_value="Conference Report"
        ):
            report = generator.get_report("conference")
            assert report == "Conference Report"
            assert generator._conference_report is not None
            # Other reports should still be None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_get_report_division(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with 'division' type."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._division_reporter, "generate", return_value="Division Report"):
            report = generator.get_report("division")
            assert report == "Division Report"
            assert generator._division_report is not None
            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_get_report_playoff(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with 'playoff' type."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._playoff_reporter, "generate", return_value="Playoff Report"):
            report = generator.get_report("playoff")
            assert report == "Playoff Report"
            assert generator._playoff_report is not None
            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._team_report is None
            assert generator._stats_report is None

    def test_get_report_team(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with 'team' type."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._team_reporter, "generate", return_value="Team Report"):
            report = generator.get_report("team")
            assert report == "Team Report"
            assert generator._team_report is not None
            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._stats_report is None

    def test_get_report_stats(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with 'stats' type."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._stats_reporter, "generate", return_value="Stats Report"):
            report = generator.get_report("stats")
            assert report == "Stats Report"
            assert generator._stats_report is not None
            # Other reports should still be None
            assert generator._conference_report is None
            assert generator._division_report is None
            assert generator._playoff_report is None
            assert generator._team_report is None

    def test_get_report_none_returns_full_report(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with None returns full report."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with (
            patch.object(generator._conference_reporter, "generate", return_value="Conference\n"),
            patch.object(generator._division_reporter, "generate", return_value="Division\n"),
            patch.object(generator._playoff_reporter, "generate", return_value="Playoff\n"),
            patch.object(generator._team_reporter, "generate", return_value="Team\n"),
            patch.object(generator._stats_reporter, "generate", return_value="Stats\n"),
        ):
            report = generator.get_report(None)
            assert isinstance(report, str)
            # All reports should be generated
            assert generator._conference_report is not None
            assert generator._division_report is not None
            assert generator._playoff_report is not None
            assert generator._team_report is not None
            assert generator._stats_report is not None

    def test_get_report_invalid_type_raises_error(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with invalid type raises ValueError."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with pytest.raises(ValueError, match="Unknown report type: invalid_type"):
            generator.get_report("invalid_type")

    def test_get_report_empty_string_raises_error(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test get_report with empty string raises ValueError."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with pytest.raises(ValueError, match="Unknown report type"):
            generator.get_report("")


class TestReportCaching:
    """Test that all report types properly cache results."""

    def test_conference_report_caching(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test conference report is cached and not regenerated."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._conference_reporter, "generate") as mock_generate:
            mock_generate.return_value = "Conference Report"

            # First access
            report1 = generator.conference_report
            assert mock_generate.call_count == 1

            # Second access (should use cache)
            report2 = generator.conference_report
            assert mock_generate.call_count == 1  # No additional call
            assert report1 == report2

    def test_division_report_caching(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test division report is cached and not regenerated."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._division_reporter, "generate") as mock_generate:
            mock_generate.return_value = "Division Report"

            # First access
            report1 = generator.division_report
            assert mock_generate.call_count == 1

            # Second access (should use cache)
            report2 = generator.division_report
            assert mock_generate.call_count == 1
            assert report1 == report2

    def test_playoff_report_caching(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test playoff report is cached and not regenerated."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._playoff_reporter, "generate") as mock_generate:
            mock_generate.return_value = "Playoff Report"

            # First access
            report1 = generator.playoff_report
            assert mock_generate.call_count == 1

            # Second access (should use cache)
            report2 = generator.playoff_report
            assert mock_generate.call_count == 1
            assert report1 == report2

    def test_stats_report_caching(
        self,
        sample_data: tuple[
            dict[str, Any], list[Any], dict[str, Any], dict[str, Any], dict[str, Any]
        ],
    ) -> None:
        """Test stats report is cached and not regenerated."""
        team_scores, all_players, div_standings, conf_standings, playoff_standings = sample_data

        generator = ReportGenerator(
            team_scores=team_scores,
            all_players=all_players,
            division_standings=div_standings,
            conference_standings=conf_standings,
            playoff_standings=playoff_standings,
        )

        with patch.object(generator._stats_reporter, "generate") as mock_generate:
            mock_generate.return_value = "Stats Report"

            # First access
            report1 = generator.stats_report
            assert mock_generate.call_count == 1

            # Second access (should use cache)
            report2 = generator.stats_report
            assert mock_generate.call_count == 1
            assert report1 == report2
