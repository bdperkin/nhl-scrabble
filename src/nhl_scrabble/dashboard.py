"""Interactive statistics dashboard with Rich visualizations."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from nhl_scrabble.models.player import PlayerScore


class StatisticsDashboard:
    """Interactive terminal dashboard for NHL Scrabble statistics.

    Displays live statistics with charts and visualizations using Rich library.
    Supports filtering by division, conference, and real-time updates.

    Example:
        >>> dashboard = StatisticsDashboard(
        ...     team_scores=team_scores,
        ...     all_players=all_players,
        ...     division_standings=division_standings,
        ...     conference_standings=conference_standings,
        ... )
        >>> dashboard.run()  # Launches interactive dashboard
    """

    def __init__(
        self,
        team_scores: dict[str, Any],
        all_players: list[PlayerScore],
        division_standings: dict[str, Any],
        conference_standings: dict[str, Any],
        division_filter: str | None = None,
        conference_filter: str | None = None,
    ) -> None:
        """Initialize the statistics dashboard.

        Args:
            team_scores: Dictionary mapping team abbreviations to TeamScore objects
            all_players: List of all PlayerScore objects
            division_standings: Dictionary of division standings
            conference_standings: Dictionary of conference standings
            division_filter: Optional division filter (e.g., 'Atlantic', 'Metropolitan')
            conference_filter: Optional conference filter (e.g., 'Eastern', 'Western')
        """
        self.team_scores = team_scores
        self.all_players = all_players
        self.division_standings = division_standings
        self.conference_standings = conference_standings
        self.division_filter = division_filter
        self.conference_filter = conference_filter
        self.console = Console()

    def _create_header(self) -> Panel:
        """Create the dashboard header with title and stats summary.

        Returns:
            Rich Panel with header content
        """
        title = Text("🏒 NHL Scrabble Statistics Dashboard 🏒", style="bold cyan")

        # Calculate summary statistics
        total_teams = len(self.team_scores)
        total_players = len(self.all_players)
        total_score = sum(p.full_score for p in self.all_players)
        avg_score = total_score / total_players if total_players > 0 else 0

        summary = Text()
        summary.append(f"Teams: {total_teams}  ", style="green")
        summary.append(f"Players: {total_players}  ", style="blue")
        summary.append(f"Avg Score: {avg_score:.1f}", style="yellow")

        # Add filters if present
        if self.division_filter:
            summary.append(f"\nDivision: {self.division_filter}", style="magenta")
        if self.conference_filter:
            summary.append(f"\nConference: {self.conference_filter}", style="magenta")

        content = Group(Align.center(title), Align.center(summary))

        return Panel(content, border_style="cyan")

    def _create_top_teams_table(self, limit: int = 10) -> Table:
        """Create table showing top teams by total score.

        Args:
            limit: Maximum number of teams to display

        Returns:
            Rich Table with top teams
        """
        table = Table(title="🏆 Top Teams by Total Score", show_header=True, header_style="bold")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Team", style="cyan")
        table.add_column("Division", style="blue")
        table.add_column("Conference", style="green")
        table.add_column("Total", justify="right", style="yellow")
        table.add_column("Players", justify="right", style="magenta")
        table.add_column("Avg/Player", justify="right", style="white")

        # Filter teams if needed
        teams = list(self.team_scores.values())
        if self.division_filter:
            teams = [t for t in teams if t.division == self.division_filter]
        if self.conference_filter:
            teams = [t for t in teams if t.conference == self.conference_filter]

        # Sort by total score descending
        sorted_teams = sorted(teams, key=lambda t: (t.total, t.avg_per_player), reverse=True)

        # Add top teams to table
        for rank, team in enumerate(sorted_teams[:limit], start=1):
            table.add_row(
                f"#{rank}",
                team.abbrev,
                team.division,
                team.conference,
                str(team.total),
                str(team.player_count),
                f"{team.avg_per_player:.1f}",
            )

        return table

    def _create_top_players_table(self, limit: int = 10) -> Table:
        """Create table showing top players by score.

        Args:
            limit: Maximum number of players to display

        Returns:
            Rich Table with top players
        """
        table = Table(title="⭐ Top Players by Score", show_header=True, header_style="bold")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Player", style="cyan")
        table.add_column("Team", style="blue")
        table.add_column("First", justify="right", style="green")
        table.add_column("Last", justify="right", style="yellow")
        table.add_column("Total", justify="right", style="bold magenta")

        # Filter players if needed
        players = self.all_players
        if self.division_filter or self.conference_filter:
            # Get team abbreviations matching filters
            filtered_teams = set()
            for abbrev, team in self.team_scores.items():
                if self.division_filter and team.division != self.division_filter:
                    continue
                if self.conference_filter and team.conference != self.conference_filter:
                    continue
                filtered_teams.add(abbrev)

            # Filter players by team
            players = [p for p in players if p.team in filtered_teams]

        # Sort by total score descending
        sorted_players = sorted(players, key=lambda p: p.full_score, reverse=True)

        # Add top players to table
        for rank, player in enumerate(sorted_players[:limit], start=1):
            table.add_row(
                f"#{rank}",
                f"{player.first_name} {player.last_name}",
                player.team,
                str(player.first_score),
                str(player.last_score),
                str(player.full_score),
            )

        return table

    def _create_division_standings_table(self) -> Table:
        """Create table showing division standings.

        Returns:
            Rich Table with division standings
        """
        table = Table(title="📊 Division Standings", show_header=True, header_style="bold")
        table.add_column("Division", style="cyan")
        table.add_column("Teams", justify="right", style="blue")
        table.add_column("Total Score", justify="right", style="yellow")
        table.add_column("Avg/Team", justify="right", style="green")
        table.add_column("Top Team", style="magenta")

        # Filter divisions if needed
        divisions = self.division_standings.copy()
        if self.division_filter:
            divisions = {k: v for k, v in divisions.items() if k == self.division_filter}

        # Sort by total score descending
        sorted_divisions = sorted(divisions.items(), key=lambda x: x[1].total, reverse=True)

        for div_name, standing in sorted_divisions:
            # Find top team in this division
            div_teams = [t for t in self.team_scores.values() if t.division == div_name]
            top_team = max(div_teams, key=lambda t: t.total) if div_teams else None
            top_team_abbrev = top_team.abbrev if top_team else "N/A"

            table.add_row(
                div_name,
                str(len(standing.teams)),
                str(standing.total),
                f"{standing.avg_per_team:.1f}",
                top_team_abbrev,
            )

        return table

    def _create_conference_standings_table(self) -> Table:
        """Create table showing conference standings.

        Returns:
            Rich Table with conference standings
        """
        table = Table(title="🏟️  Conference Standings", show_header=True, header_style="bold")
        table.add_column("Conference", style="cyan")
        table.add_column("Teams", justify="right", style="blue")
        table.add_column("Total Score", justify="right", style="yellow")
        table.add_column("Avg/Team", justify="right", style="green")
        table.add_column("Top Team", style="magenta")

        # Filter conferences if needed
        conferences = self.conference_standings.copy()
        if self.conference_filter:
            conferences = {k: v for k, v in conferences.items() if k == self.conference_filter}

        # Sort by total score descending
        sorted_conferences = sorted(conferences.items(), key=lambda x: x[1].total, reverse=True)

        for conf_name, standing in sorted_conferences:
            # Find top team in this conference
            conf_teams = [t for t in self.team_scores.values() if t.conference == conf_name]
            top_team = max(conf_teams, key=lambda t: t.total) if conf_teams else None
            top_team_abbrev = top_team.abbrev if top_team else "N/A"

            table.add_row(
                conf_name,
                str(len(standing.teams)),
                str(standing.total),
                f"{standing.avg_per_team:.1f}",
                top_team_abbrev,
            )

        return table

    def _create_layout(self) -> Layout:
        """Create the dashboard layout structure.

        Returns:
            Rich Layout with all dashboard components
        """
        # Create main layout
        layout = Layout()

        # Split into header and body
        layout.split_column(Layout(name="header", size=5), Layout(name="body"))

        # Split body into two columns
        layout["body"].split_row(Layout(name="left"), Layout(name="right"))

        # Split left column into standings
        layout["left"].split_column(
            Layout(name="divisions", ratio=1), Layout(name="conferences", ratio=1)
        )

        # Split right column into teams and players
        layout["right"].split_column(Layout(name="teams", ratio=1), Layout(name="players", ratio=1))

        # Populate layout with content
        layout["header"].update(self._create_header())
        layout["divisions"].update(Panel(self._create_division_standings_table()))
        layout["conferences"].update(Panel(self._create_conference_standings_table()))
        layout["teams"].update(Panel(self._create_top_teams_table()))
        layout["players"].update(Panel(self._create_top_players_table()))

        return layout

    def run(self, refresh_interval: float = 1.0, duration: int | None = None) -> None:
        """Run the interactive dashboard.

        Args:
            refresh_interval: Time in seconds between dashboard refreshes (default: 1.0)
            duration: Optional duration in seconds to run dashboard.
                If None, runs until interrupted. (default: None)

        Example:
            >>> dashboard.run()  # Run until Ctrl+C
            >>> dashboard.run(duration=10)  # Run for 10 seconds
        """
        start_time = time.time()

        try:
            with Live(
                self._create_layout(),
                console=self.console,
                refresh_per_second=1 / refresh_interval,
                screen=True,
            ) as live:
                # Keep dashboard running
                while True:
                    # Check if duration limit reached
                    if duration is not None:
                        elapsed = time.time() - start_time
                        if elapsed >= duration:
                            break

                    # Update layout (in future this could be dynamic data)
                    live.update(self._create_layout())
                    time.sleep(refresh_interval)

        except KeyboardInterrupt:
            # Graceful exit on Ctrl+C
            self.console.print("\n[yellow]Dashboard closed.[/yellow]")

    def display_static(self) -> None:
        """Display a static snapshot of the dashboard without live updates.

        Useful for quick viewing or when live updates are not needed.
        """
        self.console.print(self._create_layout())
