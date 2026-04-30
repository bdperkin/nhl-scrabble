"""Test analytics and coverage analysis engine."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CoverageGap:
    """Represents a module with insufficient coverage.

    Attributes:
        module: Module file path.
        current_coverage: Current coverage percentage (0-100).
        target_coverage: Target coverage percentage (0-100).
        lines_needed: Number of additional lines needed to reach target.
        priority: Priority level ("high", "medium", "low").
    """

    module: str
    current_coverage: float
    target_coverage: float
    lines_needed: int
    priority: str


@dataclass
class TestPerformance:
    """Test performance metrics.

    Attributes:
        test_name: Full test name/path.
        avg_duration: Average test duration in seconds.
        max_duration: Maximum test duration in seconds.
        min_duration: Minimum test duration in seconds.
        failure_rate: Failure rate as decimal (0.0-1.0).
        flakiness_score: Flakiness score (0.0-1.0, higher = more flaky).
    """

    test_name: str
    avg_duration: float
    max_duration: float
    min_duration: float
    failure_rate: float
    flakiness_score: float


class TestAnalyzer:
    """Analyzes test and coverage data from Codecov.

    This analyzer processes coverage reports and test analytics to identify
    coverage gaps, slow tests, flaky tests, and coverage trends.

    Args:
        codecov_data: Combined data from Codecov API responses.

    Example:
        >>> data = {"files": [...], "test_analytics": {...}}
        >>> analyzer = TestAnalyzer(data)
        >>> gaps = analyzer.find_coverage_gaps(target_coverage=90.0)
    """

    def __init__(self, codecov_data: dict[str, Any]) -> None:  # type: ignore[explicit-any]
        """Initialize analyzer with Codecov data.

        Args:
            codecov_data: Combined data from Codecov API responses.
        """
        self.data = codecov_data

    def find_coverage_gaps(
        self,
        target_coverage: float = 90.0,
    ) -> list[CoverageGap]:
        """Identify modules with coverage below target threshold.

        Args:
            target_coverage: Target coverage percentage (0-100). Defaults to 90.

        Returns:
            list[CoverageGap]: List of coverage gaps sorted by current coverage
                (lowest first).
        """
        gaps = []
        files = self.data.get("files", [])

        for file_data in files:
            totals = file_data.get("totals", {})
            coverage = totals.get("coverage", 0)

            if coverage < target_coverage:
                total_lines = totals.get("lines", 0)
                covered_lines = totals.get("hits", 0)

                # Calculate lines needed to reach target
                needed = int((total_lines * target_coverage / 100) - covered_lines)

                # Prioritize based on gap size
                gap_size = target_coverage - coverage
                if gap_size > 30:
                    priority = "high"
                elif gap_size > 15:
                    priority = "medium"
                else:
                    priority = "low"

                gaps.append(
                    CoverageGap(
                        module=file_data["name"],
                        current_coverage=coverage,
                        target_coverage=target_coverage,
                        lines_needed=max(0, needed),  # Ensure non-negative
                        priority=priority,
                    ),
                )

        return sorted(gaps, key=lambda g: g.current_coverage)

    def _calculate_flakiness(self, test: dict[str, Any]) -> float:  # type: ignore[explicit-any]
        """Calculate flakiness score based on pass/fail patterns.

        A test is considered flaky if it has inconsistent pass/fail patterns.
        A test with ~50% pass rate is maximally flaky.
        A test with 0% or 100% pass rate is consistent (not flaky).

        Args:
            test: Test data dictionary with failure_rate.

        Returns:
            float: Flakiness score between 0.0 (consistent) and 1.0 (very flaky).
        """
        failure_rate = test.get("failure_rate", 0)
        pass_rate = 1 - failure_rate

        # If pass rate is near 50%, it's very flaky
        # If it's near 0% or 100%, it's consistent (not flaky)
        # Formula: 1 - |pass_rate - 0.5| * 2
        # Examples:
        #   pass_rate=0.5 -> flakiness=1.0 (very flaky)
        #   pass_rate=0.0 or 1.0 -> flakiness=0.0 (consistent)
        #   pass_rate=0.75 or 0.25 -> flakiness=0.5 (somewhat flaky)
        flakiness = 1 - abs(pass_rate - 0.5) * 2
        return round(flakiness, 3)  # type: ignore[no-any-return]

    def analyze_test_performance(self) -> list[TestPerformance]:
        """Analyze test execution performance metrics.

        Returns:
            list[TestPerformance]: List of test performance data sorted by
                average duration (slowest first).
        """
        test_data = self.data.get("test_analytics", {}).get("tests", [])

        performances = [
            TestPerformance(
                test_name=test["name"],
                avg_duration=test.get("avg_duration", 0),
                max_duration=test.get("max_duration", 0),
                min_duration=test.get("min_duration", 0),
                failure_rate=test.get("failure_rate", 0),
                flakiness_score=self._calculate_flakiness(test),
            )
            for test in test_data
        ]

        return sorted(performances, key=lambda p: p.avg_duration, reverse=True)

    def get_coverage_trend(  # type: ignore[explicit-any]
        self,
        trends: list[dict[str, Any]],
    ) -> str:
        """Determine if coverage is improving, declining, or stable.

        Compares recent week average to previous week average.

        Args:
            trends: List of coverage trend data from get_coverage_trends().

        Returns:
            str: Trend status - "improving", "declining", "stable", or
                "insufficient_data".
        """
        if len(trends) < 2:
            return "insufficient_data"

        # Compare recent 7 commits to previous 7 commits
        recent_count = min(7, len(trends[:7]))
        older_count = min(7, len(trends[7:14]))

        if 0 in (recent_count, older_count):
            return "insufficient_data"

        recent_avg = sum(t["coverage"] for t in trends[:7]) / recent_count
        older_avg = sum(t["coverage"] for t in trends[7:14]) / older_count

        diff = recent_avg - older_avg

        # Consider >1% change as significant
        if diff > 1.0:
            return "improving"
        if diff < -1.0:
            return "declining"
        return "stable"
