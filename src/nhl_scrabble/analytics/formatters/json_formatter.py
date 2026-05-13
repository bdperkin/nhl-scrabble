"""JSON formatter for test analytics data."""

import json
from typing import Any


class JSONFormatter:
    """Format analytics data as JSON.

    Converts analytics data structures to JSON for programmatic consumption.

    Example:
        >>> formatter = JSONFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> data = json.loads(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as JSON.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: JSON-formatted string.
        """
        # Convert dataclasses to dicts for JSON serialization
        serializable_data = {}

        if "coverage_gaps" in data:
            serializable_data["coverage_gaps"] = [
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
            serializable_data["slow_tests"] = [
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
            serializable_data["flaky_tests"] = [
                {
                    "test_name": test.test_name,
                    "flakiness_score": test.flakiness_score,
                    "failure_rate": test.failure_rate,
                    "avg_duration": test.avg_duration,
                }
                for test in data["flaky_tests"]
            ]

        if "coverage_trend" in data:
            serializable_data["coverage_trend"] = data["coverage_trend"]

        if "coverage_history" in data:
            serializable_data["coverage_history"] = data["coverage_history"]

        return json.dumps(serializable_data, indent=2, default=str)
