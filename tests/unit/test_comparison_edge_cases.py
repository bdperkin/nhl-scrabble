"""Edge case tests for season comparison and trend analysis."""

from unittest.mock import Mock

from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.reports.comparison import SeasonComparison, TrendAnalysis


class TestSeasonComparisonEdgeCases:
    """Test edge cases for SeasonComparison."""

    def test_season_with_zero_player_count(self):
        """Test season with zero players (edge case for average calculation)."""
        comparison = SeasonComparison(["20222023"])

        # Add season with zero players
        comparison.add_season_data("20222023", {}, [])

        # Generate report - should handle division by zero
        report = comparison.generate_text_report()
        assert "20222023" in report
        assert "Players: 0" in report
        # Should not include average per player line when count is 0

    def test_season_with_players_but_zero_score(self):
        """Test season where all players have zero score."""
        comparison = SeasonComparison(["20222023"])

        # Create mock players with zero scores
        player1 = Mock()
        player1.full_score = 0
        player2 = Mock()
        player2.full_score = 0

        comparison.add_season_data("20222023", {}, [player1, player2])

        report = comparison.generate_text_report()
        assert "20222023" in report
        assert "Players: 2" in report
        assert "Average per Player: 0.00" in report

    def test_multiple_seasons_with_mixed_player_counts(self):
        """Test comparison with some seasons having zero players."""
        comparison = SeasonComparison(["20212022", "20222023", "20232024"])

        # Season with no players
        comparison.add_season_data("20212022", {}, [])

        # Season with players
        player = Mock()
        player.full_score = 100
        comparison.add_season_data("20222023", {}, [player])

        # Another season with no players
        comparison.add_season_data("20232024", {}, [])

        report = comparison.generate_text_report()
        assert "20212022" in report
        assert "20222023" in report
        assert "20232024" in report

    def test_json_report_with_zero_players(self):
        """Test JSON report generation with zero player count."""
        comparison = SeasonComparison(["20222023"])

        comparison.add_season_data("20222023", {}, [])

        report = comparison.generate_json_report()
        assert "20222023" in report["comparison"]
        assert report["comparison"]["20222023"]["player_count"] == 0
        assert report["comparison"]["20222023"]["average_per_player"] == 0

    def test_missing_season_data_in_text_report(self):
        """Test text report when season data is missing."""
        comparison = SeasonComparison(["20222023", "20232024"])

        # Only add data for one season
        player = Mock()
        player.full_score = 50
        comparison.add_season_data("20222023", {}, [player])
        # Don't add data for 20232024

        report = comparison.generate_text_report()
        assert "20222023" in report
        assert "20232024" in report
        assert "No data available" in report

    def test_missing_season_data_in_json_report(self):
        """Test JSON report when season data is missing."""
        comparison = SeasonComparison(["20222023", "20232024"])

        # Only add data for one season
        comparison.add_season_data("20222023", {}, [])

        report = comparison.generate_json_report()
        assert "20232024" in report["comparison"]
        assert report["comparison"]["20232024"]["error"] == "No data available"

    def test_top_teams_with_valid_data(self):
        """Test top teams section with valid team data."""
        comparison = SeasonComparison(["20222023"])

        # Create mock teams with attributes
        team1 = TeamScore(
            abbrev="WSH",
            name="Washington Capitals",
            total=1500,
            players=[],
            division="Metropolitan",
            conference="Eastern",
        )
        team2 = TeamScore(
            abbrev="PIT",
            name="Pittsburgh Penguins",
            total=1400,
            players=[],
            division="Metropolitan",
            conference="Eastern",
        )

        teams = {"WSH": team1, "PIT": team2}
        comparison.add_season_data("20222023", teams, [])

        report = comparison.generate_text_report()
        assert "TOP TEAMS BY SEASON" in report
        assert "WSH" in report
        assert "1,500" in report or "1500" in report


