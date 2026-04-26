"""Lazy report generation with on-demand evaluation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nhl_scrabble.reports.conference_report import ConferenceReporter
from nhl_scrabble.reports.division_report import DivisionReporter
from nhl_scrabble.reports.playoff_report import PlayoffReporter
from nhl_scrabble.reports.stats_report import StatsReporter
from nhl_scrabble.reports.team_report import TeamReporter

if TYPE_CHECKING:
    from nhl_scrabble.models.player import PlayerScore


class ReportGenerator:
    """Lazy report generator with on-demand evaluation.

    This class implements lazy evaluation for report generation, ensuring that reports
    are only computed when actually accessed. This improves performance when users only
    need specific reports rather than the complete output.

    Reports are cached after first generation to avoid recomputation.

    Example:
        >>> generator = ReportGenerator(
        ...     team_scores=team_scores,
        ...     all_players=all_players,
        ...     division_standings=division_standings,
        ...     conference_standings=conference_standings,
        ...     playoff_standings=playoff_standings,
        ...     top_players_count=20,
        ...     top_team_players_count=5
        ... )
        >>> # Only generates team report when accessed
        >>> print(generator.team_report)
        >>> # Playoff report only generated when needed
        >>> print(generator.playoff_report)
    """

    def __init__(
        self,
        team_scores: dict[str, Any],
        all_players: list[PlayerScore],
        division_standings: dict[str, Any],
        conference_standings: dict[str, Any],
        playoff_standings: dict[str, Any],
        top_players_count: int = 20,
        top_team_players_count: int = 5,
    ) -> None:
        """Initialize lazy report generator.

        Args:
            team_scores: Team scores dictionary
            all_players: List of all players
            division_standings: Division standings
            conference_standings: Conference standings
            playoff_standings: Playoff standings
            top_players_count: Number of top players to show in stats
            top_team_players_count: Number of top players per team to show
        """
        # Store data
        self._team_scores = team_scores
        self._all_players = all_players
        self._division_standings = division_standings
        self._conference_standings = conference_standings
        self._playoff_standings = playoff_standings

        # Initialize reporters
        self._conference_reporter = ConferenceReporter()
        self._division_reporter = DivisionReporter()
        self._playoff_reporter = PlayoffReporter()
        self._team_reporter = TeamReporter(top_players_per_team=top_team_players_count)
        self._stats_reporter = StatsReporter(top_players_count=top_players_count)

        # Cache for generated reports
        self._conference_report: str | None = None
        self._division_report: str | None = None
        self._playoff_report: str | None = None
        self._team_report: str | None = None
        self._stats_report: str | None = None

    @property
    def conference_report(self) -> str:
        """Generate conference report lazily.

        Returns:
            Formatted conference report string
        """
        if self._conference_report is None:
            self._conference_report = self._conference_reporter.generate(self._conference_standings)
        return self._conference_report

    @property
    def division_report(self) -> str:
        """Generate division report lazily.

        Returns:
            Formatted division report string
        """
        if self._division_report is None:
            self._division_report = self._division_reporter.generate(self._division_standings)
        return self._division_report

    @property
    def playoff_report(self) -> str:
        """Generate playoff report lazily.

        Returns:
            Formatted playoff report string
        """
        if self._playoff_report is None:
            self._playoff_report = self._playoff_reporter.generate(self._playoff_standings)
        return self._playoff_report

    @property
    def team_report(self) -> str:
        """Generate team report lazily.

        Returns:
            Formatted team report string
        """
        if self._team_report is None:
            self._team_report = self._team_reporter.generate(self._team_scores)
        return self._team_report

    @property
    def stats_report(self) -> str:
        """Generate stats report lazily.

        Returns:
            Formatted stats report string
        """
        if self._stats_report is None:
            self._stats_report = self._stats_reporter.generate(
                (self._all_players, self._division_standings, self._conference_standings),
            )
        return self._stats_report

    @property
    def full_report(self) -> str:
        """Generate complete report with all sections.

        Returns:
            Complete formatted report string with all sections
        """
        reports = [
            self.conference_report,
            self.division_report,
            self.playoff_report,
            self.team_report,
            self.stats_report,
        ]
        return "\n".join(reports) + "\n" + "=" * 80 + "\n"

    def get_report(self, report_type: str | None = None) -> str:
        """Get specific report or full report.

        Args:
            report_type: Type of report to generate. Options:
                - 'conference': Conference standings only
                - 'division': Division standings only
                - 'playoff': Playoff bracket only
                - 'team': Team scores only
                - 'stats': Statistics only
                - None: Full report (all sections)

        Returns:
            Requested report string

        Raises:
            ValueError: If report_type is not recognized
        """
        if report_type is None:
            return self.full_report

        # Use conditional logic to maintain lazy evaluation
        if report_type == "conference":
            return self.conference_report
        if report_type == "division":
            return self.division_report
        if report_type == "playoff":
            return self.playoff_report
        if report_type == "team":
            return self.team_report
        if report_type == "stats":
            return self.stats_report

        # Invalid report type
        valid_types = ["conference", "division", "playoff", "team", "stats"]
        raise ValueError(
            f"Unknown report type: {report_type}. Valid options: {', '.join(valid_types)}",
        )
