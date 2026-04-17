# Add Interactive Mode (REPL)

**GitHub Issue**: #133 - https://github.com/bdperkin/nhl-scrabble/issues/133

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add an interactive REPL (Read-Eval-Print Loop) mode that allows users to explore NHL Scrabble data interactively through commands, rather than re-running the entire analysis for each query.

Currently the application only supports batch mode: run the analyzer, get a complete report, exit. Users cannot explore data interactively, compare specific players, or filter results without re-running the entire analysis (which takes 10-15 seconds). An interactive mode would enable ad-hoc queries and data exploration.

**Impact**: Better user experience, faster data exploration, more engaging interface, supports learning and discovery

## Current State

**Batch mode only**:

```bash
# Current workflow
$ nhl-scrabble analyze
# Wait 10-15 seconds for analysis
# See complete report
# Exit

# Want to see just one team? Re-run everything:
$ nhl-scrabble analyze | grep "Toronto"
# Another 10-15 second wait

# Want to compare two players? No direct way
# Must parse output manually
```

**Problems**:

1. No ad-hoc queries
1. Must re-run analysis for different views
1. No way to explore data incrementally
1. No comparison commands
1. No filtering/searching within results

## Proposed Solution

Add `nhl-scrabble interactive` command with REPL using prompt_toolkit:

**Interactive commands**:

```
show team <abbrev>          Show team details
show player <name>          Show player details
top [N]                     Show top N players (default: 10)
bottom [N]                  Show bottom N players
compare <name1> <name2>     Compare two players
filter division <div>       Filter by division
filter conference <conf>    Filter by conference
search <query>              Search players by name
standings [type]            Show standings (team/division/conference)
playoff                     Show playoff bracket
stats                       Show statistics
refresh                     Re-fetch data from NHL API
help [command]              Show help
exit                        Exit interactive mode
```

**Implementation**:

```python
# src/nhl_scrabble/cli.py
import click
from nhl_scrabble.interactive import InteractiveShell

@cli.command()
@click.option("--no-fetch", is_flag=True, help="Use cached data")
def interactive(no_fetch: bool):
    """Start interactive mode for exploring NHL Scrabble data."""
    shell = InteractiveShell()

    if not no_fetch:
        click.echo("Fetching NHL data...")
        shell.fetch_data()

    shell.run()
```

