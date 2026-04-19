"""Command-line interface for NHL Scrabble."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError
from nhl_scrabble.config import Config
from nhl_scrabble.dashboard import StatisticsDashboard
from nhl_scrabble.exporters.csv_exporter import CSVExporter
from nhl_scrabble.exporters.excel_exporter import ExcelExporter
from nhl_scrabble.filters import AnalysisFilters
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.reports.generator import ReportGenerator
from nhl_scrabble.scoring.config import ScoringConfig
from nhl_scrabble.scoring.scrabble import ScrabbleScorer
from nhl_scrabble.search import PlayerSearch
from nhl_scrabble.ui.progress import ProgressManager
from nhl_scrabble.validators import ValidationError, validate_file_path, validate_integer_range

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


def validate_cli_arguments(
    output: str | None, top_players: int, top_team_players: int
) -> tuple[Path | None, int, int]:
    """Validate all CLI arguments before processing.

    Uses comprehensive validators from validators module to check all inputs
    for security issues and invalid values. This validation happens before
    any API calls to provide immediate feedback.

    Args:
        output: Output file path, or None for stdout
        top_players: Number of top players to show
        top_team_players: Number of top players per team to show

    Returns:
        Tuple of (validated_output_path, validated_top_players, validated_top_team_players)

    Raises:
        click.ClickException: If any argument is invalid with helpful error message

    Security:
        - Prevents path traversal attacks via output path
        - Validates numeric parameters to prevent DoS via memory exhaustion
        - Provides early validation before expensive operations

    Examples:
        >>> validate_cli_arguments("output.txt", 20, 5)
        (PosixPath('/current/dir/output.txt'), 20, 5)
        >>> validate_cli_arguments(None, 20, 5)  # stdout
        (None, 20, 5)
    """
    validated_output: Path | None = None

    try:
        # Validate output path if provided
        if output:
            # Allow overwrite since we'll warn the user
            validated_output = validate_file_path(output, allow_overwrite=True)
            if validated_output.exists():
                logger.warning(f"Output file exists and will be overwritten: {validated_output}")

        # Validate numeric parameters
        validated_top_players = validate_integer_range(
            top_players, min_val=1, max_val=100, name="top_players"
        )

        validated_top_team_players = validate_integer_range(
            top_team_players, min_val=1, max_val=50, name="top_team_players"
        )

        return validated_output, validated_top_players, validated_top_team_players

    except ValidationError as e:
        raise click.ClickException(str(e)) from e


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
@click.option(
    "--scoring",
    type=click.Choice(["scrabble", "wordle", "uniform"], case_sensitive=False),
    default="scrabble",
    help="Built-in scoring system to use (default: scrabble)",
)
@click.option(
    "--scoring-config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to custom scoring configuration JSON file",
)
@click.option(
    "--division",
    help="Filter by division (comma-separated: Atlantic,Metropolitan,Central,Pacific)",
)
@click.option(
    "--conference",
    help="Filter by conference (comma-separated: Eastern,Western)",
)
@click.option(
    "--teams",
    help="Filter by teams (comma-separated abbreviations: TOR,MTL,BOS)",
)
@click.option(
    "--exclude",
    help="Exclude teams (comma-separated abbreviations: NYR,PHI)",
)
@click.option(
    "--min-score",
    type=int,
    help="Minimum player score to include",
)
@click.option(
    "--max-score",
    type=int,
    help="Maximum player score to include",
)
def analyze(  # noqa: PLR0912, PLR0913, PLR0915  # CLI function with many parameters/statements
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
    scoring: str,
    scoring_config: Path | None,
    division: str | None,
    conference: str | None,
    teams: str | None,
    exclude: str | None,
    min_score: int | None,
    max_score: int | None,
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
        nhl-scrabble analyze --scoring wordle
        nhl-scrabble analyze --scoring uniform --output uniform_scores.txt
        nhl-scrabble analyze --scoring-config custom_values.json
        nhl-scrabble analyze --division Atlantic
        nhl-scrabble analyze --conference Eastern
        nhl-scrabble analyze --teams TOR,MTL,OTT
        nhl-scrabble analyze --min-score 50 --max-score 100
        nhl-scrabble analyze --exclude BOS,NYR
        nhl-scrabble analyze --division Atlantic --min-score 60
    """
    # Validate CLI arguments first (before expensive operations)
    validated_output, validated_top_players, validated_top_team_players = validate_cli_arguments(
        output, top_players, top_team_players
    )

    # Load configuration (which will also validate environment variables)
    try:
        config = Config.from_env()
    except ValueError as e:
        # Convert config validation errors to ClickException for consistent error handling
        raise click.ClickException(f"Configuration error: {e}") from e

    config.verbose = verbose
    config.output_format = output_format
    config.top_players_count = validated_top_players
    config.top_team_players_count = validated_top_team_players

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging with sanitization setting from config
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble analysis v{__version__}")
    logger.debug(f"Configuration: {config}")

    # Validate scoring options (mutually exclusive)
    if scoring_config and scoring != "scrabble":
        raise click.ClickException(
            "--scoring and --scoring-config are mutually exclusive. "
            "Use --scoring for built-in systems or --scoring-config for custom values."
        )

    # Load scoring configuration
    scoring_values = None
    if scoring_config:
        try:
            scoring_values = ScoringConfig.load_from_file(scoring_config)
            logger.info(f"Using custom scoring config from: {scoring_config}")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            raise click.ClickException(f"Error loading scoring config: {e}") from e
    elif scoring != "scrabble":
        scoring_values = ScoringConfig.get_scoring_system(scoring)
        logger.info(f"Using built-in scoring system: {scoring}")

    # Validate CSV/Excel require output file
    if output_format in ("csv", "excel") and not output:
        raise click.ClickException(
            f"{output_format.upper()} format requires --output option\n"
            f"Example: nhl-scrabble analyze --format {output_format} --output report.{output_format}"
        )

    # Validate output path BEFORE making API calls
    validate_output_path(output)

    # Display header
    console.print("\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer 🏒[/bold cyan]\n")
    console.print("=" * 80)

    try:
        # Parse sheets list for Excel export
        sheets_list = None
        if sheets:
            sheets_list = [s.strip() for s in sheets.split(",")]

        # Create filters from CLI options
        filters = AnalysisFilters.from_options(
            division=division,
            conference=conference,
            teams=teams,
            exclude=exclude,
            min_score=min_score,
            max_score=max_score,
        )

        # Log active filters
        if filters.is_active():
            logger.info(f"Active filters: {filters}")
            if not quiet:
                console.print("\n[yellow]Filters active:[/yellow]")
                if filters.divisions:
                    console.print(f"  • Divisions: {', '.join(sorted(filters.divisions))}")
                if filters.conferences:
                    console.print(f"  • Conferences: {', '.join(sorted(filters.conferences))}")
                if filters.teams:
                    console.print(f"  • Teams: {', '.join(sorted(filters.teams))}")
                if filters.excluded_teams:
                    console.print(f"  • Excluded: {', '.join(sorted(filters.excluded_teams))}")
                if filters.min_score is not None:
                    console.print(f"  • Min score: {filters.min_score}")
                if filters.max_score is not None:
                    console.print(f"  • Max score: {filters.max_score}")
                console.print()

        # Run the analysis
        result = run_analysis(
            config,
            clear_cache=clear_cache,
            report_filter=report,
            quiet=quiet,
            output_path=validated_output,
            sheets=sheets_list,
            scoring_values=scoring_values,
            filters=filters,
        )

        # Output results
        if validated_output:
            if isinstance(result, str):
                # Text/JSON output
                validated_output.write_text(result)
            # CSV/Excel are written directly by exporters
            console.print(f"\n[green]✓[/green] Report saved to: {validated_output}")
        elif isinstance(result, str):
            print(result)
        else:
            console.print(
                "\n[yellow]⚠[/yellow] CSV/Excel formats require --output option", style="yellow"
            )

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


