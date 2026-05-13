"""Search command for NHL Scrabble CLI."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

import click
from rich.console import Console

from nhl_scrabble.api.nhl_client import NHLApiError
from nhl_scrabble.cli.validators import validate_output_path
from nhl_scrabble.config import Config
from nhl_scrabble.di import DependencyContainer
from nhl_scrabble.i18n import _
from nhl_scrabble.logging_config import setup_logging
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.search import PlayerSearch

logger = logging.getLogger(__name__)
console = Console()


def generate_search_text(  # noqa: PLR0913  # Need all search parameters
    results: list[PlayerScore],
    query: str | None,
    fuzzy: bool,
    min_score: int | None,
    max_score: int | None,
    teams: str | None,
    divisions: str | None,
    conferences: str | None,
    limit: int,
) -> str:
    """Generate text format search results.

    Args:
        results: List of PlayerScore objects
        query: Search query
        fuzzy: Whether fuzzy matching was used
        min_score: Minimum score filter
        max_score: Maximum score filter
        teams: Team filter
        divisions: Division filter
        conferences: Conference filter
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
    if teams:
        lines.append(f"  Team: {teams}")
    if divisions:
        lines.append(f"  Division: {divisions}")
    if conferences:
        lines.append(f"  Conference: {conferences}")

    lines.append(f"\nFound {len(results)} player(s)")
    if limit and len(results) >= limit:
        lines.append(f"(showing top {limit})")
    lines.append("\n" + "-" * 80 + "\n")

    # Display results
    if results:
        for i, player in enumerate(results, 1):
            lines.append(
                f"{i:3d}. {player.full_name:<30} | Score: {player.full_score:3d} | "
                f"Team: {player.team:4s} | {player.division}",
            )
            lines.append(
                f"     First: {player.first_name} ({player.first_score}) | "
                f"Last: {player.last_name} ({player.last_score})",
            )
            lines.append("")
    else:
        lines.append("No players found matching the search criteria.\n")

    lines.append("-" * 80)

    return "\n".join(lines)


def generate_search_json(
    results: list[PlayerScore],
    query: str | None,
    stats: dict[str, int | float],
) -> str:
    """Generate JSON format search results.

    Args:
        results: List of PlayerScore objects
        query: Search query
        stats: Player database statistics (counts and averages)

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


@click.command()
@click.argument("query", required=False)
# === Search Options ===
@click.option(
    "--fuzzy",
    "-f",
    is_flag=True,
    help=_("Enable fuzzy matching for approximate name searches"),
)
@click.option(
    "--limit",
    "-n",
    type=click.IntRange(min=1, max=500),
    default=20,
    help=_("Maximum number of results to show (default: 20, range: 1-500)"),
)
# === Output Options ===
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help=_("Output format (default: text)"),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help=_("Output file path (default: stdout)"),
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
@click.option(
    "--no-cache",
    is_flag=True,
    help=_("Disable API response caching (always fetch fresh data)"),
)
# === Filtering Options ===
@click.option(
    "--min-score",
    type=int,
    help=_("Minimum Scrabble score to include"),
)
@click.option(
    "--max-score",
    type=int,
    help=_("Maximum Scrabble score to include"),
)
@click.option(
    "--teams",
    "-t",
    help=_("Filter by team abbreviation (e.g., TOR, MTL)"),
)
@click.option(
    "--divisions",
    "-d",
    help=_("Filter by division name (e.g., Atlantic, Metropolitan)"),
)
@click.option(
    "--conferences",
    "-c",
    help=_("Filter by conference name (Eastern or Western)"),
)
@click.help_option("-h", "--help")
def search(  # noqa: PLR0912, PLR0913  # CLI function with many branches and parameters
    query: str | None,
    fuzzy: bool,
    limit: int,
    output_format: str,
    output: str | None,
    verbose: bool,
    quiet: bool,
    no_cache: bool,
    min_score: int | None,
    max_score: int | None,
    teams: str | None,
    divisions: str | None,
    conferences: str | None,
) -> None:
    r"""Search for players by name and filter by attributes.

    Search the NHL player database by name with support for exact matching,
    fuzzy matching, and wildcard patterns. Filter results by score, team,
    division, or conference.

    \b
    Examples:
      Exact search by player name:
        $ nhl-scrabble search "Connor McDavid"

      Fuzzy search (approximate matching):
        $ nhl-scrabble search McDavid --fuzzy

      Wildcard search with pattern:
        $ nhl-scrabble search "Connor*"

      Filter by minimum score:
        $ nhl-scrabble search --min-score 50

      Filter by team:
        $ nhl-scrabble search --teams TOR

      Filter by division:
        $ nhl-scrabble search --divisions Atlantic

      Filter by conference:
        $ nhl-scrabble search --conferences Eastern

      Limit number of results:
        $ nhl-scrabble search --min-score 40 --limit 10

      JSON format output:
        $ nhl-scrabble search McDavid --fuzzy --format json

      Save results to file:
        $ nhl-scrabble search --min-score 60 --output high-scorers.txt

      Disable caching (fetch fresh data):
        $ nhl-scrabble search McDavid --no-cache

      Combine multiple filters:
        $ nhl-scrabble search "Connor*" --teams EDM --min-score 40
        $ nhl-scrabble search --divisions Metropolitan --min-score 50 --output metro-high.txt
    """
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

    logger.info("Starting NHL player search")

    # Validate output path
    validate_output_path(output)

    try:
        # Fetch player data
        if not quiet:
            console.print(_("\n[bold cyan]🔍 NHL Player Search 🔍[/bold cyan]\n"))
            console.print(_("=") * 80)

        # Initialize components using dependency injection
        container = DependencyContainer(config)

        # Use api_client as context manager for automatic cleanup
        with container.create_api_client() as api_client:
            scorer = container.create_scorer()
            team_processor = container.create_team_processor(
                api_client=api_client,
                scorer=scorer,
            )

            # Process all teams (progress handled internally by TeamProcessor)
            _team_scores, all_players, failed_teams = team_processor.process_all_teams()

            # Display summary (only if not quiet)
            if not quiet and failed_teams:
                console.print(
                    _("[yellow]⚠[/yellow]  Failed teams: {teams}").format(
                        teams=", ".join(failed_teams),
                    ),
                )

            # Create search instance
            searcher = PlayerSearch(all_players)

            # Perform search
            results = searcher.search(
                query or "",
                fuzzy=fuzzy,
                min_score=min_score,
                max_score=max_score,
                team=teams,
                division=divisions,
                conference=conferences,
            )

            # Limit results
            if limit and len(results) > limit:
                results = results[:limit]

            # Generate output
            if output_format == "json":
                output_text = generate_search_json(results, query, searcher.get_stats())
            else:
                output_text = generate_search_text(
                    results,
                    query,
                    fuzzy,
                    min_score,
                    max_score,
                    teams,
                    divisions,
                    conferences,
                    limit,
                )

            # Output results
            if output:
                Path(output).write_text(output_text, encoding="utf-8")
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
        console.print(_("\n[red]❌ Unexpected error: {error}[/red]").format(error=e), style="red")
        sys.exit(1)
