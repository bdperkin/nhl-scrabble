"""Tests for season comparison and trend analysis modules."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from nhl_scrabble.reports.comparison import SeasonComparison, TrendAnalysis


@pytest.fixture
def mock_team_score() -> Mock:
    """Create mock TeamScore object.

    Returns:
        Mock TeamScore with realistic attributes
    """
    team = Mock()
    team.total = 1500
    team.avg_per_player = 50.0
    team.player_count = 30
    team.division = "Atlantic"
    team.conference = "Eastern"
    return team


@pytest.fixture
def mock_player_score() -> Mock:
    """Create mock PlayerScore object.

    Returns:
        Mock PlayerScore with realistic attributes
    """
    player = Mock()
    player.full_score = 50
    player.first_name = "John"
    player.last_name = "Doe"
    return player


class TestSeasonComparison:
    """Tests for SeasonComparison class."""

    def test_init(self) -> None:
        """Test SeasonComparison initialization."""
        seasons = ["20222023", "20232024"]
        comparison = SeasonComparison(seasons)

        assert comparison.seasons == sorted(seasons)
        assert comparison.season_data == {}

    def test_init_sorts_seasons(self) -> None:
        """Test that seasons are sorted on initialization."""
        seasons = ["20232024", "20222023", "20212022"]
        comparison = SeasonComparison(seasons)

        assert comparison.seasons == ["20212022", "20222023", "20232024"]

    def test_add_season_data(self, mock_team_score: Mock, mock_player_score: Mock) -> None:
        """Test adding season data."""
        comparison = SeasonComparison(["20222023"])

        team_scores = {"TOR": mock_team_score}
        all_players = [mock_player_score, mock_player_score]

        comparison.add_season_data("20222023", team_scores, all_players)

        assert "20222023" in comparison.season_data
        assert comparison.season_data["20222023"]["team_count"] == 1
        assert comparison.season_data["20222023"]["player_count"] == 2
        assert comparison.season_data["20222023"]["total_score"] == 100

    def test_generate_text_report_no_data(self) -> None:
        """Test generating text report with no data."""
        comparison = SeasonComparison(["20222023"])
        report = comparison.generate_text_report()

        assert "NHL SCRABBLE SEASON COMPARISON" in report
        assert "20222023" in report
        assert "No data available" in report

    def test_generate_text_report_with_data(
        self, mock_team_score: Mock, mock_player_score: Mock
    ) -> None:
        """Test generating text report with data."""
        comparison = SeasonComparison(["20222023"])

        team_scores = {"TOR": mock_team_score}
        all_players = [mock_player_score]

        comparison.add_season_data("20222023", team_scores, all_players)
        report = comparison.generate_text_report()

        assert "NHL SCRABBLE SEASON COMPARISON" in report
        assert "20222023" in report
        assert "Teams: 1" in report
        assert "Players: 1" in report

    def test_generate_json_report_no_data(self) -> None:
        """Test generating JSON report with no data."""
        comparison = SeasonComparison(["20222023"])
        report = comparison.generate_json_report()

        assert "seasons" in report
        assert report["seasons"] == ["20222023"]
        assert "comparison" in report
        assert report["comparison"]["20222023"]["error"] == "No data available"

    def test_generate_json_report_with_data(
        self, mock_team_score: Mock, mock_player_score: Mock
    ) -> None:
        """Test generating JSON report with data."""
        comparison = SeasonComparison(["20222023"])

        team_scores = {"TOR": mock_team_score}
        all_players = [mock_player_score]

        comparison.add_season_data("20222023", team_scores, all_players)
        report = comparison.generate_json_report()

        assert report["seasons"] == ["20222023"]
        assert report["comparison"]["20222023"]["team_count"] == 1
        assert report["comparison"]["20222023"]["player_count"] == 1
        assert report["comparison"]["20222023"]["total_score"] == 50
        assert report["comparison"]["20222023"]["average_per_player"] == 50.0


class TestTrendAnalysis:
    """Tests for TrendAnalysis class."""

    def test_init(self) -> None:
        """Test TrendAnalysis initialization."""
        analysis = TrendAnalysis("20202021", "20232024")

        assert analysis.start_season == "20202021"
        assert analysis.end_season == "20232024"
        assert analysis.season_data == {}

    def test_add_season_data(self, mock_team_score: Mock, mock_player_score: Mock) -> None:
        """Test adding season data for trend analysis."""
        analysis = TrendAnalysis("20202021", "20232024")

        team_scores = {"TOR": mock_team_score}
        all_players = [mock_player_score]

        analysis.add_season_data("20222023", team_scores, all_players)

        assert "20222023" in analysis.season_data
        assert analysis.season_data["20222023"]["team_count"] == 1
        assert analysis.season_data["20222023"]["player_count"] == 1

    def test_calculate_trends_insufficient_data(self) -> None:
        """Test trend calculation with insufficient data."""
        analysis = TrendAnalysis("20202021", "20232024")

        trends = analysis.calculate_trends()

        assert trends["seasons_analyzed"] == 0
        assert "error" in trends

    def test_calculate_trends_with_data(
        self, mock_team_score: Mock, mock_player_score: Mock
    ) -> None:
        """Test trend calculation with multiple seasons."""
        analysis = TrendAnalysis("20202021", "20232024")

        # Add data for multiple seasons with increasing scores
        for i, season in enumerate(["20202021", "20212022", "20222023"]):
            player = Mock()
            player.full_score = 50 + (i * 10)  # Increasing scores
            all_players = [player] * 10

            team_scores = {"TOR": mock_team_score}
            analysis.add_season_data(season, team_scores, all_players)

        trends = analysis.calculate_trends()

        assert trends["seasons_analyzed"] == 3
        assert trends["trend_direction"] == "increasing"
        assert trends["total_change"] > 0
        assert trends["percent_change"] > 0

    def test_calculate_trends_decreasing(self, mock_team_score: Mock) -> None:
        """Test trend calculation with decreasing scores."""
        analysis = TrendAnalysis("20202021", "20222023")

        # Add data with decreasing scores
        for i, season in enumerate(["20202021", "20212022"]):
            player = Mock()
            player.full_score = 100 - (i * 20)  # Decreasing scores
            all_players = [player] * 10

            team_scores = {"TOR": mock_team_score}
            analysis.add_season_data(season, team_scores, all_players)

        trends = analysis.calculate_trends()

        assert trends["trend_direction"] == "decreasing"
        assert trends["total_change"] < 0

    def test_generate_text_report(self, mock_team_score: Mock, mock_player_score: Mock) -> None:
        """Test generating text trend report."""
        analysis = TrendAnalysis("20202021", "20232024")

        team_scores = {"TOR": mock_team_score}
        all_players = [mock_player_score] * 10

        analysis.add_season_data("20222023", team_scores, all_players)
        analysis.add_season_data("20232024", team_scores, all_players)

        report = analysis.generate_text_report()

        assert "NHL SCRABBLE TREND ANALYSIS" in report
        assert "20202021" in report
        assert "20232024" in report
        assert "Trend Direction:" in report
