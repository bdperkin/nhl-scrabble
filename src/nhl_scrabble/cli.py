"""Command-line interface for NHL Scrabble."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

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

logger = logging.getLogger(__name__)
console = Console()


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
def analyze(
    output_format: str,
    output: str | None,
    verbose: bool,
    top_players: int,
    top_team_players: int,
) -> None:
    """Run the NHL Scrabble analysis.

    Fetches current NHL roster data and generates comprehensive reports
    with Scrabble scores for all players and teams.

    Examples:
        nhl-scrabble analyze
        nhl-scrabble analyze --verbose
        nhl-scrabble analyze --output report.txt
        nhl-scrabble analyze --format json --output report.json
    """
    # Setup logging
    setup_logging(verbose=verbose)

    # Load configuration
    config = Config.from_env()
    config.verbose = verbose
    config.output_format = output_format
    config.top_players_count = top_players
    config.top_team_players_count = top_team_players

    logger.info(f"Starting NHL Scrabble analysis v{__version__}")
    logger.debug(f"Configuration: {config}")

    # Display header
    console.print("\n[bold cyan]🏒 NHL Roster Scrabble Score Analyzer 🏒[/bold cyan]\n")
    console.print("=" * 80)

    try:
        # Run the analysis
        result = run_analysis(config)

        # Output results
        if output:
            output_path = Path(output)
            output_path.write_text(result)
            console.print(f"\n[green]✓[/green] Report saved to: {output}")
        else:
            print(result)

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


def run_analysis(config: Config) -> str:
    """Run the complete NHL Scrabble analysis.

    Args:
        config: Configuration object

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
    )
    scorer = ScrabbleScorer()
    team_processor = TeamProcessor(api_client, scorer)
    playoff_calculator = PlayoffCalculator()

    # Initialize reporters
    conference_reporter = ConferenceReporter()
    division_reporter = DivisionReporter()
    playoff_reporter = PlayoffReporter()
    team_reporter = TeamReporter(top_players_per_team=config.top_team_players_count)
    stats_reporter = StatsReporter(top_players_count=config.top_players_count)

    # Process all teams with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching NHL rosters...", total=None)

        team_scores, all_players, failed_teams = team_processor.process_all_teams()

        progress.update(task, description="[green]✓ Rosters fetched")

    # Display summary
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
    # Generate text reports
    reports = [
        conference_reporter.generate(conference_standings),
        division_reporter.generate(division_standings),
        playoff_reporter.generate(playoff_standings),
        team_reporter.generate(team_scores),
        stats_reporter.generate(all_players, division_standings, conference_standings),
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


if __name__ == "__main__":
    cli()