class TestTrendAnalysisEdgeCases:
    """Test edge cases for TrendAnalysis."""

    def test_single_season_trend_analysis(self):
        """Test trend analysis with only one season (insufficient data)."""
        analysis = TrendAnalysis("20222023", "20222023")

        player = Mock()
        player.full_score = 100
        analysis.add_season_data("20222023", {}, [player])

        trends = analysis.calculate_trends()
        assert trends["seasons_analyzed"] == 1
        assert "error" in trends
        assert "Need at least 2 seasons" in trends["error"]

    def test_trend_analysis_with_zero_players(self):
        """Test trend analysis when seasons have zero players."""
        analysis = TrendAnalysis("20212022", "20222023")

        # Both seasons with zero players
        analysis.add_season_data("20212022", {}, [])
        analysis.add_season_data("20222023", {}, [])

        trends = analysis.calculate_trends()
        # When player_count is 0, average is not added to list
        # So we should have empty averages list
        assert trends["seasons_analyzed"] == 2

    def test_trend_analysis_increasing_trend(self):
        """Test trend analysis with increasing scores."""
        analysis = TrendAnalysis("20212022", "20222023")

        # First season: lower average
        player1 = Mock()
        player1.full_score = 50
        analysis.add_season_data("20212022", {}, [player1])

        # Second season: higher average
        player2 = Mock()
        player2.full_score = 100
        analysis.add_season_data("20222023", {}, [player2])

        trends = analysis.calculate_trends()
        assert trends["trend_direction"] == "increasing"
        assert trends["total_change"] > 0
        assert trends["percent_change"] > 0

    def test_trend_analysis_decreasing_trend(self):
        """Test trend analysis with decreasing scores."""
        analysis = TrendAnalysis("20212022", "20222023")

        # First season: higher average
        player1 = Mock()
        player1.full_score = 100
        analysis.add_season_data("20212022", {}, [player1])

        # Second season: lower average
        player2 = Mock()
        player2.full_score = 50
        analysis.add_season_data("20222023", {}, [player2])

        trends = analysis.calculate_trends()
        assert trends["trend_direction"] == "decreasing"
        assert trends["total_change"] < 0
        assert trends["percent_change"] < 0

    def test_trend_analysis_stable_trend(self):
        """Test trend analysis with stable scores."""
        analysis = TrendAnalysis("20212022", "20222023")

        # Both seasons: same average
        player1 = Mock()
        player1.full_score = 100
        player2 = Mock()
        player2.full_score = 100

        analysis.add_season_data("20212022", {}, [player1])
        analysis.add_season_data("20222023", {}, [player2])

        trends = analysis.calculate_trends()
        assert trends["trend_direction"] == "stable"
        assert trends["total_change"] == 0
        assert trends["percent_change"] == 0

    def test_trend_analysis_with_zero_first_average(self):
        """Test trend analysis when first season has zero average."""
        analysis = TrendAnalysis("20212022", "20222023")

        # First season: zero average (players with zero scores)
        player1 = Mock()
        player1.full_score = 0
        analysis.add_season_data("20212022", {}, [player1])

        # Second season: positive average
        player2 = Mock()
        player2.full_score = 100
        analysis.add_season_data("20222023", {}, [player2])

        trends = analysis.calculate_trends()
        # Should handle division by zero in percent change calculation
        assert trends["percent_change"] == 0  # Default when first_avg is 0

    def test_text_report_with_error(self):
        """Test text report generation when error occurs."""
        analysis = TrendAnalysis("20222023", "20222023")

        # Only one season - will cause error
        player = Mock()
        player.full_score = 100
        analysis.add_season_data("20222023", {}, [player])

        report = analysis.generate_text_report()
        assert "Error:" in report
        assert "Need at least 2 seasons" in report

    def test_text_report_with_valid_trends(self):
        """Test text report generation with valid trend data."""
        analysis = TrendAnalysis("20212022", "20222023")

        # Add data for two seasons
        player1 = Mock()
        player1.full_score = 50
        player2 = Mock()
        player2.full_score = 100

        analysis.add_season_data("20212022", {}, [player1])
        analysis.add_season_data("20222023", {}, [player2])

        report = analysis.generate_text_report()
        assert "Trend Direction:" in report
        assert "INCREASING" in report
        assert "Total Change:" in report
        assert "Percent Change:" in report
        assert "SEASON AVERAGES:" in report

    def test_text_report_season_averages_iteration(self):
        """Test text report iterates correctly over season averages."""
        analysis = TrendAnalysis("20202021", "20232024")

        # Add multiple seasons
        for i, season in enumerate(["20202021", "20212022", "20222023"]):
            player = Mock()
            player.full_score = 50 + (i * 10)
            analysis.add_season_data(season, {}, [player])

        report = analysis.generate_text_report()
        # Check that all seasons appear in averages
        assert "20202021" in report
        assert "20212022" in report
        assert "20222023" in report
        assert "points per player" in report

    def test_three_or_more_seasons_trend(self):
        """Test trend analysis with three or more seasons."""
        analysis = TrendAnalysis("20202021", "20222023")

        # Add three seasons
        for i, season in enumerate(["20202021", "20212022", "20222023"]):
            player = Mock()
            player.full_score = 50 + (i * 20)
            analysis.add_season_data(season, {}, [player])

        trends = analysis.calculate_trends()
        assert trends["seasons_analyzed"] == 3
        assert len(trends["average_scores"]) == 3
        assert trends["trend_direction"] == "increasing"
