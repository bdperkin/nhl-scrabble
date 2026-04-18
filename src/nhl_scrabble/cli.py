"""Command-line interface for NHL Scrabble."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError
from nhl_scrabble.config import Config
from nhl_scrabble.exporters.csv_exporter import CSVExporter
from nhl_scrabble.exporters.excel_exporter import ExcelExporter
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.reports.generator import ReportGenerator
from nhl_scrabble.scoring.scrabble import ScrabbleScorer
from nhl_scrabble.ui.progress import ProgressManager

logger = logging.getLogger(__name__)
console = Console()


def validate_output_path(output: str | None) -> None:
    """Validate that output path is writable before processing.

    Checks that the output path's parent directory exists and is writable,
    and that any existing file at the path is also writable. This validation
    happens before any API calls to provide immediate feedback on path issues.

    Args:
        output: Output file path, or None for stdout.

    Raises:
        click.ClickException: If output path is not writable, with helpful
            error message explaining the issue and how to fix it.

    Example:
        >>> validate_output_path("/tmp/output.txt")  # OK
        >>> validate_output_path(None)  # OK (stdout)
        >>> validate_output_path("/nonexistent/dir/file.txt")  # Raises
        ClickException: Output directory does not exist: /nonexistent/dir
        Create it first: mkdir -p /nonexistent/dir
    """
    if output is None:
        return  # stdout is always writable

    # Resolve to absolute path
    output_path = Path(output).resolve()
    output_dir = output_path.parent

    # Check if directory exists
    if not output_dir.exists():
        raise click.ClickException(
            f"Output directory does not exist: {output_dir}\nCreate it first: mkdir -p {output_dir}"
        )

    # Check if directory is writable
    if not os.access(output_dir, os.W_OK):
        raise click.ClickException(
            f"Output directory is not writable: {output_dir}\n"
            f"Check permissions with: ls -ld {output_dir}"
        )

    # Check if file exists and is writable
    if output_path.exists():
        if not os.access(output_path, os.W_OK):
            raise click.ClickException(
                f"Output file exists but is not writable: {output_path}\n"
                f"Check permissions with: ls -l {output_path}"
            )

        # Warn if file will be overwritten
        logger.warning(f"Output file exists and will be overwritten: {output_path}")


@click.group()
@click.version_option(version=__version__, prog_name="nhl-scrabble")
def cli() -> None:
    """NHL Roster Scrabble Score Analyzer.

    Fetch NHL roster data and calculate Scrabble scores for player names. Generate comprehensive
    reports showing team, division, and conference standings.
    """


@cli.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv", "excel"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--sheets",
    help="Comma-separated list of sheets for Excel export (teams,players,divisions,conferences,playoffs)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress progress bars",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable API response caching (always fetch fresh data)",
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear API cache before running",
)
@click.option(
    "--top-players",
    type=int,
    default=20,
    help="Number of top players to show (default: 20)",
)
@click.option(
    "--top-team-players",
    type=int,
    default=5,
    help="Number of top players per team to show (default: 5)",
)
@click.option(
    "--report",
    type=click.Choice(["conference", "division", "playoff", "team", "stats"], case_sensitive=False),
    help="Generate specific report only (default: all reports)",
)
def analyze(  # noqa: PLR0913, C901  # CLI function needs many parameters and has complex logic
    output_format: str,
    sheets: str | None,
    output: str | None,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    clear_cache: bool,
    top_players: int,
    top_team_players: int,
    report: str | None,
) -> None:
    """Run the NHL Scrabble analysis.

    Fetches current NHL roster data and generates comprehensive reports
    with Scrabble scores for all players and teams.

    Examples:
        nhl-scrabble analyze
        nhl-scrabble analyze --verbose
        nhl-scrabble analyze --quiet
        nhl-scrabble analyze --output report.txt
        nhl-scrabble analyze --format json --output report.json
        nhl-scrabble analyze --format csv --output report.csv
        nhl-scrabble analyze --format excel --output report.xlsx
        nhl-scrabble analyze --format excel --sheets teams,players --output report.xlsx
        nhl-scrabble analyze --no-cache
        nhl-scrabble analyze --clear-cache
        nhl-scrabble analyze --report team
        nhl-scrabble analyze --report playoff --output playoffs.txt
    """
    # Load configuration first to get sanitize_logs setting
    config = Config.from_env()
    config.verbose = verbose
    config.output_format = output_format
    config.top_players_count = top_players
    config.top_team_players_count = top_team_players

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging with sanitization setting from config
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble analysis v{__version__}")
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Configuration: {config}")

    # Validate CSV/Excel require output file
    if output_format in ("csv", "excel") and not output:
        raise click.ClickException(
            f"{output_format.upper()} format requires --output option\n"
            f"Example: nhl-scrabble analyze --format {output_format} --output report.{output_format}"
        )

    # Validate output path BEFORE making API calls
    validate_output_path(output)

    # Display header (suppress if quiet mode)
    if not quiet:
        console.print("\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer 🏒[/bold cyan]\n")
        console.print("=" * 80)

    try:
        # Parse sheets list for Excel export
        sheets_list = None
        if sheets:
            sheets_list = [s.strip() for s in sheets.split(",")]

        # Run the analysis
        result = run_analysis(
            config,
            clear_cache=clear_cache,
            report_filter=report,
            quiet=quiet,
            output_path=Path(output) if output else None,
            sheets=sheets_list,
        )

        # Output results
        if output:
            output_path = Path(output)
            if isinstance(result, str):
                # Text/JSON output
                output_path.write_text(result)
            # CSV/Excel are written directly by exporters
            if not quiet:
                console.print(f"\n[green]✓[/green] Report saved to: {output}")
        elif isinstance(result, str):
            print(result)
        else:
            console.print(
                "\n[yellow]⚠[/yellow] CSV/Excel formats require --output option", style="yellow"
            )

        if not quiet:
            console.print("\n" + "=" * 80)
            console.print("[green]✓ Analysis complete![/green]")

    except NHLApiError as e:
        logger.error(f"NHL API error: {e}")
        console.print(f"\n[red]❌ NHL API Error: {e}[/red]", style="red")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]", style="red")
        sys.exit(1)


def run_analysis(
    config: Config,
    clear_cache: bool = False,
    report_filter: str | None = None,
    quiet: bool = False,
    output_path: Path | None = None,
    sheets: list[str] | None = None,
) -> str | None:
    """Run the complete NHL Scrabble analysis.

    Args:
        config: Configuration object
        clear_cache: Whether to clear the API cache before running
        report_filter: Optional filter for specific report type
            (conference, division, playoff, team, stats)
        quiet: Whether to suppress progress bars
        output_path: Optional output file path for CSV/Excel exports
        sheets: Optional list of sheets for Excel export

    Returns:
        Complete report string for text/JSON formats, or None for CSV/Excel
        (CSV/Excel are written directly to output file)

    Raises:
        NHLApiError: If there are issues fetching data from NHL API
    """
    # Initialize components
    api_client = NHLApiClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout,
        retries=config.api_retries,
        rate_limit_delay=config.rate_limit_delay,
        backoff_factor=config.backoff_factor,
        max_backoff=config.max_backoff,
        cache_enabled=config.cache_enabled,
        cache_expiry=config.cache_expiry,
    )

    # Clear cache if requested
    if clear_cache:
        api_client.clear_cache()
        logger.info("API cache cleared")
    scorer = ScrabbleScorer()
    team_processor = TeamProcessor(api_client, scorer, max_workers=config.max_concurrent_requests)
    playoff_calculator = PlayoffCalculator()

    # Create progress manager
    progress_mgr = ProgressManager(enabled=not quiet)

    # Get team count for progress tracking
    teams_info = api_client.get_teams()
    total_teams = len(teams_info)

    # Process all teams with progress tracking
    with progress_mgr.track_api_fetching(total_teams):
        team_scores, all_players, failed_teams = team_processor.process_all_teams()

    # Display summary (only if not quiet)
    if not quiet:
        console.print(
            f"\n[green]✓[/green] Successfully fetched {len(team_scores)} of "
            f"{len(team_scores) + len(failed_teams)} teams"
        )
        if failed_teams:
            console.print(f"[yellow]⚠[/yellow]  Failed teams: {', '.join(failed_teams)}")

    # Calculate standings
    division_standings = team_processor.calculate_division_standings(team_scores)
    conference_standings = team_processor.calculate_conference_standings(team_scores)
    playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

    # Generate reports based on format
    if config.output_format == "json":
        return generate_json_report(
            team_scores,
            all_players,
            division_standings,
            conference_standings,
            playoff_standings,
        )
    if config.output_format == "html":
        return generate_html_report(
            team_scores,
            all_players,
            division_standings,
            conference_standings,
            playoff_standings,
        )
    if config.output_format == "csv":
        if output_path:
            generate_csv_report(
                team_scores,
                all_players,
                division_standings,
                conference_standings,
                playoff_standings,
                output_path,
            )
            return None
        raise ValueError("CSV format requires output path")
    if config.output_format == "excel":
        if output_path:
            generate_excel_report(
                team_scores,
                all_players,
                division_standings,
                conference_standings,
                playoff_standings,
                output_path,
                sheets,
            )
            return None
        raise ValueError("Excel format requires output path")

    # Use lazy report generator for text format
    report_generator = ReportGenerator(
        team_scores=team_scores,
        all_players=all_players,
        division_standings=division_standings,
        conference_standings=conference_standings,
        playoff_standings=playoff_standings,
        top_players_count=config.top_players_count,
        top_team_players_count=config.top_team_players_count,
    )

    # Generate requested report (lazy evaluation)
    return report_generator.get_report(report_filter)


def generate_json_report(
    team_scores: dict[str, Any],
    all_players: list[Any],
    division_standings: dict[str, Any],
    conference_standings: dict[str, Any],
    playoff_standings: dict[str, Any],
) -> str:
    """Generate JSON format report.

    Args:
        team_scores: Team scores dictionary
        all_players: List of all players
        division_standings: Division standings
        conference_standings: Conference standings
        playoff_standings: Playoff standings

    Returns:
        JSON string
    """
    # Convert dataclasses to dictionaries
    teams_data = {abbrev: team.to_dict() for abbrev, team in team_scores.items()}

    divisions_data = {name: standing.to_dict() for name, standing in division_standings.items()}

    conferences_data = {name: standing.to_dict() for name, standing in conference_standings.items()}

    playoffs_data = {
        conf: [team.to_dict() for team in teams] for conf, teams in playoff_standings.items()
    }

    report_data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(team_scores),
            "total_players": len(all_players),
        },
    }

    return json.dumps(report_data, indent=2)


def generate_html_report(
    team_scores: dict[str, Any],
    all_players: list[Any],
    division_standings: dict[str, Any],
    conference_standings: dict[str, Any],
    playoff_standings: dict[str, Any],
) -> str:
    """Generate HTML format report.

    Args:
        team_scores: Team scores dictionary
        all_players: List of all players
        division_standings: Division standings
        conference_standings: Conference standings
        playoff_standings: Playoff standings

    Returns:
        HTML string
    """
    # Setup Jinja2 environment
    env = Environment(
        loader=PackageLoader("nhl_scrabble", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Get top 20 players by score
    sorted_players = sorted(all_players, key=lambda p: p.full_score, reverse=True)
    top_players = sorted_players[:20]

    # Prepare conferences data with actual team objects
    conferences = []
    for conf_name in sorted(conference_standings.keys()):
        # Get all teams in this conference from playoff standings
        conf_teams = [
            team for team in playoff_standings.get(conf_name, []) if team.conference == conf_name
        ]
        conferences.append({"name": conf_name, "teams": conf_teams})

    # Prepare divisions data
    divisions = []
    for div_name in sorted(division_standings.keys()):
        # Get teams in this division from all playoff teams
        div_teams = []
        for conf_teams in playoff_standings.values():
            div_teams.extend([team for team in conf_teams if team.division == div_name])
        # Sort by total score descending
        div_teams.sort(key=lambda t: (t.total, t.avg), reverse=True)
        divisions.append({"name": div_name, "teams": div_teams})

    # Calculate statistics
    total_score = sum(p.full_score for p in all_players)
    avg_score = total_score / len(all_players) if all_players else 0
    highest_score = sorted_players[0].full_score if sorted_players else 0

    stats = {
        "total_players": len(all_players),
        "total_teams": len(team_scores),
        "average_score": avg_score,
        "highest_score": highest_score,
    }

    # Render template
    template = env.get_template("report.html")
    html = template.render(
        timestamp=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        version=__version__,
        stats=stats,
        top_n=len(top_players),
        top_players=top_players,
        conferences=conferences,
        divisions=divisions,
    )

    return html


def generate_csv_report(
    team_scores: dict[str, Any],
    all_players: list[Any],  # noqa: ARG001
    division_standings: dict[str, Any],  # noqa: ARG001
    conference_standings: dict[str, Any],  # noqa: ARG001
    playoff_standings: dict[str, Any],  # noqa: ARG001
    output: Path,
) -> None:
    """Generate CSV format report.

    Creates a CSV report with team scores. For more detailed CSV exports,
    use the CSVExporter class directly with specific export methods.

    Args:
        team_scores: Team scores dictionary
        all_players: List of all players (not used in basic CSV export)
        division_standings: Division standings (not used in basic CSV export)
        conference_standings: Conference standings (not used in basic CSV export)
        playoff_standings: Playoff standings (not used in basic CSV export)
        output: Output file path

    Returns:
        None (writes directly to file)
    """
    exporter = CSVExporter()

    # For CSV, we export the full team report
    # This includes all teams with their scores
    exporter.export_team_scores(team_scores, output)

    logger.info(f"CSV report written to {output}")


def generate_excel_report(
    team_scores: dict[str, Any],
    all_players: list[Any],
    division_standings: dict[str, Any],
    conference_standings: dict[str, Any],
    playoff_standings: dict[str, Any],
    output: Path,
    sheets: list[str] | None = None,
) -> None:
    """Generate Excel format report.

    Creates a comprehensive Excel workbook with multiple sheets for different
    aspects of the analysis.

    Args:
        team_scores: Team scores dictionary
        all_players: List of all players
        division_standings: Division standings
        conference_standings: Conference standings
        playoff_standings: Playoff standings
        output: Output file path
        sheets: Optional list of sheets to include (default: all)

    Returns:
        None (writes directly to file)

    Raises:
        ImportError: If openpyxl is not installed
    """
    try:
        exporter = ExcelExporter()
    except ImportError as e:
        raise click.ClickException(str(e)) from e

    # Export full report with all sheets
    exporter.export_full_report(
        team_scores=team_scores,
        all_players=all_players,
        division_standings=division_standings,
        conference_standings=conference_standings,
        playoff_standings=playoff_standings,
        output=output,
        sheets=sheets,
    )

    logger.info(f"Excel report written to {output}")


@cli.command()
@click.option("--no-fetch", is_flag=True, help="Skip fetching data from NHL API on startup")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def interactive(no_fetch: bool, verbose: bool) -> None:
    """Start interactive mode for exploring NHL Scrabble data.

    Interactive mode provides a REPL (Read-Eval-Print Loop) for exploring
    NHL Scrabble scores through commands like show, top, compare, and more.

    Examples:
        nhl-scrabble interactive
        nhl-scrabble interactive --no-fetch
        nhl-scrabble interactive --verbose
    """
    from nhl_scrabble.interactive import InteractiveShell

    # Load configuration
    config = Config.from_env()
    config.verbose = verbose

    # Setup logging
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble interactive mode v{__version__}")

    try:
        shell = InteractiveShell()

        if not no_fetch:
            shell.fetch_data()

        shell.run()

    except KeyboardInterrupt:
        console.print("\n[cyan]Goodbye![/cyan]")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unexpected error in interactive mode")
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]", style="red")
        sys.exit(1)


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload (development only)")
def serve(host: str, port: int, reload: bool) -> None:
    """Start web interface server.

    Starts a FastAPI web server providing browser-based access to
    NHL Scrabble analysis. Visit http://localhost:8000 after starting.

    Examples:
        # Start server on default port
        nhl-scrabble serve

        # Development mode with auto-reload
        nhl-scrabble serve --reload

        # Custom host and port
        nhl-scrabble serve --host 0.0.0.0 --port 5000
    """
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: uvicorn not installed. Install with: pip install nhl-scrabble[web]",
            err=True,
        )
        raise click.Abort from None

    click.echo(f"Starting NHL Scrabble web server at http://{host}:{port}")
    click.echo("Press CTRL+C to stop")

    # Import here to avoid loading FastAPI when not needed
    from nhl_scrabble.web.app import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload (development only)")
@click.option("--workers", default=1, type=int, help="Number of worker processes (production)")
def api(host: str, port: int, reload: bool, workers: int) -> None:
    """Start REST API server.

    Starts a FastAPI REST API server providing programmatic access to
    NHL Scrabble data. Visit http://localhost:8000/docs for API documentation.

    The API provides endpoints for:
    - Team scores (/api/v1/teams)
    - Player scores (/api/v1/players)
    - Division standings (/api/v1/standings/division)
    - Conference standings (/api/v1/standings/conference)
    - Playoff bracket (/api/v1/standings/playoffs)

    Examples:
        # Start API server on default port
        nhl-scrabble api

        # Development mode with auto-reload
        nhl-scrabble api --reload

        # Production mode with multiple workers
        nhl-scrabble api --workers 4 --host 0.0.0.0

        # Custom host and port
        nhl-scrabble api --host 0.0.0.0 --port 5000
    """
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: uvicorn not installed. Install with: pip install nhl-scrabble",
            err=True,
        )
        raise click.Abort from None

    click.echo(f"Starting NHL Scrabble REST API server at http://{host}:{port}")
    click.echo(f"API Documentation: http://{host}:{port}/docs")
    click.echo("Press CTRL+C to stop")

    # Import here to avoid loading FastAPI when not needed
    from nhl_scrabble.api_server.app import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,  # Multiple workers not compatible with reload
        log_level="info",
    )


if __name__ == "__main__":
    cli()
