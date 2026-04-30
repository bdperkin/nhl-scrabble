"""Unit tests for test analytics analyzer."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestAnalyzer, TestPerformance


class TestCoverageGap:
    """Tests for CoverageGap dataclass."""

    def test_coverage_gap_creation(self) -> None:
        """Test creating a coverage gap instance."""
        gap = CoverageGap(
            module="src/example.py",
            current_coverage=50.0,
            target_coverage=90.0,
            lines_needed=40,
            priority="high",
        )

        assert gap.module == "src/example.py"
        assert gap.current_coverage == 50.0
        assert gap.target_coverage == 90.0
        assert gap.lines_needed == 40
        assert gap.priority == "high"


class TestTestPerformance:
    """Tests for TestPerformance dataclass."""

    def test_test_performance_creation(self) -> None:
        """Test creating a test performance instance."""
        perf = TestPerformance(
            test_name="tests/test_example.py::test_function",
            avg_duration=1.5,
            max_duration=2.0,
            min_duration=1.0,
            failure_rate=0.1,
            flakiness_score=0.5,
        )

        assert perf.test_name == "tests/test_example.py::test_function"
        assert perf.avg_duration == 1.5
        assert perf.max_duration == 2.0
        assert perf.min_duration == 1.0
        assert perf.failure_rate == 0.1
        assert perf.flakiness_score == 0.5


class TestTestAnalyzer:
    """Tests for TestAnalyzer."""

    @pytest.fixture
    def sample_coverage_data(self) -> dict:
        """Sample coverage data for testing."""
        return {
            "files": [
                {
                    "name": "src/low_coverage.py",
                    "totals": {"coverage": 50.0, "lines": 100, "hits": 50},
                },
                {
                    "name": "src/medium_coverage.py",
                    "totals": {"coverage": 80.0, "lines": 100, "hits": 80},
                },
                {
                    "name": "src/high_coverage.py",
                    "totals": {"coverage": 95.0, "lines": 100, "hits": 95},
                },
            ]
        }

    @pytest.fixture
    def sample_test_data(self) -> dict:
        """Sample test analytics data for testing."""
        return {
            "test_analytics": {
                "tests": [
                    {
                        "name": "test_slow",
                        "avg_duration": 10.0,
                        "max_duration": 15.0,
                        "min_duration": 8.0,
                        "failure_rate": 0.05,
                    },
                    {
                        "name": "test_fast",
                        "avg_duration": 0.1,
                        "max_duration": 0.2,
                        "min_duration": 0.05,
                        "failure_rate": 0.0,
                    },
                    {
                        "name": "test_flaky",
                        "avg_duration": 1.0,
                        "max_duration": 1.5,
                        "min_duration": 0.5,
                        "failure_rate": 0.5,  # 50% failure = very flaky
                    },
                ]
            }
        }

    def test_analyzer_initialization(self, sample_coverage_data: dict) -> None:
        """Test analyzer initialization."""
        analyzer = TestAnalyzer(sample_coverage_data)

        assert analyzer.data == sample_coverage_data

    def test_find_coverage_gaps_default_target(
        self,
        sample_coverage_data: dict,
    ) -> None:
        """Test finding coverage gaps with default target."""
        analyzer = TestAnalyzer(sample_coverage_data)
        gaps = analyzer.find_coverage_gaps(target_coverage=90.0)

        # Should find 2 files below 90%: low_coverage (50%) and medium_coverage (80%)
        assert len(gaps) == 2

        # Should be sorted by current coverage (lowest first)
        assert gaps[0].module == "src/low_coverage.py"
        assert gaps[0].current_coverage == 50.0
        assert gaps[0].target_coverage == 90.0
        assert gaps[0].lines_needed == 40  # (100 * 90 / 100) - 50 = 40
        assert gaps[0].priority == "high"  # gap > 30%

        assert gaps[1].module == "src/medium_coverage.py"
        assert gaps[1].current_coverage == 80.0
        assert gaps[1].target_coverage == 90.0
        assert gaps[1].lines_needed == 10  # (100 * 90 / 100) - 80 = 10
        assert gaps[1].priority == "low"  # gap <= 15%

    def test_find_coverage_gaps_custom_target(
        self,
        sample_coverage_data: dict,
    ) -> None:
        """Test finding coverage gaps with custom target."""
        analyzer = TestAnalyzer(sample_coverage_data)
        gaps = analyzer.find_coverage_gaps(target_coverage=85.0)

        # Should find 2 files below 85%: low_coverage (50%) and medium_coverage (80%)
        assert len(gaps) == 2
        assert gaps[0].target_coverage == 85.0

    def test_find_coverage_gaps_priority_levels(self) -> None:
        """Test coverage gap priority level assignment."""
        data = {
            "files": [
                {
                    "name": "high_priority.py",
                    "totals": {"coverage": 50.0, "lines": 100, "hits": 50},
                },  # 40% gap = high
                {
                    "name": "medium_priority.py",
                    "totals": {"coverage": 70.0, "lines": 100, "hits": 70},
                },  # 20% gap = medium
                {
                    "name": "low_priority.py",
                    "totals": {"coverage": 85.0, "lines": 100, "hits": 85},
                },  # 5% gap = low
            ]
        }

        analyzer = TestAnalyzer(data)
        gaps = analyzer.find_coverage_gaps(target_coverage=90.0)

        # Check priority assignments
        gap_dict = {gap.module: gap.priority for gap in gaps}
        assert gap_dict["high_priority.py"] == "high"  # gap > 30%
        assert gap_dict["medium_priority.py"] == "medium"  # 15% < gap <= 30%
        assert gap_dict["low_priority.py"] == "low"  # gap <= 15%

    def test_find_coverage_gaps_no_gaps(self) -> None:
        """Test finding coverage gaps when all files meet target."""
        data = {
            "files": [
                {
                    "name": "perfect_coverage.py",
                    "totals": {"coverage": 100.0, "lines": 100, "hits": 100},
                },
                {
                    "name": "great_coverage.py",
                    "totals": {"coverage": 95.0, "lines": 100, "hits": 95},
                },
            ]
        }

        analyzer = TestAnalyzer(data)
        gaps = analyzer.find_coverage_gaps(target_coverage=90.0)

        assert len(gaps) == 0

    def test_analyze_test_performance(self, sample_test_data: dict) -> None:
        """Test test performance analysis."""
        analyzer = TestAnalyzer(sample_test_data)
        performances = analyzer.analyze_test_performance()

        # Should return 3 tests, sorted by avg_duration (slowest first)
        assert len(performances) == 3
        assert performances[0].test_name == "test_slow"
        assert performances[0].avg_duration == 10.0
        assert performances[0].max_duration == 15.0
        assert performances[0].min_duration == 8.0
        assert performances[0].failure_rate == 0.05

        assert performances[1].test_name == "test_flaky"
        assert performances[1].avg_duration == 1.0

        assert performances[2].test_name == "test_fast"
        assert performances[2].avg_duration == 0.1

    def test_analyze_test_performance_empty_data(self) -> None:
        """Test test performance analysis with no test data."""
        analyzer = TestAnalyzer({"test_analytics": {"tests": []}})
        performances = analyzer.analyze_test_performance()

        assert len(performances) == 0

    def test_calculate_flakiness_consistent_passing(
        self,
        sample_test_data: dict,
    ) -> None:
        """Test flakiness calculation for consistently passing test."""
        analyzer = TestAnalyzer(sample_test_data)

        # Test with 0% failure rate (100% pass)
        test = {"failure_rate": 0.0}
        flakiness = analyzer._calculate_flakiness(test)

        # Should be 0.0 (consistent)
        assert flakiness == 0.0

    def test_calculate_flakiness_consistent_failing(
        self,
        sample_test_data: dict,
    ) -> None:
        """Test flakiness calculation for consistently failing test."""
        analyzer = TestAnalyzer(sample_test_data)

        # Test with 100% failure rate (0% pass)
        test = {"failure_rate": 1.0}
        flakiness = analyzer._calculate_flakiness(test)

        # Should be 0.0 (consistent, even though always failing)
        assert flakiness == 0.0

    def test_calculate_flakiness_very_flaky(
        self,
        sample_test_data: dict,
    ) -> None:
        """Test flakiness calculation for very flaky test."""
        analyzer = TestAnalyzer(sample_test_data)

        # Test with 50% failure rate (50% pass) = maximally flaky
        test = {"failure_rate": 0.5}
        flakiness = analyzer._calculate_flakiness(test)

        # Should be 1.0 (very flaky)
        assert flakiness == 1.0

    def test_calculate_flakiness_somewhat_flaky(
        self,
        sample_test_data: dict,
    ) -> None:
        """Test flakiness calculation for somewhat flaky test."""
        analyzer = TestAnalyzer(sample_test_data)

        # Test with 25% failure rate (75% pass)
        test = {"failure_rate": 0.25}
        flakiness = analyzer._calculate_flakiness(test)

        # Should be 0.5 (somewhat flaky)
        # Formula: 1 - |0.75 - 0.5| * 2 = 1 - 0.25 * 2 = 1 - 0.5 = 0.5
        assert flakiness == 0.5

    def test_get_coverage_trend_improving(self) -> None:
        """Test coverage trend detection for improving coverage."""
        trends = [
            {"coverage": 88.0},  # Recent (avg = 87)
            {"coverage": 87.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 88.0},
            {"coverage": 85.0},  # Older (avg = 84)
            {"coverage": 84.0},
            {"coverage": 83.0},
            {"coverage": 84.0},
            {"coverage": 83.0},
            {"coverage": 84.0},
            {"coverage": 85.0},
        ]

        analyzer = TestAnalyzer({})
        trend = analyzer.get_coverage_trend(trends)

        # Recent avg (87) > Older avg (84) by > 1% = improving
        assert trend == "improving"

    def test_get_coverage_trend_declining(self) -> None:
        """Test coverage trend detection for declining coverage."""
        trends = [
            {"coverage": 83.0},  # Recent (avg = 84)
            {"coverage": 84.0},
            {"coverage": 85.0},
            {"coverage": 84.0},
            {"coverage": 83.0},
            {"coverage": 84.0},
            {"coverage": 85.0},
            {"coverage": 87.0},  # Older (avg = 87)
            {"coverage": 88.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 88.0},
        ]

        analyzer = TestAnalyzer({})
        trend = analyzer.get_coverage_trend(trends)

        # Recent avg (84) < Older avg (87) by > 1% = declining
        assert trend == "declining"

    def test_get_coverage_trend_stable(self) -> None:
        """Test coverage trend detection for stable coverage."""
        trends = [
            {"coverage": 85.0},  # Recent (avg ~85)
            {"coverage": 85.5},
            {"coverage": 84.5},
            {"coverage": 85.0},
            {"coverage": 85.0},
            {"coverage": 85.5},
            {"coverage": 84.5},
            {"coverage": 85.0},  # Older (avg ~85)
            {"coverage": 85.5},
            {"coverage": 84.5},
            {"coverage": 85.0},
            {"coverage": 85.0},
            {"coverage": 85.5},
            {"coverage": 84.5},
        ]

        analyzer = TestAnalyzer({})
        trend = analyzer.get_coverage_trend(trends)

        # Recent avg ≈ Older avg (diff < 1%) = stable
        assert trend == "stable"

    def test_get_coverage_trend_insufficient_data(self) -> None:
        """Test coverage trend with insufficient data."""
        # Only 1 data point
        trends = [{"coverage": 85.0}]

        analyzer = TestAnalyzer({})
        trend = analyzer.get_coverage_trend(trends)

        assert trend == "insufficient_data"

        # Empty data
        trends = []
        trend = analyzer.get_coverage_trend(trends)

        assert trend == "insufficient_data"

    def test_get_coverage_trend_partial_data(self) -> None:
        """Test coverage trend with partial data (< 14 commits)."""
        # Only 10 commits total (7 recent, 3 older)
        trends = [
            {"coverage": 88.0},  # Recent 7
            {"coverage": 87.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 86.0},
            {"coverage": 87.0},
            {"coverage": 88.0},
            {"coverage": 84.0},  # Older 3
            {"coverage": 83.0},
            {"coverage": 84.0},
        ]

        analyzer = TestAnalyzer({})
        trend = analyzer.get_coverage_trend(trends)

        # Should still calculate trend with available data
        assert trend in ["improving", "declining", "stable"]
