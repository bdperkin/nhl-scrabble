"""Dashboard command for NHL Scrabble CLI."""

from __future__ import annotations

import logging
import sys
from typing import TypedDict

import click
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiError
from nhl_scrabble.config import Config
from nhl_scrabble.dashboard import StatisticsDashboard
from nhl_scrabble.di import DependencyContainer
from nhl_scrabble.i18n import _
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.ui.progress import ProgressManager

logger = logging.getLogger(__name__)
console = Console()


class DashboardData(TypedDict):
    """Type definition for dashboard data dictionary.

    Attributes:
        team_scores: Dictionary of team abbreviations to team scores
        all_players: List of all players with scores
        division_standings: Division-level standings
        conference_standings: Conference-level standings
    """

    team_scores: dict[str, TeamScore]
    all_players: list[PlayerScore]
    division_standings: dict[str, DivisionStandings]
    conference_standings: dict[str, ConferenceStandings]


def fetch_dashboard_data(
    config: Config,
    quiet: bool = False,
    season: str | None = None,
) -> DashboardData | None:
    """Fetch data needed for dashboard.

    Uses dependency injection to create properly configured components.

    Args:
        config: Configuration object
        quiet: Whether to suppress progress bars
        season: Optional season to analyze (format: YYYYYYYY, e.g., 20222023)

    Returns:
        Dictionary with team_scores, all_players, division_standings,
        conference_standings, or None if fetching failed
    """
    # Initialize components using dependency injection
    container = DependencyContainer(config)

    # Use api_client as context manager for automatic cleanup
    with container.create_api_client() as api_client:
        scorer = container.create_scorer()
        team_processor = container.create_team_processor(
            api_client=api_client,
            scorer=scorer,
        )

        # Create progress manager
        progress_mgr = ProgressManager(enabled=not quiet)

        # Get team count for progress tracking
        teams_info = api_client.get_teams(season=season)
        total_teams = len(teams_info)

        # Process all teams with progress tracking
        with progress_mgr.track_api_fetching(total_teams):
            team_scores, all_players, failed_teams = team_processor.process_all_teams(season=season)

        # Display summary (only if not quiet)
        if not quiet:
            console.print(
                f"\n[green]✓[/green] Successfully fetched {len(team_scores)} of "
                f"{len(team_scores) + len(failed_teams)} teams",
            )
            if failed_teams:
                console.print(
                    _("[yellow]⚠[/yellow]  Failed teams: {teams}").format(
                        teams=", ".join(failed_teams),
                    ),
                )

        # Calculate standings
        division_standings = team_processor.calculate_division_standings(team_scores)
        conference_standings = team_processor.calculate_conference_standings(team_scores)

        return {
            "team_scores": team_scores,
            "all_players": all_players,
            "division_standings": division_standings,
            "conference_standings": conference_standings,
        }


@click.command()
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
    help=_("Suppress progress bars and status messages during data fetching"),
)
# === Data Source Options ===
@click.option(
    "--no-cache",
    is_flag=True,
    help=_("Disable API response caching (always fetch fresh data)"),
)
# === Dashboard Options ===
@click.option(
    "--duration",
    type=click.IntRange(min=1),
    help=_("Run dashboard for specified seconds (default: until Ctrl+C, range: 1+)"),
)
@click.option(
    "--static",
    is_flag=True,
    help=_("Display static snapshot instead of live dashboard"),
)
# === Filtering Options ===
@click.option(
    "--divisions",
    help=_("Filter by division (e.g., Atlantic, Metropolitan, Central, Pacific)"),
)
@click.option(
    "--conferences",
    help=_("Filter by conference (Eastern or Western)"),
)
@click.help_option("-h", "--help")
def dashboard(
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    duration: int | None,
    static: bool,
    divisions: str | None,
    conferences: str | None,
) -> None:
    r"""Launch interactive statistics dashboard.

    Displays live statistics with charts and visualizations using Rich library.
    Shows top teams, players, division and conference standings in an interactive
    terminal dashboard.

    Press Ctrl+C to exit the dashboard.

    \b
    Examples:
      Launch live dashboard with auto-updates:
        $ nhl-scrabble dashboard

      Filter dashboard by division:
        $ nhl-scrabble dashboard --divisions Atlantic

      Filter dashboard by conference:
        $ nhl-scrabble dashboard --conferences Eastern

      Run for specific duration (30 seconds):
        $ nhl-scrabble dashboard --duration 30

      Display static snapshot (no live updates):
        $ nhl-scrabble dashboard --static

      Suppress progress bars during data fetch:
        $ nhl-scrabble dashboard --quiet

      Enable verbose logging:
        $ nhl-scrabble dashboard --verbose

      Disable API caching for fresh data:
        $ nhl-scrabble dashboard --no-cache

      Combine multiple options:
        $ nhl-scrabble dashboard --divisions Metropolitan --static
        $ nhl-scrabble dashboard --conferences Western --duration 60 --quiet
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
            division_filter=divisions,
            conference_filter=conferences,
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
        console.print(_("\n[red]❌ Unexpected error: {error}[/red]").format(error=e), style="red")
        sys.exit(1)
