"""HTML formatter for test analytics data."""

from typing import Any

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance


class HTMLFormatter:
    """Format analytics data as HTML.

    Generates HTML tables and styled output for web display.

    Example:
        >>> formatter = HTMLFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> Path("report.html").write_text(output)
    """

    def _format_coverage_gaps_html(self, gaps: list[CoverageGap]) -> str:
        """Format coverage gaps as HTML table.

        Args:
            gaps: List of CoverageGap instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Coverage Gaps</h2>", "<table>", "<tr>"]
        html.append("<th>Module</th>")
        html.append("<th>Current</th>")
        html.append("<th>Target</th>")
        html.append("<th>Lines Needed</th>")
        html.append("<th>Priority</th>")
        html.append("</tr>")

        for gap in gaps[:20]:  # Show top 20
            html.append("<tr>")
            html.append(f"<td>{gap.module}</td>")
            html.append(f"<td>{gap.current_coverage:.1f}%</td>")
            html.append(f"<td>{gap.target_coverage:.1f}%</td>")
            html.append(f"<td>{gap.lines_needed}</td>")
            html.append(
                f'<td class="{gap.priority}">{gap.priority.upper()}</td>',
            )
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_slow_tests_html(self, tests: list[TestPerformance]) -> str:
        """Format slow tests as HTML table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Slowest Tests</h2>", "<table>", "<tr>"]
        html.append("<th>Test</th>")
        html.append("<th>Avg Duration</th>")
        html.append("<th>Max Duration</th>")
        html.append("<th>Failure Rate</th>")
        html.append("</tr>")

        for test in tests:
            html.append("<tr>")
            html.append(f"<td>{test.test_name}</td>")
            html.append(f"<td>{test.avg_duration:.2f}s</td>")
            html.append(f"<td>{test.max_duration:.2f}s</td>")
            html.append(f"<td>{test.failure_rate * 100:.1f}%</td>")
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_flaky_tests_html(self, tests: list[TestPerformance]) -> str:
        """Format flaky tests as HTML table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Flaky Tests</h2>", "<table>", "<tr>"]
        html.append("<th>Test</th>")
        html.append("<th>Flakiness Score</th>")
        html.append("<th>Failure Rate</th>")
        html.append("</tr>")

        for test in tests:
            html.append("<tr>")
            html.append(f"<td>{test.test_name}</td>")
            html.append(f"<td>{test.flakiness_score:.3f}</td>")
            html.append(f"<td>{test.failure_rate * 100:.1f}%</td>")
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_trends_html(  # type: ignore[explicit-any]
        self,
        trend: str,
        history: list[dict[str, Any]],
    ) -> str:
        """Format coverage trend as HTML.

        Args:
            trend: Trend status.
            history: Historical coverage data.

        Returns:
            str: HTML div string.
        """
        trend_emoji = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️",
            "insufficient_data": "❓",
        }.get(trend, "")

        current = history[0]["coverage"] if history else 0
        oldest = history[-1]["coverage"] if len(history) > 1 else 0
        change = current - oldest

        html = ['<div class="trend">', "<h2>Coverage Trends</h2>"]
        html.append(f"<p>{trend_emoji} <strong>Trend:</strong> {trend.upper()}</p>")
        html.append(f"<p><strong>Current:</strong> {current:.1f}%</p>")
        html.append(f"<p><strong>Change (30 days):</strong> {change:+.1f}%</p>")
        html.append("</div>")

        return "\n".join(html)

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as HTML.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: HTML-formatted string.
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Test Analytics Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1 { color: #333; }",
            "h2 { color: #666; margin-top: 30px; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #4CAF50; color: white; }",
            "tr:nth-child(even) { background-color: #f2f2f2; }",
            ".high { color: red; font-weight: bold; }",
            ".medium { color: orange; font-weight: bold; }",
            ".low { color: green; font-weight: bold; }",
            ".trend { padding: 20px; background-color: #e7f3ff; border-left: 4px solid #2196F3; margin: 20px 0; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Test Analytics Report</h1>",
        ]

        # Coverage gaps
        if "coverage_gaps" in data:
            html_parts.append(self._format_coverage_gaps_html(data["coverage_gaps"]))

        # Slow tests
        if "slow_tests" in data:
            html_parts.append(self._format_slow_tests_html(data["slow_tests"]))

        # Flaky tests
        if "flaky_tests" in data:
            html_parts.append(self._format_flaky_tests_html(data["flaky_tests"]))

        # Trends
        if "coverage_trend" in data:
            html_parts.append(
                self._format_trends_html(
                    data["coverage_trend"],
                    data.get("coverage_history", []),
                ),
            )

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)
