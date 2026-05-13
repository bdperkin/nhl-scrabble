"""Interactive shell for NHL Scrabble."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from nhl_scrabble.i18n import get_translator
from nhl_scrabble.interactive.commands import CommandHandler
from nhl_scrabble.interactive.completion import get_completer

if TYPE_CHECKING:
    from nhl_scrabble.models.player import PlayerScore
    from nhl_scrabble.models.team import TeamScore

# Get translator for interactive shell
_ = get_translator()


class InteractiveShell:
    """Interactive REPL for NHL Scrabble data exploration.

    Provides commands for querying and exploring NHL Scrabble scores interactively.
    """

    def __init__(self) -> None:
        """Initialize interactive shell."""
        self.data: dict[str, Any] | None = None
        self.history_file = Path.home() / ".nhl_scrabble_history"
        self.session: PromptSession[str] = PromptSession(
            history=FileHistory(str(self.history_file)),
        )
        self.console = Console()

        # Available commands
        self.commands = [
            "show",
            "top",
            "bottom",
            "compare",
            "filter",
            "search",
            "standings",
            "playoff",
            "stats",
            "refresh",
            "help",
            "exit",
            "quit",
        ]

        # Prompt style
        self.style = Style.from_dict(
            {
                "prompt": "#00aa00 bold",
                "command": "#0000ff",
            },
        )

        # Command handler (initialized after data is loaded)
        self.cmd_handler: CommandHandler | None = None

    def _find_team(self, abbrev: str) -> TeamScore | None:
        """Find team by abbreviation.

        Args:
            abbrev: Team abbreviation to search for

        Returns:
            TeamScore if found, None otherwise
        """
        if not self.data:
            return None

        teams: list[TeamScore] = self.data["teams"]
        for team in teams:
            if team.abbrev.upper() == abbrev.upper():
                return team
        return None

    def _find_player(self, name: str) -> PlayerScore | None:  # noqa: C901
        """Find player by name (fuzzy match).

        Args:
            name: Player name to search for

        Returns:
            PlayerScore if found, None otherwise
        """
        if not self.data:
            return None

        name_lower = name.lower()
        teams: list[TeamScore] = self.data["teams"]

        # Exact match first
        for team in teams:
            for player in team.players:
                if player.full_name.lower() == name_lower:
                    return player

        # Partial match (last name)
        for team in teams:
            for player in team.players:
                if name_lower in player.last_name.lower():
                    return player

        # Partial match (any part)
        for team in teams:
            for player in team.players:
                if name_lower in player.full_name.lower():
                    return player

        return None

    # Display methods (proxy to formatting module for backward compatibility)
    def _display_team(self, team: TeamScore) -> None:
        """Display team details (proxy to formatting module).

        Args:
            team: Team score to display
        """
        from nhl_scrabble.interactive.formatting import display_team  # noqa: PLC0415

        display_team(team, self.console)

    def _display_player(self, player: PlayerScore) -> None:
        """Display player details (proxy to formatting module).

        Args:
            player: Player score to display
        """
        from nhl_scrabble.interactive.formatting import display_player  # noqa: PLC0415

        display_player(player, self.console)

    def _display_team_list(self, teams: list[TeamScore], title: str) -> None:
        """Display list of teams (proxy to formatting module).

        Args:
            teams: List of team scores to display
            title: Table title
        """
        from nhl_scrabble.interactive.formatting import display_team_list  # noqa: PLC0415

        display_team_list(teams, title, self.console)

    def fetch_data(self) -> None:
        """Fetch NHL data from API."""
        # Imports inside method to avoid circular dependencies
        from nhl_scrabble.api.nhl_client import NHLApiClient  # noqa: PLC0415
        from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator  # noqa: PLC0415
        from nhl_scrabble.processors.team_processor import TeamProcessor  # noqa: PLC0415
        from nhl_scrabble.scoring.scrabble import ScrabbleScorer  # noqa: PLC0415

        self.console.print(f"[cyan]{_('Fetching NHL data...')}[/cyan]")

        # Create processors with API client context manager
        scorer = ScrabbleScorer()

        with NHLApiClient() as api_client:
            team_processor = TeamProcessor(api_client, scorer)

            # Process all teams
            team_scores_dict, all_players, failed_teams = team_processor.process_all_teams()

            # Calculate playoff positions
            playoff_calculator = PlayoffCalculator()
            playoff_standings_data = playoff_calculator.calculate_playoff_standings(
                team_scores_dict,
            )

            # Extract playoff teams from standings
            playoff_teams = []
            for conf_teams in playoff_standings_data.values():
                playoff_teams.extend(conf_teams)

            # Convert dict to list for easier iteration
            team_scores_list = list(team_scores_dict.values())

            # Organize by conference
            eastern_teams = [t for t in team_scores_list if t.conference == "Eastern"]
            western_teams = [t for t in team_scores_list if t.conference == "Western"]

            self.data = {
                "teams": team_scores_list,
                "teams_dict": team_scores_dict,
                "all_players": all_players,
                "playoff_teams": playoff_teams,
                "playoff_standings": playoff_standings_data,
                "eastern": eastern_teams,
                "western": western_teams,
                "failed_teams": failed_teams,
            }

            # Initialize command handler with data
            self.cmd_handler = CommandHandler(
                self.data,
                self.console,
                self._find_team,
                self._find_player,
                self.fetch_data,
                self._display_team,
                self._display_player,
                self._display_team_list,
            )

            self.console.print(f"[green]{_('Data loaded successfully!')}[/green]")

            if failed_teams:
                self.console.print(
                    f"[yellow]⚠ {_('Warning: Failed to fetch')} {len(failed_teams)} {_('teams')}: "
                    f"{', '.join(failed_teams)}[/yellow]",
                )

    def run(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """Run interactive shell."""
        self.console.print(f"\n[bold cyan]{_('NHL Scrabble Interactive Mode')}[/bold cyan]")
        self.console.print(f"{_('Type')} [yellow]'help'[/yellow] {_('for available commands')}")
        self.console.print(f"{_('Type')} [yellow]'exit'[/yellow] {_('to quit')}\n")

        while True:
            try:
                completer = get_completer(self.commands, self.data)

                text = self.session.prompt(
                    "NHL Scrabble> ",
                    completer=completer,
                    style=self.style,
                )

                if not text.strip():
                    continue

                # Parse command
                try:
                    parts = shlex.split(text)
                except ValueError:
                    self.console.print(f"[red]{_('Error: Invalid command syntax')}[/red]")
                    continue

                command = parts[0].lower()
                args = parts[1:]

                # Check if data is loaded (except for help/exit/refresh)
                if command not in ("help", "exit", "quit", "refresh") and not self.data:
                    self.console.print(
                        f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
                    )
                    continue

                # Execute command
                if command in ("exit", "quit"):
                    break
                if command == "help":
                    self.cmd_help(args)
                elif command == "refresh":
                    self.cmd_refresh(args)
                elif command == "show":
                    self.cmd_show(args)
                elif command == "top":
                    self.cmd_top(args)
                elif command == "bottom":
                    self.cmd_bottom(args)
                elif command == "compare":
                    self.cmd_compare(args)
                elif command == "filter":
                    self.cmd_filter(args)
                elif command == "search":
                    self.cmd_search(args)
                elif command == "standings":
                    self.cmd_standings(args)
                elif command == "playoff":
                    self.cmd_playoff(args)
                elif command == "stats":
                    self.cmd_stats(args)
                else:
                    self.console.print(f"[red]{_('Unknown command')}: {command}[/red]")
                    self.console.print(
                        f"{_('Type')} [yellow]'help'[/yellow] {_('for available commands')}",
                    )

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

        self.console.print(f"\n[cyan]{_('Goodbye!')}[/cyan]")

    def _show_basic_help(self) -> None:
        """Show basic help when no data is loaded."""
        from rich.table import Table  # noqa: PLC0415

        table = Table(title=_("Available Commands"), show_header=False)
        table.add_column(_("Command"), style="cyan", width=30)
        table.add_column(_("Description"), style="white")

        table.add_row("refresh", _("Fetch NHL data"))
        table.add_row("help", _("Show this help"))
        table.add_row("exit", _("Exit interactive mode"))

        self.console.print(table)

    def _ensure_command_handler(self) -> None:
        """Ensure command handler is initialized (for backward compatibility)."""
        if not self.cmd_handler and self.data:
            self.cmd_handler = CommandHandler(
                self.data,
                self.console,
                self._find_team,
                self._find_player,
                self.fetch_data,
                self._display_team,
                self._display_player,
                self._display_team_list,
            )

    # Proxy methods to maintain backward compatibility with tests
    def cmd_show(self, args: list[str]) -> None:
        """Show team or player details (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_show(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_top(self, args: list[str]) -> None:
        """Show top N players (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_top(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_bottom(self, args: list[str]) -> None:
        """Show bottom N players (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_bottom(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_compare(self, args: list[str]) -> None:
        """Compare two players (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_compare(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_filter(self, args: list[str]) -> None:
        """Filter teams by division or conference (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_filter(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_search(self, args: list[str]) -> None:
        """Search players by name (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_search(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_standings(self, args: list[str]) -> None:
        """Show standings (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_standings(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_playoff(self, args: list[str]) -> None:
        """Show playoff bracket (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_playoff(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_stats(self, args: list[str]) -> None:
        """Show statistics (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_stats(args)
        else:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )

    def cmd_refresh(self, args: list[str]) -> None:  # noqa: ARG002
        """Re-fetch data from NHL API (proxy to command handler).

        Args:
            args: Command arguments
        """
        self.fetch_data()

    def cmd_help(self, args: list[str]) -> None:
        """Show help (proxy to command handler).

        Args:
            args: Command arguments
        """
        self._ensure_command_handler()
        if self.cmd_handler:
            self.cmd_handler.cmd_help(args)
        else:
            self._show_basic_help()

    def get_completer(self) -> Any:  # noqa: ANN401
        """Get command completer with team/player names (proxy to completion module).

        Returns:
            WordCompleter configured with commands and data
        """
        return get_completer(self.commands, self.data)
