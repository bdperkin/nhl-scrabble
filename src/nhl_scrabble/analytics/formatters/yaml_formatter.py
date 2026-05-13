"""YAML formatter for test analytics data."""

from typing import Any


class YAMLFormatter:
    """Format analytics data as YAML.

    Outputs analytics data in YAML format for configuration files and
    human-readable structured data.

    Example:
        >>> formatter = YAMLFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> with open("analytics.yaml", "w") as f:
        ...     f.write(output)
    """

    def _convert_to_dict(self, data: dict[str, Any]) -> dict[str, Any]:  # type: ignore[explicit-any]
        """Convert dataclasses to dicts for serialization.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            dict: Serializable dictionary.
        """
        serializable_data: dict[str, Any] = {}  # type: ignore[explicit-any]

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

        return serializable_data

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as YAML.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: YAML-formatted string.
        """
        import yaml  # noqa: PLC0415  # lazy import for optional dependency

        serializable_data = self._convert_to_dict(data)
        return yaml.dump(serializable_data, default_flow_style=False, sort_keys=False)
