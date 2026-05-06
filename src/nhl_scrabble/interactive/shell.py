"""Interactive shell for NHL Scrabble."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table

from nhl_scrabble.i18n import get_translator

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

            self.console.print(f"[green]{_('Data loaded successfully!')}[/green]")

            if failed_teams:
                self.console.print(
                    f"[yellow]⚠ {_('Warning: Failed to fetch')} {len(failed_teams)} {_('teams')}: "
                    f"{', '.join(failed_teams)}[/yellow]",
                )

    def get_completer(self) -> WordCompleter:
        """Get command completer with team/player names."""
        if not self.data:
            return WordCompleter(self.commands, ignore_case=True)

        # Add team abbreviations
        teams = [team.abbrev for team in self.data["teams"]]

        # Add player names (first 100 for performance)
        players: list[str] = []
        for team in self.data["teams"]:
            players.extend([p.full_name for p in team.players[:10]])

        words = self.commands + teams + players[:100]
        return WordCompleter(words, ignore_case=True)

    def run(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """Run interactive shell."""
        self.console.print(f"\n[bold cyan]{_('NHL Scrabble Interactive Mode')}[/bold cyan]")
        self.console.print(f"{_('Type')} [yellow]'help'[/yellow] {_('for available commands')}")
        self.console.print(f"{_('Type')} [yellow]'exit'[/yellow] {_('to quit')}\n")

        while True:
            try:
                completer = self.get_completer()

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
                elif command == "refresh":
                    self.cmd_refresh(args)
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

    def _find_team(self, abbrev: str) -> TeamScore | None:
        """Find team by abbreviation."""
        if not self.data:
            return None

        teams: list[TeamScore] = self.data["teams"]
        for team in teams:
            if team.abbrev.upper() == abbrev.upper():
                return team
        return None

    def _find_player(self, name: str) -> PlayerScore | None:  # noqa: C901
        """Find player by name (fuzzy match)."""
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

    def _display_team(self, team: TeamScore) -> None:
        """Display team details."""
        table = Table(title=f"{team.abbrev} ({team.abbrev})")
        table.add_column(_("Attribute"), style="cyan")
        table.add_column(_("Value"), style="green")

        table.add_row(_("Conference"), team.conference)
        table.add_row(_("Division"), team.division)
        table.add_row(_("Total Score"), str(team.total))
        table.add_row(_("Players"), str(len(team.players)))
        table.add_row(_("Average Score"), f"{team.avg_per_player:.2f}")

        self.console.print(table)
        self.console.print()

        # Show top players
        top_players = sorted(team.players, key=lambda p: p.full_score, reverse=True)[:10]

        player_table = Table(title=_("Top 10 Players"))
        player_table.add_column(_("Rank"), style="cyan", width=6)
        player_table.add_column(_("Player"), style="green", width=25)
        player_table.add_column(_("Score"), style="magenta", width=8)

        for i, player in enumerate(top_players, 1):
            player_table.add_row(str(i), player.full_name, str(player.full_score))

        self.console.print(player_table)

    def _display_player(self, player: PlayerScore) -> None:
        """Display player details."""
        table = Table(title=player.full_name)
        table.add_column(_("Attribute"), style="cyan")
        table.add_column(_("Value"), style="green")

        table.add_row(_("Team"), player.team)
        table.add_row(_("First Name"), player.first_name)
        table.add_row(_("Last Name"), player.last_name)
        table.add_row(_("Scrabble Score"), str(player.full_score))

        self.console.print(table)

    def cmd_show(self, args: list[str]) -> None:
        """Show team or player details."""
        if not args:
            self.console.print(
                f"[yellow]{_('Usage: show team <abbrev> | show player <name>')}[/yellow]",
            )
            return

        if args[0] == "team":
            if len(args) < 2:
                self.console.print(f"[yellow]{_('Usage: show team <abbrev>')}[/yellow]")
                return

            abbrev = args[1].upper()
            team = self._find_team(abbrev)
            if team:
                self._display_team(team)
            else:
                self.console.print(f"[red]{_('Team not found')}: {abbrev}[/red]")

        elif args[0] == "player":
            if len(args) < 2:
                self.console.print(f"[yellow]{_('Usage: show player <name>')}[/yellow]")
                return

            name = " ".join(args[1:])
            player = self._find_player(name)
            if player:
                self._display_player(player)
            else:
                self.console.print(f"[red]{_('Player not found')}: {name}[/red]")
        else:
            self.console.print(
                f"[yellow]{_('Usage: show team <abbrev> | show player <name>')}[/yellow]",
            )

    def cmd_top(self, args: list[str]) -> None:
        """Show top N players."""
        try:
            n = int(args[0]) if args else 10
        except ValueError:
            self.console.print(f"[red]{_('Error: N must be a number')}[/red]")
            return

        # Collect all players
        all_players: list[PlayerScore] = []
        for team in self.data["teams"]:  # type: ignore[index]
            all_players.extend(team.players)

        # Sort by score
        top_players = sorted(all_players, key=lambda p: p.full_score, reverse=True)[:n]

        table = Table(title=_("Top {} Players").format(n))
        table.add_column(_("Rank"), style="cyan", width=6)
        table.add_column(_("Player"), style="green", width=25)
        table.add_column(_("Team"), style="blue", width=6)
        table.add_column(_("Score"), style="magenta", width=8)

        for i, player in enumerate(top_players, 1):
            table.add_row(str(i), player.full_name, player.team, str(player.full_score))

        self.console.print(table)

    def cmd_bottom(self, args: list[str]) -> None:
        """Show bottom N players."""
        try:
            n = int(args[0]) if args else 10
        except ValueError:
            self.console.print(f"[red]{_('Error: N must be a number')}[/red]")
            return

        # Collect all players
        all_players: list[PlayerScore] = []
        for team in self.data["teams"]:  # type: ignore[index]
            all_players.extend(team.players)

        # Sort by score (ascending)
        bottom_players = sorted(all_players, key=lambda p: p.full_score)[:n]

        table = Table(title=_("Bottom {} Players").format(n))
        table.add_column(_("Rank"), style="cyan", width=6)
        table.add_column(_("Player"), style="green", width=25)
        table.add_column(_("Team"), style="blue", width=6)
        table.add_column(_("Score"), style="magenta", width=8)

        for i, player in enumerate(bottom_players, 1):
            table.add_row(str(i), player.full_name, player.team, str(player.full_score))

        self.console.print(table)

    def cmd_compare(self, args: list[str]) -> None:
        """Compare two players."""
        if len(args) < 2:
            self.console.print(f"[yellow]{_('Usage: compare <player1> <player2>')}[/yellow]")
            return

        # Find split point between player names
        # Try to find first player name, then second
        name1 = args[0]
        name2_parts = args[1:]

        player1 = self._find_player(name1)

        # If first name not found, try multi-word first name
        if not player1 and len(args) > 2:
            name1 = " ".join(args[:2])
            player1 = self._find_player(name1)
            name2_parts = args[2:]

        if not player1:
            self.console.print(f"[red]{_('Player not found')}: {name1}[/red]")
            return

        name2 = " ".join(name2_parts)
        player2 = self._find_player(name2)

        if not player2:
            self.console.print(f"[red]{_('Player not found')}: {name2}[/red]")
            return

        # Display comparison
        table = Table(title=_("Player Comparison"))
        table.add_column(_("Attribute"), style="cyan")
        table.add_column(player1.full_name, style="green")
        table.add_column(player2.full_name, style="blue")

        table.add_row(_("Team"), player1.team, player2.team)
        table.add_row(_("Scrabble Score"), str(player1.full_score), str(player2.full_score))

        diff = abs(player1.full_score - player2.full_score)
        table.add_row(_("Difference"), str(diff), str(diff))

        self.console.print(table)

        if player1.full_score > player2.full_score:
            self.console.print(f"\n[green]{player1.full_name}[/green] {_('has a higher score')}")
        elif player2.full_score > player1.full_score:
            self.console.print(f"\n[blue]{player2.full_name}[/blue] {_('has a higher score')}")
        else:
            self.console.print(f"\n[yellow]{_('Tied!')}[/yellow]")

    def _display_team_list(self, teams: list[TeamScore], title: str) -> None:
        """Display list of teams."""
        table = Table(title=title)
        table.add_column(_("Rank"), style="cyan", width=6)
        table.add_column(_("Team"), style="green", width=25)
        table.add_column(_("Score"), style="magenta", width=8)

        for i, team in enumerate(teams, 1):
            table.add_row(str(i), team.abbrev, str(team.total))

        self.console.print(table)

    def cmd_filter(self, args: list[str]) -> None:
        """Filter teams by division or conference."""
        if not args:
            self.console.print(
                f"[yellow]{_('Usage: filter division <div> | filter conference <conf>')}[/yellow]",
            )
            return

        filter_type = args[0].lower()

        if filter_type == "division":
            if len(args) < 2:
                self.console.print(f"[yellow]{_('Usage: filter division <div>')}[/yellow]")
                return

            division = " ".join(args[1:])
            teams = [t for t in self.data["teams"] if division.lower() in t.division.lower()]  # type: ignore[index]

            if not teams:
                self.console.print(f"[red]{_('No teams found in division')}: {division}[/red]")
                return

            self._display_team_list(teams, _("Teams in {}").format(division))

        elif filter_type == "conference":
            if len(args) < 2:
                self.console.print(f"[yellow]{_('Usage: filter conference <conf>')}[/yellow]")
                return

            conference = " ".join(args[1:])
            teams = [
                t
                for t in self.data["teams"]  # type: ignore[index]
                if conference.lower() in t.conference.lower()
            ]

            if not teams:
                self.console.print(f"[red]{_('No teams found in conference')}: {conference}[/red]")
                return

            self._display_team_list(teams, _("Teams in {} Conference").format(conference))

        else:
            self.console.print(
                f"[yellow]{_('Usage: filter division <div> | filter conference <conf>')}[/yellow]",
            )

    def cmd_search(self, args: list[str]) -> None:
        """Search players by name."""
        if not args:
            self.console.print(f"[yellow]{_('Usage: search <query>')}[/yellow]")
            return

        if not self.data:
            self.console.print(
                f"[red]{_('No data loaded. Use')} 'refresh' {_('to fetch data.')}[/red]",
            )
            return

        query = " ".join(args).lower()

        # Find all matching players
        teams: list[TeamScore] = self.data["teams"]
        matches: list[PlayerScore] = [
            player for team in teams for player in team.players if query in player.full_name.lower()
        ]

        if not matches:
            self.console.print(f"[red]{_('No players found matching')}: {query}[/red]")
            return

        table = Table(title=_("Search Results for '{}'").format(query))
        table.add_column(_("Player"), style="green", width=25)
        table.add_column(_("Team"), style="blue", width=6)
        table.add_column(_("Score"), style="magenta", width=8)

        for player in sorted(matches, key=lambda p: p.full_score, reverse=True):
            table.add_row(player.full_name, player.team, str(player.full_score))

        self.console.print(table)
        self.console.print(f"\n{_('Found')} {len(matches)} {_('player(s)')}")

    def cmd_standings(self, args: list[str]) -> None:
        """Show standings."""
        standings_type = args[0].lower() if args else "team"

        if standings_type == "team":
            # Show team standings
            teams = sorted(self.data["teams"], key=lambda t: t.total, reverse=True)  # type: ignore[index]

            table = Table(title=_("Team Standings"))
            table.add_column(_("Rank"), style="cyan", width=6)
            table.add_column(_("Team"), style="green", width=25)
            table.add_column(_("Conference"), style="blue", width=10)
            table.add_column(_("Division"), style="yellow", width=15)
            table.add_column(_("Score"), style="magenta", width=8)

            for i, team in enumerate(teams, 1):
                table.add_row(str(i), team.abbrev, team.conference, team.division, str(team.total))

            self.console.print(table)

        elif standings_type == "division":
            # Group by division
            divisions: dict[str, list[TeamScore]] = {}
            for team in self.data["teams"]:  # type: ignore[index]
                if team.division not in divisions:
                    divisions[team.division] = []
                divisions[team.division].append(team)

            for division, teams in sorted(divisions.items()):
                teams_sorted = sorted(teams, key=lambda t: t.total, reverse=True)
                self._display_team_list(teams_sorted, _("{} Division").format(division))
                self.console.print()

        elif standings_type == "conference":
            # Show conference standings
            self._display_team_list(
                sorted(self.data["eastern"], key=lambda t: t.total, reverse=True),  # type: ignore[index]
                _("Eastern Conference"),
            )
            self.console.print()
            self._display_team_list(
                sorted(self.data["western"], key=lambda t: t.total, reverse=True),  # type: ignore[index]
                _("Western Conference"),
            )

        else:
            self.console.print(
                f"[yellow]{_('Usage: standings [team|division|conference]')}[/yellow]",
            )

    def cmd_playoff(self, _args: list[str]) -> None:
        """Show playoff bracket."""
        playoff_teams = self.data["playoff_teams"]  # type: ignore[index]

        # Eastern Conference
        eastern = [t for t in playoff_teams if t.conference == "Eastern"]
        eastern_sorted = sorted(eastern, key=lambda t: t.total, reverse=True)

        # Western Conference
        western = [t for t in playoff_teams if t.conference == "Western"]
        western_sorted = sorted(western, key=lambda t: t.total, reverse=True)

        # Display Eastern
        table = Table(title=_("Eastern Conference Playoff Teams"))
        table.add_column(_("Seed"), style="cyan", width=6)
        table.add_column(_("Team"), style="green", width=25)
        table.add_column(_("Division"), style="yellow", width=15)
        table.add_column(_("Score"), style="magenta", width=8)

        for i, team in enumerate(eastern_sorted, 1):
            table.add_row(str(i), team.abbrev, team.division, str(team.total))

        self.console.print(table)
        self.console.print()

        # Display Western
        table = Table(title=_("Western Conference Playoff Teams"))
        table.add_column(_("Seed"), style="cyan", width=6)
        table.add_column(_("Team"), style="green", width=25)
        table.add_column(_("Division"), style="yellow", width=15)
        table.add_column(_("Score"), style="magenta", width=8)

        for i, team in enumerate(western_sorted, 1):
            table.add_row(str(i), team.abbrev, team.division, str(team.total))

        self.console.print(table)

    def cmd_stats(self, _args: list[str]) -> None:
        """Show statistics."""
        teams = self.data["teams"]  # type: ignore[index]

        # Collect stats
        total_teams = len(teams)
        total_players = sum(len(t.players) for t in teams)
        total_score = sum(t.total for t in teams)
        avg_team_score = total_score / total_teams if total_teams > 0 else 0

        # Top team
        top_team = max(teams, key=lambda t: t.total)

        # All players
        all_players: list[PlayerScore] = []
        for team in teams:
            all_players.extend(team.players)

        top_player = max(all_players, key=lambda p: p.full_score)
        avg_player_score = sum(p.full_score for p in all_players) / len(all_players)

        # Display stats
        table = Table(title=_("NHL Scrabble Statistics"))
        table.add_column(_("Statistic"), style="cyan")
        table.add_column(_("Value"), style="green")

        table.add_row(_("Total Teams"), str(total_teams))
        table.add_row(_("Total Players"), str(total_players))
        table.add_row(_("Total Score"), str(total_score))
        table.add_row(_("Average Team Score"), f"{avg_team_score:.2f}")
        table.add_row(_("Average Player Score"), f"{avg_player_score:.2f}")
        table.add_row(_("Top Team"), f"{top_team.abbrev} ({top_team.total})")
        table.add_row(_("Top Player"), f"{top_player.full_name} ({top_player.full_score})")

        self.console.print(table)

    def cmd_refresh(self, _args: list[str]) -> None:
        """Re-fetch data from NHL API."""
        self.fetch_data()

    def cmd_help(self, args: list[str]) -> None:
        """Show help."""
        if args:
            # Help for specific command
            command = args[0]
            help_text = {
                "show": _("show team <abbrev> | show player <name> - Display details"),
                "top": _("top [N] - Show top N players (default: 10)"),
                "bottom": _("bottom [N] - Show bottom N players (default: 10)"),
                "compare": _("compare <player1> <player2> - Compare two players"),
                "filter": _("filter division <div> | filter conference <conf>"),
                "search": _("search <query> - Search players by name"),
                "standings": _("standings [team|division|conference] - Show standings"),
                "playoff": _("playoff - Show playoff bracket"),
                "stats": _("stats - Show statistics"),
                "refresh": _("refresh - Re-fetch data from NHL API"),
                "help": _("help [command] - Show help"),
                "exit": _("exit | quit - Exit interactive mode"),
            }

            if command in help_text:
                self.console.print(help_text[command])
            else:
                self.console.print(f"[red]{_('No help available for')}: {command}[/red]")
        else:
            # General help
            table = Table(title=_("Available Commands"), show_header=False)
            table.add_column(_("Command"), style="cyan", width=30)
            table.add_column(_("Description"), style="white")

            table.add_row("show team <abbrev>", _("Show team details"))
            table.add_row("show player <name>", _("Show player details"))
            table.add_row("top [N]", _("Show top N players"))
            table.add_row("bottom [N]", _("Show bottom N players"))
            table.add_row("compare <p1> <p2>", _("Compare two players"))
            table.add_row("filter division <div>", _("Filter by division"))
            table.add_row("filter conference <conf>", _("Filter by conference"))
            table.add_row("search <query>", _("Search players"))
            table.add_row("standings [type]", _("Show standings"))
            table.add_row("playoff", _("Show playoff bracket"))
            table.add_row("stats", _("Show statistics"))
            table.add_row("refresh", _("Re-fetch data"))
            table.add_row("help [command]", _("Show help"))
            table.add_row("exit", _("Exit"))

            self.console.print(table)
            self.console.print(
                f"\n[yellow]{_('Tip: Type')} 'help <command>' {_('for detailed help on a specific command')}[/yellow]",
            )
