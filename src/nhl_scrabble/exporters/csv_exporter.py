"""CSV export functionality for NHL Scrabble reports.

.. deprecated:: 2.1.0
    Use :mod:`nhl_scrabble.formatters` instead. This module will be removed in version 3.0.0.
"""

from __future__ import annotations

import csv
import warnings
from pathlib import Path  # noqa: TC003
from typing import Any

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


class CSVExporter:
    """Export NHL Scrabble data to CSV format.

    .. deprecated:: 2.1.0
        Use :class:`~nhl_scrabble.formatters.csv_formatter.CSVFormatter` instead.
        CSVExporter will be removed in version 3.0.0.

    This class is deprecated. Use the formatter pattern instead:

    .. code-block:: python

        from nhl_scrabble.formatters import get_formatter

        formatter = get_formatter("csv")
        csv_string = formatter.format(data)
        Path("output.csv").write_text(csv_string)

    Examples:
        >>> # OLD (deprecated):
        >>> exporter = CSVExporter()  # doctest: +SKIP
        >>> exporter.export_team_scores(teams, Path("teams.csv"))  # doctest: +SKIP

        >>> # NEW (recommended):
        >>> from nhl_scrabble.formatters import get_formatter  # doctest: +SKIP
        >>> formatter = get_formatter('csv')  # doctest: +SKIP
        >>> Path("teams.csv").write_text(formatter.format(data))  # doctest: +SKIP
    """

    def __init__(self) -> None:
        """Initialize CSV exporter with deprecation warning."""
        warnings.warn(
            "CSVExporter is deprecated and will be removed in version 3.0.0. "
            "Use nhl_scrabble.formatters.get_formatter('csv') instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def export_team_scores(
        self, teams: dict[str, TeamScore] | list[TeamScore], output: Path
    ) -> None:
        """Export team scores to CSV file.

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            teams: Dictionary or list of TeamScore objects
            output: Output file path

        Raises:
            OSError: If file cannot be written
        """
        warnings.warn(
            "CSVExporter.export_team_scores() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Convert dict to list if necessary
        team_list = list(teams.values()) if isinstance(teams, dict) else teams

        # Sort by total score descending
        sorted_teams = sorted(team_list, key=lambda t: (t.total, t.avg_per_player), reverse=True)

        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Team",
                    "Division",
                    "Conference",
                    "Total Score",
                    "Player Count",
                    "Average Score",
                ]
            )

            for team in sorted_teams:
                writer.writerow(
                    [
                        team.abbrev,
                        team.division,
                        team.conference,
                        team.total,
                        team.player_count,
                        f"{team.avg_per_player:.2f}",
                    ]
                )

    def export_player_scores(self, players: list[PlayerScore], output: Path) -> None:
        """Export player scores to CSV file.

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            players: List of PlayerScore objects
            output: Output file path

        Raises:
            OSError: If file cannot be written
        """
        warnings.warn(
            "CSVExporter.export_player_scores() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Sort by score descending
        sorted_players = sorted(players, key=lambda p: p.full_score, reverse=True)

        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Player Name",
                    "Team",
                    "Division",
                    "Conference",
                    "First Name Score",
                    "Last Name Score",
                    "Total Score",
                ]
            )

            for player in sorted_players:
                writer.writerow(
                    [
                        player.full_name,
                        player.team,
                        player.division,
                        player.conference,
                        player.first_score,
                        player.last_score,
                        player.full_score,
                    ]
                )

    def export_division_standings(self, division_standings: dict[str, Any], output: Path) -> None:
        """Export division standings to CSV file.

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            division_standings: Dictionary of division standings
            output: Output file path

        Raises:
            OSError: If file cannot be written
        """
        warnings.warn(
            "CSVExporter.export_division_standings() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Division",
                    "Team",
                    "Total Score",
                    "Player Count",
                    "Average Score",
                ]
            )

            for division_name in sorted(division_standings.keys()):
                standing = division_standings[division_name]
                for team in standing.teams:
                    writer.writerow(
                        [
                            division_name,
                            team.abbrev,
                            team.total,
                            team.player_count,
                            f"{team.avg_per_player:.2f}",
                        ]
                    )

    def export_conference_standings(
        self, conference_standings: dict[str, Any], output: Path
    ) -> None:
        """Export conference standings to CSV file.

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            conference_standings: Dictionary of conference standings
            output: Output file path

        Raises:
            OSError: If file cannot be written
        """
        warnings.warn(
            "CSVExporter.export_conference_standings() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Conference",
                    "Team",
                    "Division",
                    "Total Score",
                    "Player Count",
                    "Average Score",
                ]
            )

            for conference_name in sorted(conference_standings.keys()):
                standing = conference_standings[conference_name]
                for team in standing.teams:
                    writer.writerow(
                        [
                            conference_name,
                            team.abbrev,
                            team.division,
                            team.total,
                            team.player_count,
                            f"{team.avg_per_player:.2f}",
                        ]
                    )

    def export_playoff_standings(self, playoff_standings: dict[str, Any], output: Path) -> None:
        """Export playoff standings to CSV file.

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            playoff_standings: Dictionary of playoff standings by conference
            output: Output file path

        Raises:
            OSError: If file cannot be written
        """
        warnings.warn(
            "CSVExporter.export_playoff_standings() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Conference",
                    "Seed",
                    "Team",
                    "Division",
                    "Total Score",
                    "Average Score",
                    "Status",
                ]
            )

            for conference_name in sorted(playoff_standings.keys()):
                teams = playoff_standings[conference_name]
                for seed, team in enumerate(teams, start=1):
                    writer.writerow(
                        [
                            conference_name,
                            seed,
                            team.abbrev,
                            team.division,
                            team.total,
                            f"{team.avg:.2f}",
                            team.status_indicator,
                        ]
                    )
