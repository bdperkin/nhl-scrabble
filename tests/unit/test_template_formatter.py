"""Unit tests for TemplateFormatter class."""

from pathlib import Path

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import TemplateFormatter


class TestTemplateFormatter:
    """Tests for TemplateFormatter class."""

    def test_format_with_template(
        self,
        tmp_path: Path,
    ) -> None:
        """Test template formatting with custom template."""
        template_file = tmp_path / "template.j2"
        template_file.write_text(
            "Gaps: {{ coverage_gaps|length }}\n" "Trend: {{ coverage_trend }}",
        )

        sample_gaps = [
            CoverageGap(
                module="src/api/client.py",
                current_coverage=85.5,
                target_coverage=90.0,
                lines_needed=12,
                priority="high",
            ),
        ]

        formatter = TemplateFormatter(str(template_file))
        data = {"coverage_gaps": sample_gaps, "coverage_trend": "improving"}
        result = formatter.format(data)

        assert "Gaps: 1" in result
        assert "Trend: improving" in result

    def test_format_without_template(
        self,
    ) -> None:
        """Test template formatter requires template path."""
        formatter = TemplateFormatter()
        data = {"coverage_gaps": []}

        with pytest.raises(ValueError, match="Template path required"):
            formatter.format(data)

    def test_format_with_timestamp(
        self,
        tmp_path: Path,
    ) -> None:
        """Test template includes timestamp."""
        template_file = tmp_path / "template.j2"
        template_file.write_text("Time: {{ timestamp }}")

        formatter = TemplateFormatter(str(template_file))
        result = formatter.format({})

        assert "Time: " in result
        # Should have ISO format timestamp
        assert "T" in result  # ISO format separator

    def test_format_with_all_data(
        self,
        tmp_path: Path,
    ) -> None:
        """Test template with all data types."""
        template_file = tmp_path / "template.j2"
        template_file.write_text(
            "{% if coverage_gaps %}Gaps{% endif %}\n"
            "{% if slow_tests %}Slow{% endif %}\n"
            "{% if flaky_tests %}Flaky{% endif %}\n"
            "{% if coverage_trend %}Trend{% endif %}",
        )

        sample_gaps = [
            CoverageGap(
                module="src/api/client.py",
                current_coverage=85.5,
                target_coverage=90.0,
                lines_needed=12,
                priority="high",
            ),
        ]

        sample_tests = [
            TestPerformance(
                test_name="test_api_fetch",
                avg_duration=2.45,
                max_duration=3.21,
                min_duration=1.89,
                failure_rate=0.05,
                flakiness_score=0.123,
            ),
        ]

        formatter = TemplateFormatter(str(template_file))
        data = {
            "coverage_gaps": sample_gaps,
            "slow_tests": sample_tests,
            "flaky_tests": sample_tests,
            "coverage_trend": "improving",
        }
        result = formatter.format(data)

        assert "Gaps" in result
        assert "Slow" in result
        assert "Flaky" in result
        assert "Trend" in result
