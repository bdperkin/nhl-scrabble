"""Unit tests for YAMLFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import YAMLFormatter


class TestYAMLFormatter:
    """Tests for YAMLFormatter class."""

    @pytest.fixture
    def formatter(self) -> YAMLFormatter:
        """Create YAMLFormatter instance."""
        return YAMLFormatter()

    @pytest.fixture
    def sample_gaps(self) -> list[CoverageGap]:
        """Create sample coverage gaps."""
        return [
            CoverageGap(
                module="src/api/client.py",
                current_coverage=85.5,
                target_coverage=90.0,
                lines_needed=12,
                priority="high",
            ),
        ]

    @pytest.fixture
    def sample_tests(self) -> list[TestPerformance]:
        """Create sample test performance data."""
        return [
            TestPerformance(
                test_name="test_api_fetch",
                avg_duration=2.45,
                max_duration=3.21,
                min_duration=1.89,
                failure_rate=0.05,
                flakiness_score=0.123,
            ),
        ]

    def test_format_coverage_gaps(
        self,
        formatter: YAMLFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test YAML formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        # Parse YAML and verify structure
        import yaml

        parsed = yaml.safe_load(result)

        assert "coverage_gaps" in parsed
        assert len(parsed["coverage_gaps"]) == 1
        assert parsed["coverage_gaps"][0]["module"] == "src/api/client.py"
        assert parsed["coverage_gaps"][0]["current_coverage"] == 85.5
        assert parsed["coverage_gaps"][0]["priority"] == "high"

    def test_format_slow_tests(
        self,
        formatter: YAMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test YAML formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "slow_tests" in parsed
        assert len(parsed["slow_tests"]) == 1
        assert parsed["slow_tests"][0]["test_name"] == "test_api_fetch"
        assert parsed["slow_tests"][0]["avg_duration"] == 2.45

    def test_format_empty_data(
        self,
        formatter: YAMLFormatter,
    ) -> None:
        """Test YAML formatting with empty data."""
        data = {}
        result = formatter.format(data)

        assert result == "{}\n"