```python
# src/nhl_scrabble/interactive/shell.py
"""Interactive shell for NHL Scrabble."""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pathlib import Path
import shlex

class InteractiveShell:
    """Interactive REPL for NHL Scrabble data exploration."""

    def __init__(self):
        self.data = None
        self.history_file = Path.home() / ".nhl_scrabble_history"
        self.session = PromptSession(
            history=FileHistory(str(self.history_file))
        )

        # Command completer
        self.commands = [
            "show", "top", "bottom", "compare", "filter",
            "search", "standings", "playoff", "stats",
            "refresh", "help", "exit", "quit"
        ]

        # Style
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'command': '#0000ff',
        })

    def fetch_data(self):
        """Fetch NHL data."""
        from nhl_scrabble.api.nhl_client import NHLApiClient
        from nhl_scrabble.processors.team_processor import TeamProcessor

        client = NHLApiClient()
        standings = client.get_standings()

        team_scores = []
        for team in standings.teams:
            roster = client.get_team_roster(team.abbrev)
            score = TeamProcessor.process_roster(roster)
            team_scores.append(score)

        self.data = {
            'teams': team_scores,
            'standings': standings,
        }

    def get_completer(self):
        """Get command completer with team/player names."""
        if not self.data:
            return WordCompleter(self.commands)

        # Add team abbreviations
        teams = [team.abbrev for team in self.data['teams']]

        # Add player names (first 100 for performance)
        players = []
        for team in self.data['teams']:
            players.extend([p.name for p in team.players[:10]])

        words = self.commands + teams + players[:100]
        return WordCompleter(words, ignore_case=True)

    def run(self):
        """Run interactive shell."""
        print("NHL Scrabble Interactive Mode")
        print("Type 'help' for available commands, 'exit' to quit")
        print()

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
                    print("Error: Invalid command syntax")
                    continue

                command = parts[0].lower()
                args = parts[1:]

                # Execute command
                if command in ['exit', 'quit']:
                    break
                elif command == 'help':
                    self.cmd_help(args)
                elif command == 'show':
                    self.cmd_show(args)
                elif command == 'top':
                    self.cmd_top(args)
                elif command == 'bottom':
                    self.cmd_bottom(args)
                elif command == 'compare':
                    self.cmd_compare(args)
                elif command == 'filter':
                    self.cmd_filter(args)
                elif command == 'search':
                    self.cmd_search(args)
                elif command == 'standings':
                    self.cmd_standings(args)
                elif command == 'playoff':
                    self.cmd_playoff(args)
                elif command == 'stats':
                    self.cmd_stats(args)
                elif command == 'refresh':
                    self.cmd_refresh(args)
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

        print("\nGoodbye!")

    def cmd_show(self, args):
        """Show team or player details."""
        if not args:
            print("Usage: show team <abbrev> | show player <name>")
            return

        if args[0] == 'team':
            if len(args) < 2:
                print("Usage: show team <abbrev>")
                return

            abbrev = args[1].upper()
            team = self._find_team(abbrev)
            if team:
                self._display_team(team)
            else:
                print(f"Team not found: {abbrev}")

        elif args[0] == 'player':
            if len(args) < 2:
                print("Usage: show player <name>")
                return

            name = ' '.join(args[1:])
            player = self._find_player(name)
            if player:
                self._display_player(player)
            else:
                print(f"Player not found: {name}")
        else:
            print("Usage: show team <abbrev> | show player <name>")

    def cmd_top(self, args):
        """Show top N players."""
        n = int(args[0]) if args else 10

        # Collect all players
        all_players = []
        for team in self.data['teams']:
            all_players.extend(team.players)

        # Sort by score
        top_players = sorted(
            all_players, key=lambda p: p.score, reverse=True
        )[:n]

        print(f"\nTop {n} Players:")
        print(f"{'Rank':<6} {'Player':<25} {'Team':<6} {'Score':<8}")
        print("-" * 50)

        for i, player in enumerate(top_players, 1):
            print(f"{i:<6} {player.name:<25} {player.team:<6} {player.score:<8}")

    def cmd_compare(self, args):
        """Compare two players."""
        if len(args) < 2:
            print("Usage: compare <player1> <player2>")
            return

        # Find players (name might have spaces)
        # Simple: take first arg as player1, rest as player2
        name1 = args[0]
        name2 = ' '.join(args[1:])

        player1 = self._find_player(name1)
        player2 = self._find_player(name2)

        if not player1:
            print(f"Player not found: {name1}")
            return
        if not player2:
            print(f"Player not found: {name2}")
            return

        print(f"\nComparison:")
        print(f"{'Attribute':<20} {player1.name:<25} {player2.name:<25}")
        print("-" * 70)
        print(f"{'Team':<20} {player1.team:<25} {player2.team:<25}")
        print(f"{'Scrabble Score':<20} {player1.score:<25} {player2.score:<25}")
        print(f"{'Difference':<20} {abs(player1.score - player2.score)} points")

        if player1.score > player2.score:
            print(f"\n{player1.name} has a higher score")
        elif player2.score > player1.score:
            print(f"\n{player2.name} has a higher score")
        else:
            print(f"\nTied!")

    def cmd_help(self, args):
        """Show help."""
        if args:
            # Help for specific command
            command = args[0]
            help_text = {
                'show': 'show team <abbrev> | show player <name> - Display details',
                'top': 'top [N] - Show top N players (default: 10)',
                'bottom': 'bottom [N] - Show bottom N players',
                'compare': 'compare <player1> <player2> - Compare two players',
                'filter': 'filter division <div> | filter conference <conf>',
                'search': 'search <query> - Search players by name',
                'standings': 'standings [team|division|conference] - Show standings',
                'playoff': 'playoff - Show playoff bracket',
                'stats': 'stats - Show statistics',
                'refresh': 'refresh - Re-fetch data from NHL API',
                'help': 'help [command] - Show help',
                'exit': 'exit | quit - Exit interactive mode',
            }

            if command in help_text:
                print(help_text[command])
            else:
                print(f"No help available for: {command}")
        else:
            # General help
            print("\nAvailable Commands:")
            print("  show team <abbrev>          Show team details")
            print("  show player <name>          Show player details")
            print("  top [N]                     Show top N players")
            print("  bottom [N]                  Show bottom N players")
            print("  compare <p1> <p2>           Compare two players")
            print("  filter division <div>       Filter by division")
            print("  filter conference <conf>    Filter by conference")
            print("  search <query>              Search players")
            print("  standings [type]            Show standings")
            print("  playoff                     Show playoff bracket")
            print("  stats                       Show statistics")
            print("  refresh                     Re-fetch data")
            print("  help [command]              Show help")
            print("  exit                        Exit")
            print("\nType 'help <command>' for detailed help on a specific command")

    def _find_team(self, abbrev):
        """Find team by abbreviation."""
        for team in self.data['teams']:
            if team.abbrev.upper() == abbrev.upper():
                return team
        return None

    def _find_player(self, name):
        """Find player by name (fuzzy match)."""
        name_lower = name.lower()

        # Exact match first
        for team in self.data['teams']:
            for player in team.players:
                if player.name.lower() == name_lower:
                    return player

        # Partial match
        for team in self.data['teams']:
            for player in team.players:
                if name_lower in player.name.lower():
                    return player

        return None

    # ... other command implementations ...
```

