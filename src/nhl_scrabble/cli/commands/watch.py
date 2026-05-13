"""Watch command for NHL Scrabble CLI."""

from __future__ import annotations

import logging
import signal
import time
import types
from contextlib import suppress
from datetime import UTC, datetime

import click
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiError
from nhl_scrabble.cli.orchestration import run_analysis
from nhl_scrabble.config import Config
from nhl_scrabble.i18n import _, format_datetime
from nhl_scrabble.logging_config import setup_logging

logger = logging.getLogger(__name__)
console = Console()


def _interruptible_sleep(seconds: int, shutdown_flag: list[bool]) -> None:
    """Sleep for specified seconds, checking shutdown flag every second.

    Args:
        seconds: Number of seconds to sleep
        shutdown_flag: Mutable list containing shutdown boolean flag
    """
    for _i in range(seconds):
        if shutdown_flag[0]:
            return
        time.sleep(1)


@click.command()
# === Watch Options ===
@click.option(
    "--interval",
    type=click.IntRange(min=1),
    default=300,
    help=_("Refresh interval in seconds (default: 300 = 5 minutes, range: 1+)"),
)
# === Output Options ===
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help=_("Output format (default: text)"),
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
@click.help_option("-h", "--help")
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
    r"""Watch mode - automatically refresh data at intervals.

    Runs continuous analysis with auto-refresh, useful for monitoring
    roster changes during active periods.

    Press Ctrl+C to stop watching.

    \b
    Examples:
      Watch with default 5-minute interval (300 seconds):
        $ nhl-scrabble watch

      Custom 1-minute interval:
        $ nhl-scrabble watch --interval 60

      Watch specific report with 30-second interval:
        $ nhl-scrabble watch --report team --interval 30

      Watch with JSON output format:
        $ nhl-scrabble watch --format json --interval 120

      Watch with custom player display limits:
        $ nhl-scrabble watch --top-players 30 --top-team-players 10

      Suppress progress bars:
        $ nhl-scrabble watch --quiet --interval 60

      Enable verbose logging for debugging:
        $ nhl-scrabble watch --verbose

      Disable API caching for fresh data:
        $ nhl-scrabble watch --no-cache

      Combine multiple options:
        $ nhl-scrabble watch --interval 120 --report playoff --quiet
        $ nhl-scrabble watch --format json --top-players 50 --interval 300
    """
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
        "\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer - Watch Mode 🏒[/bold cyan]\n",
    )
    console.print("=" * 80)
    console.print(f"[yellow]Auto-refresh every {interval} seconds (Ctrl+C to stop)[/yellow]\n")
    console.print("=" * 80)

    # Use list to allow modification in nested function (mutable container)
    shutdown_flag = [False]

    def signal_handler(_signum: int, _frame: types.FrameType | None) -> None:
        """Handle Ctrl+C gracefully."""
        shutdown_flag[0] = True
        console.print("\n\n[yellow]⏹  Stopping watch mode...[/yellow]")

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Watch loop
    iteration = 0
    with suppress(KeyboardInterrupt):
        while not shutdown_flag[0]:
            iteration += 1
            timestamp = format_datetime(datetime.now(tz=UTC), format="medium") + " UTC"

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
                        f"\n[dim]Next refresh in {interval} seconds... (Press Ctrl+C to stop)[/dim]",
                    )
                    _interruptible_sleep(interval, shutdown_flag)

            except NHLApiError as e:
                logger.error(f"NHL API error: {e}")
                console.print(f"[red]❌ NHL API Error: {e}[/red]", style="red")
                console.print("[yellow]Will retry on next iteration...[/yellow]")

                # Wait before retry
                if not shutdown_flag[0]:
                    console.print(
                        f"\n[dim]Retrying in {interval} seconds... (Press Ctrl+C to stop)[/dim]",
                    )
                    _interruptible_sleep(interval, shutdown_flag)

            except Exception as e:
                logger.exception("Unexpected error during watch iteration")
                console.print(f"[red]❌ Unexpected error: {e}[/red]", style="red")
                console.print("[yellow]Will retry on next iteration...[/yellow]")

                # Wait before retry
                if not shutdown_flag[0]:
                    console.print(
                        f"\n[dim]Retrying in {interval} seconds... (Press Ctrl+C to stop)[/dim]",
                    )
                    _interruptible_sleep(interval, shutdown_flag)

    # Clean shutdown
    console.print("\n" + "=" * 80)
    console.print(f"[green]✓ Watch mode stopped after {iteration} updates[/green]")
