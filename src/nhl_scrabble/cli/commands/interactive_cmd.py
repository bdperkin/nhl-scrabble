"""Interactive command for NHL Scrabble CLI."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console

from nhl_scrabble import __version__
from nhl_scrabble.config import Config
from nhl_scrabble.i18n import _
from nhl_scrabble.logging_config import setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option(
    "--no-fetch",
    is_flag=True,
    help=_("Skip fetching data from NHL API on startup"),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=_("Enable verbose logging"),
)
@click.option(
    "--no-cache",
    is_flag=True,
    help=_("Disable API response caching (always fetch fresh data)"),
)
@click.help_option("-h", "--help")
def interactive(no_fetch: bool, verbose: bool, no_cache: bool) -> None:
    r"""Start interactive mode for exploring NHL Scrabble data.

    Interactive mode provides a REPL (Read-Eval-Print Loop) for exploring
    NHL Scrabble scores through commands like show, top, compare, and more.

    \b
    Examples:
      Start interactive mode with data fetch:
        $ nhl-scrabble interactive

      Skip fetching data on startup:
        $ nhl-scrabble interactive --no-fetch

      Enable verbose logging for debugging:
        $ nhl-scrabble interactive --verbose

      Disable caching (fetch fresh data):
        $ nhl-scrabble interactive --no-cache

      Combine options:
        $ nhl-scrabble interactive --no-fetch --verbose
        $ nhl-scrabble interactive --no-fetch --no-cache
    """
    from nhl_scrabble.interactive import InteractiveShell  # noqa: PLC0415

    # Load configuration
    try:
        config = Config.from_env()
    except ValueError as e:
        # Convert config validation errors to ClickException for consistent error handling
        raise click.ClickException(f"Configuration error: {e}") from e

    config.verbose = verbose

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    # Setup logging
    setup_logging(verbose=verbose, sanitize_logs=config.sanitize_logs)

    logger.info(f"Starting NHL Scrabble interactive mode v{__version__}")

    try:
        shell = InteractiveShell()

        if not no_fetch:
            shell.fetch_data()

        shell.run()

    except KeyboardInterrupt:
        console.print(_("\n[cyan]Goodbye![/cyan]"))
        sys.exit(0)
    except Exception as e:
        logger.exception("Unexpected error in interactive mode")
        console.print(_("\n[red]❌ Unexpected error: {error}[/red]").format(error=e), style="red")
        sys.exit(1)