def run_analysis(  # noqa: PLR0913  # Complex analysis orchestration function with many parameters
    config: Config,
    clear_cache: bool = False,
    report_filter: str | None = None,
    quiet: bool = False,
    output_path: Path | None = None,
    sheets: list[str] | None = None,
    scoring_values: dict[str, int] | None = None,
    filters: AnalysisFilters | None = None,
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
        scoring_values: Optional custom letter-to-point value mapping.
            If None, uses standard Scrabble values.
        filters: Optional filters to apply to analysis results

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
        rate_limit_max_requests=config.rate_limit_max_requests,
        rate_limit_window=config.rate_limit_window,
        backoff_factor=config.backoff_factor,
        max_backoff=config.max_backoff,
        cache_enabled=config.cache_enabled,
        cache_expiry=config.cache_expiry,
    )

    # Clear cache if requested
    if clear_cache:
        api_client.clear_cache()
        logger.info("API cache cleared")

    # Initialize scorer with custom or default values
    scorer = ScrabbleScorer(letter_values=scoring_values)
    team_processor = TeamProcessor(api_client, scorer)
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

    # Apply filters if specified
    if filters and filters.is_active():
        from nhl_scrabble.filters import (
            filter_conference_standings,
            filter_division_standings,
            filter_players,
            filter_playoff_standings,
            filter_teams,
        )

        logger.info("Applying filters to analysis results")
        team_scores = filter_teams(team_scores, filters)
        all_players = filter_players(all_players, filters)
        division_standings = filter_division_standings(division_standings, filters)
        conference_standings = filter_conference_standings(conference_standings, filters)
        playoff_standings = filter_playoff_standings(playoff_standings, filters)

        # Log filter results
        if not quiet:
            console.print(
                f"\n[green]✓[/green] Filters applied: {len(team_scores)} teams, "
                f"{len(all_players)} players"
            )

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
    try:
        config = Config.from_env()
    except ValueError as e:
        # Convert config validation errors to ClickException for consistent error handling
        raise click.ClickException(f"Configuration error: {e}") from e

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
@click.argument("query", required=False)
@click.option(
    "--fuzzy",
    "-f",
    is_flag=True,
    help="Enable fuzzy matching",
)
@click.option(
    "--min-score",
    type=int,
    help="Minimum Scrabble score",
)
@click.option(
    "--max-score",
    type=int,
    help="Maximum Scrabble score",
)
@click.option(
    "--team",
    "-t",
    help="Filter by team abbreviation (e.g., TOR, MTL)",
)
@click.option(
    "--division",
    "-d",
    help="Filter by division name",
)
@click.option(
    "--conference",
    "-c",
    help="Filter by conference name",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    default=20,
    help="Maximum number of results to show (default: 20)",
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
def search(  # noqa: PLR0913  # CLI function needs many parameters
    query: str | None,
    fuzzy: bool,
    min_score: int | None,
    max_score: int | None,
    team: str | None,
    division: str | None,
    conference: str | None,
    limit: int,
    verbose: bool,
    quiet: bool,
    output_format: str,
    output: str | None,
) -> None:
    """Search for players by name and filter by attributes.

    Search the NHL player database by name with support for exact matching,
    fuzzy matching, and wildcard patterns. Filter results by score, team,
    division, or conference.

    Examples:
        # Exact search
        nhl-scrabble search "Connor McDavid"

        # Fuzzy search
        nhl-scrabble search McDavid --fuzzy

        # Wildcard search
        nhl-scrabble search "Connor*"

        # Score filtering
        nhl-scrabble search --min-score 50

        # Team filtering
        nhl-scrabble search --team TOR

        # Combined filters
        nhl-scrabble search "Connor*" --team EDM --min-score 40

        # JSON output
        nhl-scrabble search McDavid --fuzzy --format json

        # Save to file
        nhl-scrabble search --min-score 60 --output high-scorers.txt
    """
    # Load configuration
    try:
        config = Config.from_env()
    except ValueError as e:
        # Convert config validation errors to ClickException for consistent error handling
        raise click.ClickException(f"Configuration error: {e}") from e

    config.verbose = verbose

    # Setup logging
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info("Starting NHL player search")

    # Validate output path
    validate_output_path(output)

    try:
        # Fetch player data
        if not quiet:
            console.print("\n[bold cyan]🔍 NHL Player Search 🔍[/bold cyan]\n")
            console.print("=" * 80)

        # Initialize components
        api_client = NHLApiClient(
            base_url=config.api_base_url,
            timeout=config.api_timeout,
            retries=config.api_retries,
            rate_limit_max_requests=config.rate_limit_max_requests,
            rate_limit_window=config.rate_limit_window,
            backoff_factor=config.backoff_factor,
            max_backoff=config.max_backoff,
            cache_enabled=config.cache_enabled,
            cache_expiry=config.cache_expiry,
        )
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        # Process all teams (progress handled internally by TeamProcessor)
        _, all_players, failed_teams = team_processor.process_all_teams()

        # Display summary (only if not quiet)
        if not quiet and failed_teams:
            console.print(f"[yellow]⚠[/yellow]  Failed teams: {', '.join(failed_teams)}")

        # Create search instance
        searcher = PlayerSearch(all_players)

        # Perform search
        results = searcher.search(
            query or "",
            fuzzy=fuzzy,
            min_score=min_score,
            max_score=max_score,
            team=team,
            division=division,
            conference=conference,
        )

        # Limit results
        if limit and len(results) > limit:
            results = results[:limit]

        # Generate output
        if output_format == "json":
            output_text = generate_search_json(results, query, searcher.get_stats())
        else:
            output_text = generate_search_text(
                results, query, fuzzy, min_score, max_score, team, division, conference, limit
            )

        # Output results
        if output:
            Path(output).write_text(output_text)
            if not quiet:
                console.print(f"\n[green]✓[/green] Results saved to: {output}")
        else:
            print(output_text)

        if not quiet:
            console.print("\n" + "=" * 80)
            console.print("[green]✓ Search complete![/green]")

    except NHLApiError as e:
        logger.error(f"NHL API error: {e}")
        console.print(f"\n[red]❌ NHL API Error: {e}[/red]", style="red")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during search")
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]", style="red")
        sys.exit(1)


