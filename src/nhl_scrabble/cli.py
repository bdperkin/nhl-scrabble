"""Command-line interface for NHL Scrabble."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError
from nhl_scrabble.config import Config
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.reports.conference_report import ConferenceReporter
from nhl_scrabble.reports.division_report import DivisionReporter
from nhl_scrabble.reports.playoff_report import PlayoffReporter
from nhl_scrabble.reports.stats_report import StatsReporter
from nhl_scrabble.reports.team_report import TeamReporter
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
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
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
    help="Suppress progress bars and non-essential output",
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
def analyze(  # noqa: PLR0913 - CLI command requires all these parameters
    output_format: str,
    output: str | None,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    clear_cache: bool,
    top_players: int,
    top_team_players: int,
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
        nhl-scrabble analyze --no-cache
        nhl-scrabble analyze --clear-cache
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
    logger.debug(f"Configuration: {config}")

    # Validate output path BEFORE making API calls
    validate_output_path(output)

    # Display header (suppress if quiet mode)
    if not quiet:
        console.print("\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer 🏒[/bold cyan]\n")
        console.print("=" * 80)

    try:
        # Run the analysis
        result = run_analysis(config, clear_cache=clear_cache, quiet=quiet)

        # Output results
        if output:
            output_path = Path(output)
            output_path.write_text(result)
            if not quiet:
                console.print(f"\n[green]✓[/green] Report saved to: {output}")
        else:
            print(result)

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


def run_analysis(config: Config, clear_cache: bool = False, quiet: bool = False) -> str:
    """Run the complete NHL Scrabble analysis.

    Args:
        config: Configuration object
        clear_cache: Whether to clear the API cache before running
        quiet: Whether to suppress progress bars and non-essential output

    Returns:
        Complete report string

    Raises:
        NHLApiError: If there are issues fetching data from NHL API
    """
    # Initialize components
    api_client = NHLApiClient(
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
    team_processor = TeamProcessor(api_client, scorer)
    playoff_calculator = PlayoffCalculator()

    # Initialize reporters
    conference_reporter = ConferenceReporter()
    division_reporter = DivisionReporter()
    playoff_reporter = PlayoffReporter()
    team_reporter = TeamReporter(top_players_per_team=config.top_team_players_count)
    stats_reporter = StatsReporter(top_players_count=config.top_players_count)

    # Initialize progress manager
    progress_manager = ProgressManager(enabled=not quiet)

    # Get teams count for progress tracking
    teams = api_client.get_teams()
    total_teams = len(teams)

    # Process all teams with progress tracking
    with progress_manager.track_api_fetching(total_teams) as progress_callback:
        team_scores, all_players, failed_teams = team_processor.process_all_teams(
            progress_callback=progress_callback
        )

    # Display summary (suppress if quiet)
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
    # Generate text reports
    reports = [
        conference_reporter.generate(conference_standings),
        division_reporter.generate(division_standings),
        playoff_reporter.generate(playoff_standings),
        team_reporter.generate(team_scores),
        stats_reporter.generate((all_players, division_standings, conference_standings)),
    ]

    return "\n".join(reports) + "\n" + "=" * 80 + "\n"


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
    import json
    from dataclasses import asdict

    # Convert dataclasses to dictionaries
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in team_scores.items()
    }

    divisions_data = {name: asdict(standing) for name, standing in division_standings.items()}

    conferences_data = {name: asdict(standing) for name, standing in conference_standings.items()}

    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in playoff_standings.items()
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
    from datetime import datetime

    from jinja2 import Environment, PackageLoader, select_autoescape

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
    from datetime import timezone

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


@cli.command()
@click.option(
    "--no-fetch",
    is_flag=True,
    help="Skip fetching data (requires previous session data)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
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


if __name__ == "__main__":
    cli()