## Implementation Steps

1. **Add prompt_toolkit dependency**:

   - Add to pyproject.toml
   - Run uv lock

1. **Create interactive module**:

   - Create `src/nhl_scrabble/interactive/` directory
   - Create `shell.py` with InteractiveShell class

1. **Implement commands**:

   - show, top, bottom, compare
   - filter, search, standings
   - playoff, stats, refresh, help

1. **Add tab completion**:

   - Command completion
   - Team name completion
   - Player name completion

1. **Add command history**:

   - Persistent history file
   - History navigation (up/down arrows)

1. **Add CLI command**:

   - `nhl-scrabble interactive`
   - --no-fetch flag for using cached data

1. **Add tests**:

   - Unit tests for commands
   - Integration tests for shell

1. **Update documentation**:

   - Document interactive mode
   - Add command reference

## Testing Strategy

**Manual testing**:

```bash
# Start interactive mode
$ nhl-scrabble interactive
# Should fetch data and start REPL

# Test commands
NHL Scrabble> show team TOR
NHL Scrabble> top 10
NHL Scrabble> compare McDavid Ovechkin
NHL Scrabble> help
NHL Scrabble> exit
```

## Acceptance Criteria

- [ ] prompt_toolkit dependency added
- [ ] Interactive module created
- [ ] `nhl-scrabble interactive` command works
- [ ] All commands implemented (show, top, bottom, compare, etc.)
- [ ] Tab completion works for commands
- [ ] Tab completion works for team names
- [ ] Command history persists across sessions
- [ ] Help system shows all commands
- [ ] --no-fetch flag skips data fetching
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/interactive/__init__.py` - New interactive module
- `src/nhl_scrabble/interactive/shell.py` - REPL implementation
- `src/nhl_scrabble/cli.py` - Add interactive command
- `pyproject.toml` - Add prompt_toolkit dependency
- `docs/tutorials/` - Add interactive mode tutorial

## Dependencies

**Python packages**:

- `prompt_toolkit>=3.0.0` - REPL framework (new dependency)

**No blocking dependencies** - Can be implemented immediately

## Additional Notes

**prompt_toolkit Features**:

- Tab completion
- Syntax highlighting
- Command history
- Multi-line input
- Vi/Emacs key bindings

**Future Enhancements**:

- Export current view to file
- Custom queries/filters
- Plotting/visualization
- Shell integration (pipe to other tools)

## Implementation Notes

*To be filled during implementation*