def generate_search_text(  # noqa: PLR0913  # Need all search parameters
    results: list[Any],
    query: str | None,
    fuzzy: bool,
    min_score: int | None,
    max_score: int | None,
    team: str | None,
    division: str | None,
    conference: str | None,
    limit: int,
) -> str:
    """Generate text format search results.

    Args:
        results: List of PlayerScore objects
        query: Search query
        fuzzy: Whether fuzzy matching was used
        min_score: Minimum score filter
        max_score: Maximum score filter
        team: Team filter
        division: Division filter
        conference: Conference filter
        limit: Result limit

    Returns:
        Formatted text output
    """
    lines = []
    lines.append("\n🔍 PLAYER SEARCH RESULTS\n")
    lines.append("=" * 80)

    # Display search parameters
    lines.append("\nSearch Parameters:")
    if query:
        match_type = "Fuzzy" if fuzzy else ("Wildcard" if "*" in query or "?" in query else "Exact")
        lines.append(f"  Query: {query} ({match_type} matching)")
    if min_score is not None:
        lines.append(f"  Minimum Score: {min_score}")
    if max_score is not None:
        lines.append(f"  Maximum Score: {max_score}")
    if team:
        lines.append(f"  Team: {team}")
    if division:
        lines.append(f"  Division: {division}")
    if conference:
        lines.append(f"  Conference: {conference}")

    lines.append(f"\nFound {len(results)} player(s)")
    if limit and len(results) >= limit:
        lines.append(f"(showing top {limit})")
    lines.append("\n" + "-" * 80 + "\n")

    # Display results
    if results:
        for i, player in enumerate(results, 1):
            lines.append(
                f"{i:3d}. {player.full_name:<30} | Score: {player.full_score:3d} | "
                f"Team: {player.team:4s} | {player.division}"
            )
            lines.append(
                f"     First: {player.first_name} ({player.first_score}) | "
                f"Last: {player.last_name} ({player.last_score})"
            )
            lines.append("")
    else:
        lines.append("No players found matching the search criteria.\n")

    lines.append("-" * 80)

    return "\n".join(lines)


