"""Template formatter for test analytics data."""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class TemplateFormatter:
    """Format analytics data using custom Jinja2 template.

    Allows users to provide a custom Jinja2 template file for flexible
    output formatting.

    Template variables available:
        - coverage_gaps: List of coverage gap data
        - slow_tests: List of slow test data
        - flaky_tests: List of flaky test data
        - coverage_trend: Trend status string
        - coverage_history: Historical coverage data
        - timestamp: Current timestamp

    Example:
        >>> formatter = TemplateFormatter("/path/to/template.j2")
        >>> output = formatter.format({"coverage_gaps": gaps})
    """

    def __init__(self, template_path: str | None = None) -> None:
        """Initialize template formatter.

        Args:
            template_path: Path to Jinja2 template file. If not provided,
                will check NHL_SCRABBLE_ANALYTICS_TEMPLATE environment variable.
        """
        self.template_path = template_path or os.getenv(
            "NHL_SCRABBLE_ANALYTICS_TEMPLATE",
        )

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data using template.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: Formatted output from template.

        Raises:
            ValueError: If template path is not provided.
        """
        from jinja2 import (  # noqa: PLC0415  # lazy import for optional dependency
            Environment,
            FileSystemLoader,
            select_autoescape,
        )

        if not self.template_path:
            msg = (
                "Template path required. Set NHL_SCRABBLE_ANALYTICS_TEMPLATE "
                "or use --template option."
            )
            raise ValueError(msg)

        template = Environment(
            loader=FileSystemLoader(Path(self.template_path).parent),
            autoescape=select_autoescape(),
        ).get_template(Path(self.template_path).name)

        # Convert dataclasses to dicts for template rendering

        render_data: dict[str, Any] = {"timestamp": datetime.now(tz=UTC).isoformat()}  # type: ignore[explicit-any]

        if "coverage_gaps" in data:
            render_data["coverage_gaps"] = [
                {
                    "module": gap.module,
                    "current_coverage": gap.current_coverage,
                    "target_coverage": gap.target_coverage,
                    "lines_needed": gap.lines_needed,
                    "priority": gap.priority,
                }
                for gap in data["coverage_gaps"]
            ]

        if "slow_tests" in data:
            render_data["slow_tests"] = [
                {
                    "test_name": test.test_name,
                    "avg_duration": test.avg_duration,
                    "max_duration": test.max_duration,
                    "min_duration": test.min_duration,
                    "failure_rate": test.failure_rate,
                    "flakiness_score": test.flakiness_score,
                }
                for test in data["slow_tests"]
            ]

        if "flaky_tests" in data:
            render_data["flaky_tests"] = [
                {
                    "test_name": test.test_name,
                    "flakiness_score": test.flakiness_score,
                    "failure_rate": test.failure_rate,
                    "avg_duration": test.avg_duration,
                }
                for test in data["flaky_tests"]
            ]

        if "coverage_trend" in data:
            render_data["coverage_trend"] = data["coverage_trend"]

        if "coverage_history" in data:
            render_data["coverage_history"] = data["coverage_history"]

        return template.render(**render_data)
