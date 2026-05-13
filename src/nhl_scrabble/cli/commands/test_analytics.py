"""Test analytics command for NHL Scrabble CLI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import click
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "html"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--target-coverage",
    type=click.FloatRange(min=0.0, max=100.0),
    default=90.0,
    help="Target coverage percentage (default: 90.0)",
)
@click.option(
    "--show-gaps",
    is_flag=True,
    help="Show coverage gaps analysis",
)
@click.option(
    "--show-slow-tests",
    is_flag=True,
    help="Show slowest tests analysis",
)
@click.option(
    "--show-flaky-tests",
    is_flag=True,
    help="Show flaky tests analysis",
)
@click.option(
    "--show-trends",
    is_flag=True,
    help="Show coverage trends analysis",
)
@click.help_option("-h", "--help")
@click.pass_context
def test_analytics(  # noqa: PLR0913, PLR0915  # CLI function with many options and statements
    ctx: click.Context,
    output_format: str,
    output: str | None,
    target_coverage: float,
    show_gaps: bool,
    show_slow_tests: bool,
    show_flaky_tests: bool,
    show_trends: bool,
) -> None:
    r"""Analyze test analytics and coverage data from Codecov.

    Fetches data from Codecov API to provide insights into test performance,
    coverage trends, and areas needing more testing attention.

    Requires CODECOV_TOKEN environment variable for API authentication.

    \b
    Examples:
      Show all analytics (default):
        $ nhl-scrabble test-analytics

      Show only coverage gaps with custom target:
        $ nhl-scrabble test-analytics --show-gaps --target-coverage 95

      Show slow tests:
        $ nhl-scrabble test-analytics --show-slow-tests

      Show flaky tests:
        $ nhl-scrabble test-analytics --show-flaky-tests

      Show coverage trends:
        $ nhl-scrabble test-analytics --show-trends

      Export to JSON:
        $ nhl-scrabble test-analytics --format json -o analytics.json

      Export to HTML:
        $ nhl-scrabble test-analytics --format html -o analytics.html

      Combine multiple analyses:
        $ nhl-scrabble test-analytics --show-gaps --show-slow-tests
    """
    from nhl_scrabble.analytics.analyzer import TestAnalyzer
    from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig
    from nhl_scrabble.analytics.formatters import HTMLFormatter, JSONFormatter, TextFormatter

    # Load configuration from environment
    config = CodecovConfig.from_env()
    if not config.token:
        console.print(
            "[red]Error: CODECOV_TOKEN environment variable not set[/red]",
            style="red",
        )
        console.print(
            "\n[yellow]Get your token from: https://app.codecov.io/account/gh/bdperkin/access[/yellow]",
        )
        console.print("[yellow]Then set it: export CODECOV_TOKEN='your-token-here'[/yellow]")
        ctx.exit(1)

    # Determine which analyses to show (default: all if none specified)
    show_all = not any([show_gaps, show_slow_tests, show_flaky_tests, show_trends])

    try:
        # Fetch data from Codecov API
        console.print("[cyan]Fetching data from Codecov API...[/cyan]")

        with CodecovClient(config) as client:
            analytics_data = client.get_test_analytics()
            coverage_data = client.get_coverage_report()
            trends_data = client.get_coverage_trends()

        console.print("[green]✓ Data fetched successfully[/green]")

        # Analyze data
        console.print("[cyan]Analyzing test analytics...[/cyan]")
        analyzer = TestAnalyzer(analytics_data | coverage_data)

        # Generate report data
        report_data: dict[str, Any] = {}

        if show_gaps or show_all:
            report_data["coverage_gaps"] = analyzer.find_coverage_gaps(target_coverage)

        if show_slow_tests or show_all:
            performances = analyzer.analyze_test_performance()
            report_data["slow_tests"] = performances[:10]  # Top 10 slowest

        if show_flaky_tests:
            performances = analyzer.analyze_test_performance()
            flaky = [p for p in performances if p.flakiness_score > 0.3]
            report_data["flaky_tests"] = flaky[:10]  # Top 10 flakiest

        if show_trends or show_all:
            report_data["coverage_trend"] = analyzer.get_coverage_trend(trends_data)
            report_data["coverage_history"] = trends_data[:30]  # Last 30 commits

        console.print("[green]✓ Analysis complete[/green]")

        # Format output
        formatter: JSONFormatter | HTMLFormatter | TextFormatter
        if output_format == "json":
            formatter = JSONFormatter()
            output_text = formatter.format(report_data)
        elif output_format == "html":
            formatter = HTMLFormatter()
            output_text = formatter.format(report_data)
        else:
            formatter = TextFormatter()
            output_text = formatter.format(report_data)

        # Write or display output
        if output:
            output_path = Path(output)
            output_path.write_text(output_text, encoding="utf-8")
            console.print(f"[green]✓ Analytics report saved to {output}[/green]")
        else:
            console.print("\n" + "=" * 80)
            console.print(output_text)
            console.print("=" * 80)

    except Exception as e:
        logger.exception("Error fetching or analyzing test analytics")
        console.print(f"[red]Error: {e}[/red]", style="red")
        ctx.exit(1)
