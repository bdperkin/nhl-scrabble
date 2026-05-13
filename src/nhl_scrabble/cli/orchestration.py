"""Analysis orchestration for CLI."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING

from rich.console import Console

from nhl_scrabble.config import Config
from nhl_scrabble.di import DependencyContainer
from nhl_scrabble.filters import AnalysisFilters
from nhl_scrabble.i18n import _
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.reports.generator import ReportGenerator
from nhl_scrabble.ui.progress import ProgressManager

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)
console = Console()


def run_analysis(  # noqa: PLR0913  # Complex analysis orchestration function with many parameters
    config: Config,
    clear_cache: bool = False,
    report_filter: str | None = None,
    quiet: bool = False,
    output_path: Path | None = None,
    sheets: list[str] | None = None,
    scoring_values: dict[str, int] | None = None,
    filters: AnalysisFilters | None = None,
    season: str | None = None,
    template_file: str | None = None,
) -> str | None:
    """Run the complete NHL Scrabble analysis.

    Uses dependency injection to create properly configured components, making
    the function easier to test and maintain.

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
        season: Optional season to analyze (format: YYYYYYYY, e.g., 20222023).
            If None, analyzes current season.
        template_file: Optional path to Jinja2 template file (for template format)

    Returns:
        Complete report string for text/JSON/YAML/XML/HTML/Table/Markdown/Template formats,
        or None for CSV/Excel (CSV/Excel are written directly to output file)

    Raises:
        NHLApiError: If there are issues fetching data from NHL API
    """
    # Import generate_excel_report locally to avoid circular imports
    from nhl_scrabble.cli.excel import generate_excel_report  # noqa: PLC0415

    # Create dependency container
    container = DependencyContainer(config)

    # Use api_client as context manager for automatic cleanup
    with container.create_api_client() as api_client:
        # Initialize components using dependency injection
        scorer = container.create_scorer(letter_values=scoring_values)
        team_processor = container.create_team_processor(
            api_client=api_client,
            scorer=scorer,
        )
        playoff_calculator = PlayoffCalculator()

        # Clear cache if requested
        if clear_cache:
            api_client.clear_cache()
            logger.info("API cache cleared")

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
        playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

        # Apply filters if specified
        if filters and filters.is_active():
            from nhl_scrabble.filters import (  # noqa: PLC0415
                filter_conference_standings,
                filter_division_standings,
                filter_players,
                filter_playoff_standings,
                filter_teams,
            )

            logger.debug("Applying filters to analysis results")
            team_scores = filter_teams(team_scores, filters)
            all_players = filter_players(all_players, filters)
            division_standings = filter_division_standings(division_standings, filters)
            conference_standings = filter_conference_standings(conference_standings, filters)
            playoff_standings = filter_playoff_standings(playoff_standings, filters)

            # Log filter results
            if not quiet:
                console.print(
                    f"\n[green]✓[/green] Filters applied: {len(team_scores)} teams, "
                    f"{len(all_players)} players",
                )

        # Excel format uses special exporter (multi-sheet workbook)
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

        # For text format, use the existing rich report generator
        if config.output_format == "text":
            report_generator = ReportGenerator(
                team_scores=team_scores,
                all_players=all_players,
                division_standings=division_standings,
                conference_standings=conference_standings,
                playoff_standings=playoff_standings,
                top_players_count=config.top_players_count,
                top_team_players_count=config.top_team_players_count,
            )
            return report_generator.get_report(report_filter)

        # For all other formats, use the formatter factory
        from nhl_scrabble.formatters import get_formatter  # noqa: PLC0415

        # Prepare data dictionary for formatters
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
        conferences_data = {
            name: asdict(standing) for name, standing in conference_standings.items()
        }
        playoffs_data = {
            conf: [asdict(team) for team in teams] for conf, teams in playoff_standings.items()
        }

        formatter_data = {
            "teams": teams_data,
            "divisions": divisions_data,
            "conferences": conferences_data,
            "playoffs": playoffs_data,
            "summary": {
                "total_teams": len(team_scores),
                "total_players": len(all_players),
            },
        }

        # Get appropriate formatter
        formatter_kwargs = {}
        if config.output_format == "template":
            formatter_kwargs["template_file"] = template_file

        formatter = get_formatter(config.output_format, **formatter_kwargs)

        # Generate and return formatted output
        return formatter.format(formatter_data)
