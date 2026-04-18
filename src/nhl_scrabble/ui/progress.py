"""Progress bar management for NHL Scrabble."""

from collections.abc import Callable, Generator
from contextlib import contextmanager

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)


class ProgressManager:
    """Manage progress bars for NHL Scrabble operations.

    Provides context managers for different operation types with rich progress bars.
    """

    def __init__(self, enabled: bool = True) -> None:
        """Initialize progress manager.

        Args:
            enabled: Whether to show progress bars (disable for --quiet mode)
        """
        self.enabled = enabled
        self._progress: Progress | None = None

    @contextmanager
    def create_progress(self) -> Generator[Progress | None, None, None]:
        """Create rich Progress instance with custom columns.

        Yields:
            Progress instance if enabled, None otherwise
        """
        if not self.enabled:
            yield None
            return

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[status]}"),
        )

        try:
            progress.start()
            self._progress = progress
            yield progress
        finally:
            progress.stop()
            self._progress = None

    @contextmanager
    def track_api_fetching(self, total_teams: int) -> Generator[Callable[[str], None], None, None]:
        """Track API fetching progress.

        Args:
            total_teams: Total number of teams to fetch

        Yields:
            Function to update progress after each team
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda _: None
                return

            task = progress.add_task("Fetching team rosters", total=total_teams, status="")

            def update(team_abbrev: str) -> None:
                """Update progress after fetching a team."""
                progress.update(task, advance=1, status=f"[green]{team_abbrev}")

            yield update

    @contextmanager
    def track_score_calculation(
        self, total_players: int
    ) -> Generator[Callable[[], None], None, None]:
        """Track score calculation progress.

        Args:
            total_players: Total number of players to score

        Yields:
            Function to update progress after each player
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda: None
                return

            task = progress.add_task("Calculating Scrabble scores", total=total_players, status="")

            def update() -> None:
                """Update progress after scoring a player."""
                progress.update(task, advance=1)

            yield update

    @contextmanager
    def track_report_generation(
        self, total_reports: int
    ) -> Generator[Callable[[str], None], None, None]:
        """Track report generation progress.

        Args:
            total_reports: Total number of reports to generate

        Yields:
            Function to update progress after each report
        """
        with self.create_progress() as progress:
            if progress is None:
                yield lambda _: None
                return

            task = progress.add_task("Generating reports", total=total_reports, status="")

            def update(report_name: str) -> None:
                """Update progress after generating a report."""
                progress.update(task, advance=1, status=f"[yellow]{report_name}")

            yield update