def generate_search_json(results: list[Any], query: str | None, stats: dict[str, Any]) -> str:
    """Generate JSON format search results.

    Args:
        results: List of PlayerScore objects
        query: Search query
        stats: Player database statistics

    Returns:
        JSON string
    """
    data = {
        "query": query,
        "result_count": len(results),
        "stats": stats,
        "results": [asdict(p) for p in results],
    }
    return json.dumps(data, indent=2)


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
@click.option(
    "--division",
    help="Filter by division (e.g., Atlantic, Metropolitan, Central, Pacific)",
)
@click.option(
    "--conference",
    help="Filter by conference (Eastern or Western)",
)
@click.option(
    "--duration",
    type=int,
    help="Run dashboard for specified seconds (default: until Ctrl+C)",
)
@click.option(
    "--static",
    is_flag=True,
    help="Display static snapshot instead of live dashboard",
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
    help="Suppress progress bars during data fetching",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable API response caching (always fetch fresh data)",
)
def dashboard(
    division: str | None,
    conference: str | None,
    duration: int | None,
    static: bool,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
) -> None:
    """Launch interactive statistics dashboard.

    Displays live statistics with charts and visualizations using Rich library.
    Shows top teams, players, division and conference standings in an interactive
    terminal dashboard.

    Press Ctrl+C to exit the dashboard.

    Examples:
        # Launch dashboard
        nhl-scrabble dashboard

        # Filter by division
        nhl-scrabble dashboard --division Atlantic

        # Filter by conference
        nhl-scrabble dashboard --conference Eastern

        # Run for 30 seconds then exit
        nhl-scrabble dashboard --duration 30

        # Display static snapshot (no live updates)
        nhl-scrabble dashboard --static

        # Combine filters
        nhl-scrabble dashboard --division Metropolitan --static
    """
    # Load configuration
    try:
        config = Config.from_env()
    except ValueError as e:
        raise click.ClickException(f"Configuration error: {e}") from e

    config.verbose = verbose

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble dashboard v{__version__}")

    # Display header
    if not quiet:
        console.print("\n[bold cyan]🏒 NHL Scrabble Dashboard 🏒[/bold cyan]\n")
        console.print("=" * 80)
        console.print("Fetching NHL roster data...\n")

    try:
        # Fetch data using same logic as analyze command
        result_data = fetch_dashboard_data(config, quiet=quiet)

        if result_data is None:
            console.print("[red]❌ Failed to fetch data[/red]")
            sys.exit(1)

        # Create and run dashboard
        dash = StatisticsDashboard(
            team_scores=result_data["team_scores"],
            all_players=result_data["all_players"],
            division_standings=result_data["division_standings"],
            conference_standings=result_data["conference_standings"],
            division_filter=division,
            conference_filter=conference,
        )

        if static:
            # Display static snapshot
            dash.display_static()
        else:
            # Run live dashboard
            if not quiet:
                console.print("[green]✓[/green] Data fetched successfully!\n")
                console.print("=" * 80)
                console.print("\n[yellow]Press Ctrl+C to exit dashboard[/yellow]\n")

            dash.run(duration=duration)

    except NHLApiError as e:
        logger.error(f"NHL API error: {e}")
        console.print(f"\n[red]❌ NHL API Error: {e}[/red]", style="red")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard closed.[/yellow]")
    except Exception as e:
        logger.exception("Unexpected error during dashboard")
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]", style="red")
        sys.exit(1)


