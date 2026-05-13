"""Excel report generation for CLI."""

from __future__ import annotations

import logging
from pathlib import Path

import click

from nhl_scrabble.exporters.excel_exporter import ExcelExporter
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import (
    ConferenceStandings,
    DivisionStandings,
    PlayoffTeam,
)
from nhl_scrabble.models.team import TeamScore

logger = logging.getLogger(__name__)


def generate_excel_report(
    team_scores: dict[str, TeamScore],
    all_players: list[PlayerScore],
    division_standings: dict[str, DivisionStandings],
    conference_standings: dict[str, ConferenceStandings],
    playoff_standings: dict[str, list[PlayoffTeam]],
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

    Example:
        >>> from pathlib import Path
        >>> generate_excel_report(
        ...     team_scores={"TOR": team_score},
        ...     all_players=[player1, player2],
        ...     division_standings={"Atlantic": div_standings},
        ...     conference_standings={"Eastern": conf_standings},
        ...     playoff_standings={"Eastern": [team1, team2]},
        ...     output=Path("report.xlsx"),
        ...     sheets=["Teams", "Players"],  # Optional: limit sheets
        ... )
        # Creates report.xlsx with Teams and Players sheets
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
