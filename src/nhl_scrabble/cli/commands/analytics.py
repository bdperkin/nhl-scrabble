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
    type=click.Choice(
        ["text", "json", "yaml", "xml", "html", "table", "markdown", "csv", "excel", "template"],
        case_sensitive=False,
    ),
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
    "--template",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Template file path (required for --format template)",
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
def test_analytics(  # noqa: PLR0913, PLR0915, C901  # CLI function with many options, statements, and conditional logic
    ctx: click.Context,
    output_format: str,
    output: str | None,
    template: str | None,
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

      Export to YAML:
        $ nhl-scrabble test-analytics --format yaml -o analytics.yaml

      Export to XML:
        $ nhl-scrabble test-analytics --format xml -o analytics.xml

      Export to Markdown:
        $ nhl-scrabble test-analytics --format markdown -o analytics.md

      Export to CSV:
        $ nhl-scrabble test-analytics --format csv -o analytics.csv

      Export to Excel:
        $ nhl-scrabble test-analytics --format excel -o analytics.xlsx

      Export with custom template:
        $ nhl-scrabble test-analytics --format template --template template.j2 -o report.txt

      Combine multiple analyses:
        $ nhl-scrabble test-analytics --show-gaps --show-slow-tests
    """
    from nhl_scrabble.analytics.analyzer import TestAnalyzer  # noqa: PLC0415
    from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig  # noqa: PLC0415
    from nhl_scrabble.analytics.formatters import (  # noqa: PLC0415
        CSVFormatter,
        ExcelFormatter,
        HTMLFormatter,
        JSONFormatter,
        MarkdownFormatter,
        TableFormatter,
        TemplateFormatter,
        TextFormatter,
        XMLFormatter,
        YAMLFormatter,
    )

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

        # Validate format requirements
        if output_format == "excel" and not output:
            console.print(
                "[red]Error: Excel format requires --output option[/red]",
                style="bold",
            )
            ctx.exit(1)

        if output_format == "template" and not template:
            console.print(
                "[red]Error: Template format requires --template option[/red]",
                style="bold",
            )
            ctx.exit(1)

        # Format output using formatter map
        formatter_map = {
            "json": JSONFormatter(),
            "yaml": YAMLFormatter(),
            "xml": XMLFormatter(),
            "html": HTMLFormatter(),
            "table": TableFormatter(),
            "markdown": MarkdownFormatter(),
            "csv": CSVFormatter(),
            "excel": ExcelFormatter(),
            "template": TemplateFormatter(template),
            "text": TextFormatter(),
        }

        formatter = formatter_map.get(output_format, TextFormatter())
        output_data = formatter.format(report_data)  # type: ignore[attr-defined]

        # Write or display output
        if output:
            output_path = Path(output)
            if output_format == "excel":
                # Excel returns bytes, write in binary mode
                output_path.write_bytes(output_data)
            else:
                # Other formats return str, write in text mode
                output_path.write_text(output_data, encoding="utf-8")
            console.print(f"[green]✓ Analytics report saved to {output}[/green]")
        else:
            console.print("\n" + "=" * 80)
            console.print(output_data)
            console.print("=" * 80)

    except Exception as e:
        logger.exception("Error fetching or analyzing test analytics")
        console.print(f"[red]Error: {e}[/red]", style="red")
        ctx.exit(1)