def fetch_dashboard_data(
    config: Config,
    quiet: bool = False,
) -> dict[str, Any] | None:
    """Fetch data needed for dashboard.

    Args:
        config: Configuration object
        quiet: Whether to suppress progress bars

    Returns:
        Dictionary with team_scores, all_players, division_standings,
        conference_standings, or None if fetching failed
    """
    # Initialize components
    api_client = NHLApiClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout,
        retries=config.api_retries,
        rate_limit_max_requests=config.rate_limit_max_requests,
        rate_limit_window=config.rate_limit_window,
        backoff_factor=config.backoff_factor,
        max_backoff=config.max_backoff,
        cache_enabled=config.cache_enabled,
        cache_expiry=config.cache_expiry,
    )

    scorer = ScrabbleScorer()
    team_processor = TeamProcessor(api_client, scorer)

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

    return {
        "team_scores": team_scores,
        "all_players": all_players,
        "division_standings": division_standings,
        "conference_standings": conference_standings,
    }


def _interruptible_sleep(seconds: int, shutdown_flag: list[bool]) -> None:
    """Sleep for specified seconds, checking shutdown flag every second.

    Args:
        seconds: Number of seconds to sleep
        shutdown_flag: Mutable list containing shutdown boolean flag
    """
    for _ in range(seconds):
        if shutdown_flag[0]:
            return
        time.sleep(1)


