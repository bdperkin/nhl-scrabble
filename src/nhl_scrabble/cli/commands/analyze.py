"""Analyze command for NHL Scrabble CLI."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiError
from nhl_scrabble.cli.orchestration import run_analysis
from nhl_scrabble.cli.validators import validate_cli_arguments, validate_output_path
from nhl_scrabble.config import Config
from nhl_scrabble.filters import AnalysisFilters
from nhl_scrabble.i18n import SUPPORTED_LOCALES, _
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.scoring.config import ScoringConfig

logger = logging.getLogger(__name__)
console = Console()


@click.command()
# === Output Options ===
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(
        ["text", "json", "yaml", "xml", "html", "table", "markdown", "csv", "excel", "template"],
        case_sensitive=False,
    ),
    default="text",
    help=_("Output format (default: text)"),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help=_("Output file path (default: stdout)"),
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False),
    help=_("Custom template file path (required for --format template)"),
)
@click.option(
    "--sheets",
    help=_(
        "Comma-separated list of sheets for Excel export (teams,players,divisions,conferences,playoffs)",
    ),
)
# === Behavior Flags ===
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=_("Enable verbose logging"),
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help=_("Suppress progress bars and status messages"),
)
# === Data Source Options ===
@click.option(
    "--no-cache",
    is_flag=True,
    help=_("Disable API response caching (always fetch fresh data)"),
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help=_("Clear API cache before running"),
)
@click.option(
    "--season",
    type=str,
    help=_("Analyze specific season (format: YYYYYYYY, e.g., 20222023 for 2022-23)"),
)
# === Display Options ===
@click.option(
    "--top-players",
    type=click.IntRange(min=1, max=100),
    default=20,
    help=_("Number of top players to show (default: 20, range: 1-100)"),
)
@click.option(
    "--top-team-players",
    type=click.IntRange(min=1, max=50),
    default=5,
    help=_("Number of top players per team to show (default: 5, range: 1-50)"),
)
# === Report Selection ===
@click.option(
    "--report",
    type=click.Choice(["conference", "division", "playoff", "team", "stats"], case_sensitive=False),
    help=_("Generate specific report only (default: all reports)"),
)
# === Scoring Options ===
@click.option(
    "--scoring",
    type=click.Choice(["scrabble", "wordle", "uniform"], case_sensitive=False),
    default="scrabble",
    help=_("Built-in scoring system to use (default: scrabble)"),
)
@click.option(
    "--scoring-config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help=_("Path to custom scoring configuration JSON file"),
)
# === Filtering Options ===
@click.option(
    "--divisions",
    help=_("Filter by divisions (comma-separated: Atlantic,Metropolitan,Central,Pacific)"),
)
@click.option(
    "--conferences",
    help=_("Filter by conferences (comma-separated: Eastern,Western)"),
)
@click.option(
    "--teams",
    help=_("Filter by teams (comma-separated abbreviations: TOR,MTL,BOS)"),
)
@click.option(
    "--exclude-teams",
    help=_("Exclude teams (comma-separated abbreviations: NYR,PHI)"),
)
@click.option(
    "--countries",
    help=_("Filter by countries (comma-separated codes: CAN,USA,SWE,FIN)"),
)
@click.option(
    "--min-score",
    type=int,
    help=_("Minimum player score to include"),
)
@click.option(
    "--max-score",
    type=int,
    help=_("Maximum player score to include"),
)
@click.option(
    "--group-by",
    type=click.Choice(
        ["team", "division", "conference", "nationality", "position", "position-type"],
        case_sensitive=False,
    ),
    help=_("Group players by team, division, conference, nationality, position, or position-type"),
)
@click.option(
    "--positions",
    help=_(
        "Filter by positions (comma-separated codes: C,L,R,D,G or types: Forward,Defense,Goalie)",
    ),
)
# === Locale Options ===
@click.option(
    "--locale",
    "-l",
    type=click.Choice(SUPPORTED_LOCALES, case_sensitive=True),
    help=_("Display locale (e.g., fr_CA for Canadian French)"),
)
@click.help_option("-h", "--help")
def analyze(  # noqa: PLR0912, PLR0913, PLR0915  # CLI function with many parameters/statements
    output_format: str,
    output: str | None,
    template: str | None,
    sheets: str | None,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    clear_cache: bool,
    season: str | None,
    top_players: int,
    top_team_players: int,
    report: str | None,
    scoring: str,
    scoring_config: Path | None,
    divisions: str | None,
    conferences: str | None,
    teams: str | None,
    exclude_teams: str | None,
    countries: str | None,
    min_score: int | None,
    max_score: int | None,
    group_by: str | None,
    positions: str | None,
    locale: str | None,
) -> None:
    r"""Run the NHL Scrabble analysis.

    Fetches current NHL roster data and generates comprehensive reports
    with Scrabble scores for all players and teams.

    \b
    Examples:
      Basic usage with text output to stdout:
        $ nhl-scrabble analyze

      Enable verbose logging for debugging:
        $ nhl-scrabble analyze --verbose

      Suppress progress bars (quiet mode):
        $ nhl-scrabble analyze --quiet

      Save text output to file:
        $ nhl-scrabble analyze --output report.txt

      JSON format output to file:
        $ nhl-scrabble analyze --format json --output report.json

      YAML format output to file:
        $ nhl-scrabble analyze --format yaml --output report.yaml

      XML format output to file:
        $ nhl-scrabble analyze --format xml --output report.xml

      HTML format output to file:
        $ nhl-scrabble analyze --format html --output report.html

      Markdown format output to file:
        $ nhl-scrabble analyze --format markdown --output report.md

      Table format to terminal:
        $ nhl-scrabble analyze --format table

      CSV format output to file:
        $ nhl-scrabble analyze --format csv --output report.csv

      Excel workbook with all sheets:
        $ nhl-scrabble analyze --format excel --output report.xlsx

      Excel with specific sheets only:
        $ nhl-scrabble analyze --format excel --sheets teams,players --output report.xlsx

      Custom template output:
        $ nhl-scrabble analyze --format template --template custom.j2 --output report.txt

      Disable API response caching:
        $ nhl-scrabble analyze --no-cache

      Clear cache before running:
        $ nhl-scrabble analyze --clear-cache

      Generate specific report only:
        $ nhl-scrabble analyze --report team

      Generate playoff report to file:
        $ nhl-scrabble analyze --report playoff --output playoffs.txt

      Use alternative scoring system (Wordle):
        $ nhl-scrabble analyze --scoring wordle

      Use custom scoring configuration:
        $ nhl-scrabble analyze --scoring-config custom_values.json

      Filter by division:
        $ nhl-scrabble analyze --divisions Atlantic

      Filter by conference:
        $ nhl-scrabble analyze --conferences Eastern

      Filter by specific teams:
        $ nhl-scrabble analyze --teams TOR,MTL,OTT

      Filter by score range:
        $ nhl-scrabble analyze --min-score 50 --max-score 100

      Filter by country:
        $ nhl-scrabble analyze --countries CAN

      Filter by multiple countries:
        $ nhl-scrabble analyze --countries CAN,USA,SWE

      Group by nationality:
        $ nhl-scrabble analyze --group-by nationality

      Combine country filter with grouping:
        $ nhl-scrabble analyze --countries CAN,USA --group-by nationality

      Exclude specific teams:
        $ nhl-scrabble analyze --exclude-teams BOS,NYR

      Analyze specific season:
        $ nhl-scrabble analyze --season 20222023

      Combine multiple options:
        $ nhl-scrabble analyze --format json --output report.json --verbose
        $ nhl-scrabble analyze --divisions Atlantic --min-score 60 --output atlantic.txt
    """
    # Validate output path (numeric validation now handled by Click IntRange)
    validated_output = validate_cli_arguments(output)

    # Load configuration (which will also validate environment variables)
    try:
        config = Config.from_env()
    except ValueError as e:
        # Convert config validation errors to ClickException for consistent error handling
        raise click.ClickException(f"Configuration error: {e}") from e

    config.verbose = verbose
    config.output_format = output_format
    config.top_players_count = top_players
    config.top_team_players_count = top_team_players

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging with sanitization setting from config
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    # Note: locale parameter validated by Click but translation override via NHL_SCRABBLE_LANG env var
    # TODO(#future): Implement locale override to avoid global variable issues (tracked separately)
    if locale:
        logger.debug(f"Locale requested: {locale} (use NHL_SCRABBLE_LANG env var for now)")

    logger.info(f"Starting NHL Scrabble analysis v{__version__}")
    logger.debug(f"Configuration: {config}")

    # Validate scoring options (mutually exclusive)
    if scoring_config and scoring != "scrabble":
        raise click.ClickException(
            "--scoring and --scoring-config are mutually exclusive. "
            "Use --scoring for built-in systems or --scoring-config for custom values.",
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
            f"Example: nhl-scrabble analyze --format {output_format} --output report.{output_format}",
        )

    # Validate template format requires --template option
    if output_format == "template" and not template:
        raise click.ClickException(
            "Template format requires --template option\n"
            "Example: nhl-scrabble analyze --format template --template custom.j2",
        )

    # Validate output path BEFORE making API calls
    validate_output_path(output)

    # Display header
    console.print(f"\n[bold cyan]{_('🏒 NHL Roster Scrabble Score Analyzer 🏒')}[/bold cyan]\n")
    console.print(_("=") * 80)

    try:
        # Parse sheets list for Excel export
        sheets_list = None
        if sheets:
            sheets_list = [s.strip() for s in sheets.split(",")]

        # Create filters from CLI options
        filters = AnalysisFilters.from_options(
            division=divisions,
            conference=conferences,
            teams=teams,
            exclude=exclude_teams,
            countries=countries,
            positions=positions,
            min_score=min_score,
            max_score=max_score,
        )

        # Log active filters
        if filters.is_active():
            logger.debug(f"Active filters: {filters}")
            if not quiet:
                console.print(f"\n[yellow]{_('Filters active:')}[/yellow]")
                if filters.divisions:
                    console.print(
                        _("  • Divisions: {divisions}").format(
                            divisions=", ".join(sorted(filters.divisions)),
                        ),
                    )
                if filters.conferences:
                    console.print(
                        _("  • Conferences: {conferences}").format(
                            conferences=", ".join(sorted(filters.conferences)),
                        ),
                    )
                if filters.teams:
                    console.print(
                        _("  • Teams: {teams}").format(teams=", ".join(sorted(filters.teams))),
                    )
                if filters.excluded_teams:
                    console.print(
                        _("  • Excluded: {excluded}").format(
                            excluded=", ".join(sorted(filters.excluded_teams)),
                        ),
                    )
                if filters.countries:
                    console.print(
                        _("  • Countries: {countries}").format(
                            countries=", ".join(sorted(filters.countries)),
                        ),
                    )
                if filters.positions:
                    console.print(
                        _("  • Positions: {positions}").format(
                            positions=", ".join(sorted(filters.positions)),
                        ),
                    )
                if filters.min_score is not None:
                    console.print(
                        _("  • Min score: {min_score}").format(min_score=filters.min_score),
                    )
                if filters.max_score is not None:
                    console.print(
                        _("  • Max score: {max_score}").format(max_score=filters.max_score),
                    )
                if group_by:
                    console.print(
                        _("  • Group by: {group_by}").format(group_by=group_by),
                    )
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
            season=season,
            template_file=template,
        )

        # Output results
        if validated_output:
            if isinstance(result, str):
                # Text/JSON output
                validated_output.write_text(result, encoding="utf-8")
            # CSV/Excel are written directly by exporters
            console.print(
                _("\n[green]✓[/green] Report saved to: {output}").format(output=validated_output),
            )
        elif isinstance(result, str):
            print(result)
        else:
            console.print(
                _("\n[yellow]⚠[/yellow] CSV/Excel formats require --output option"),
                style="yellow",
            )

        console.print(_("\n") + _("=") * 80)
        console.print(_("[green]✓ Analysis complete![/green]"))

    except NHLApiError as e:
        logger.error(f"NHL API error: {e}")
        console.print(_("\n[red]❌ NHL API Error: {error}[/red]").format(error=e), style="red")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        console.print(_("\n[red]❌ Unexpected error: {error}[/red]").format(error=e), style="red")
        sys.exit(1)
