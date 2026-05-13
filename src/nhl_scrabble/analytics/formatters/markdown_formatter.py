"""Markdown formatter for test analytics data."""

from typing import Any


class MarkdownFormatter:
    """Format analytics data as Markdown.

    Outputs analytics data in Markdown format for documentation and GitHub.

    Example:
        >>> formatter = MarkdownFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> with open("analytics.md", "w") as f:
        ...     f.write(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as Markdown.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: Markdown-formatted string.
        """
        output = ["# Test Analytics Report\n"]

        # Coverage gaps
        if "coverage_gaps" in data:
            output.append("## Coverage Gaps\n")
            output.append("| Module | Current | Target | Lines Needed | Priority |")
            output.append("|--------|---------|--------|--------------|----------|")
            output.extend(
                [
                    f"| {gap.module} | {gap.current_coverage:.1f}% | "
                    f"{gap.target_coverage:.1f}% | {gap.lines_needed} | "
                    f"{gap.priority.upper()} |"
                    for gap in data["coverage_gaps"][:20]
                ],
            )
            output.append("")

        # Slow tests
        if "slow_tests" in data:
            output.append("## Slowest Tests\n")
            output.append("| Test | Avg Duration | Max Duration | Failure Rate |")
            output.append("|------|--------------|--------------|--------------|")
            output.extend(
                [
                    f"| {test.test_name} | {test.avg_duration:.2f}s | "
                    f"{test.max_duration:.2f}s | {test.failure_rate * 100:.1f}% |"
                    for test in data["slow_tests"]
                ],
            )
            output.append("")

        # Flaky tests
        if "flaky_tests" in data:
            output.append("## Flaky Tests\n")
            output.append("| Test | Flakiness Score | Failure Rate |")
            output.append("|------|-----------------|--------------|")
            output.extend(
                [
                    f"| {test.test_name} | {test.flakiness_score:.3f} | "
                    f"{test.failure_rate * 100:.1f}% |"
                    for test in data["flaky_tests"]
                ],
            )
            output.append("")

        # Coverage trend
        if "coverage_trend" in data:
            output.append("## Coverage Trends\n")
            trend = data["coverage_trend"]
            history = data.get("coverage_history", [])

            trend_emoji = {
                "improving": "📈",
                "declining": "📉",
                "stable": "➡️",
                "insufficient_data": "❓",
            }.get(trend, "")

            output.append(f"{trend_emoji} **Trend:** {trend.upper()}\n")

            if history:
                current = history[0]["coverage"]
                oldest = history[-1]["coverage"] if len(history) > 1 else 0
                change = current - oldest
                output.append(f"- **Current:** {current:.1f}%")
                output.append(f"- **Change (30 days):** {change:+.1f}%\n")

        return "\n".join(output)