@cli.command()
@click.option(
    "--interval",
    type=int,
    default=300,
    help="Refresh interval in seconds (default: 300 = 5 minutes)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
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
def watch(  # noqa: PLR0913, PLR0915  # Complex but necessary for watch mode
    interval: int,
    output_format: str,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    top_players: int,
    top_team_players: int,
    report: str | None,
) -> None:
    """Watch mode - automatically refresh data at intervals.

    Runs continuous analysis with auto-refresh, useful for monitoring
    roster changes during active periods.

    Press Ctrl+C to stop watching.

    Examples:
        # Watch with default 5-minute interval
        nhl-scrabble watch

        # Custom 1-minute interval
        nhl-scrabble watch --interval 60

        # Watch specific report with 30-second interval
        nhl-scrabble watch --report team --interval 30

        # Watch with JSON output
        nhl-scrabble watch --format json --interval 120
    """
    # Validate interval
    if interval < 1:
        raise click.ClickException("Interval must be at least 1 second")

    # Load configuration
    config = Config.from_env()
    config.verbose = verbose
    config.output_format = output_format
    config.top_players_count = top_players
    config.top_team_players_count = top_team_players

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble watch mode v{__version__} (interval: {interval}s)")

    # Display header
    console.print(
        "\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer - Watch Mode 🏒[/bold cyan]\n"
    )
    console.print("=" * 80)
    console.print(f"[yellow]Auto-refresh every {interval} seconds (Ctrl+C to stop)[/yellow]\n")
    console.print("=" * 80)

    # Use list to allow modification in nested function (mutable container)
    shutdown_flag = [False]

    def signal_handler(_signum: int, _frame: Any) -> None:  # Required signature
        """Handle Ctrl+C gracefully."""
        shutdown_flag[0] = True
        console.print("\n\n[yellow]⏹  Stopping watch mode...[/yellow]")

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Watch loop
    iteration = 0
    try:
        while not shutdown_flag[0]:
            iteration += 1
            timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            console.print(f"\n[bold cyan]Update #{iteration}[/bold cyan] - {timestamp}")
            console.print("-" * 80)

            try:
                # Run analysis
                result = run_analysis(
                    config,
                    clear_cache=False,  # Don't clear cache between iterations
                    report_filter=report,
                    quiet=quiet,
                    output_path=None,  # Always stdout for watch mode
                    sheets=None,
                )

                # Display result
                if result:
                    print(result)

                console.print("-" * 80)

                # Wait for next iteration (unless shutdown requested)
                if not shutdown_flag[0]:
                    console.print(
                        f"\n[dim]Next refresh in {interval} seconds... (Press Ctrl+C to stop)[/dim]"
                    )
                    _interruptible_sleep(interval, shutdown_flag)

            except NHLApiError as e:
                logger.error(f"NHL API error: {e}")
                console.print(f"[red]❌ NHL API Error: {e}[/red]", style="red")
                console.print("[yellow]Will retry on next iteration...[/yellow]")

                # Wait before retry
                if not shutdown_flag[0]:
                    console.print(
                        f"\n[dim]Retrying in {interval} seconds... (Press Ctrl+C to stop)[/dim]"
                    )
                    _interruptible_sleep(interval, shutdown_flag)

            except Exception as e:
                logger.exception("Unexpected error during watch iteration")
                console.print(f"[red]❌ Unexpected error: {e}[/red]", style="red")
                console.print("[yellow]Will retry on next iteration...[/yellow]")

                # Wait before retry
                if not shutdown_flag[0]:
                    console.print(
                        f"\n[dim]Retrying in {interval} seconds... (Press Ctrl+C to stop)[/dim]"
                    )
                    _interruptible_sleep(interval, shutdown_flag)

    except KeyboardInterrupt:
        # Additional safety net
        pass

    # Clean shutdown
    console.print("\n" + "=" * 80)
    console.print(f"[green]✓ Watch mode stopped after {iteration} updates[/green]")


if __name__ == "__main__":
    cli()
