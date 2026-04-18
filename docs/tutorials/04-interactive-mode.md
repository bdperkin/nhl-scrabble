# Interactive Mode Tutorial

Learn how to use NHL Scrabble's interactive REPL mode to explore player and team data interactively.

## What is Interactive Mode?

Interactive mode provides a command-line REPL (Read-Eval-Print Loop) that lets you explore NHL Scrabble data through commands, without re-running the entire analysis for each query.

**Benefits**:

- **Fast queries**: Explore data without waiting for full analysis
- **Ad-hoc exploration**: Compare players, filter teams, search by name
- **No scripting needed**: Simple commands for common queries
- **Tab completion**: Command and name auto-completion
- **Command history**: Navigate previous commands with arrow keys

## Starting Interactive Mode

```bash
# Fetch data and start interactive mode
nhl-scrabble interactive

# Use cached data (from previous session)
nhl-scrabble interactive --no-fetch

# Enable verbose logging
nhl-scrabble interactive --verbose
```

When you start, you'll see:

```
NHL Scrabble Interactive Mode
Type 'help' for available commands
Type 'exit' to quit

NHL Scrabble>
```

## Basic Commands

### Show Team Details

View detailed information about a specific team:

```
NHL Scrabble> show team TOR
```

Output shows:

- Team conference and division
- Total Scrabble score
- Number of players
- Average score per player
- Top 10 players on the team

### Show Player Details

View information about a specific player:

```
NHL Scrabble> show player McDavid
```

Or use full name:

```
NHL Scrabble> show player Connor McDavid
```

Output shows:

- Player's team
- First and last name
- Scrabble score

## Exploring Top and Bottom Players

### Top Players

Show the highest-scoring players:

```
# Top 10 players (default)
NHL Scrabble> top

# Top 20 players
NHL Scrabble> top 20

# Top 50 players
NHL Scrabble> top 50
```

### Bottom Players

Show the lowest-scoring players:

```
# Bottom 10 players (default)
NHL Scrabble> bottom

# Bottom 20 players
NHL Scrabble> bottom 20
```

## Comparing Players

Compare two players side-by-side:

```
NHL Scrabble> compare McDavid Ovechkin
```

Or with full names:

```
NHL Scrabble> compare "Connor McDavid" "Alex Ovechkin"
```

Output shows:

- Both players' teams
- Their Scrabble scores
- The difference in points
- Which player has the higher score

## Filtering and Searching

### Filter by Division

Show all teams in a division:

```
NHL Scrabble> filter division Atlantic
NHL Scrabble> filter division Pacific
NHL Scrabble> filter division Metropolitan
NHL Scrabble> filter division Central
```

### Filter by Conference

Show all teams in a conference:

```
NHL Scrabble> filter conference Eastern
NHL Scrabble> filter conference Western
```

### Search for Players

Find players whose names contain a search term:

```
# Find all players with "ov" in their name
NHL Scrabble> search ov

# Find all Matthews
NHL Scrabble> search Matthews
```

Results are sorted by Scrabble score and show:

- Player name
- Team
- Score
- Total number of matches

## Viewing Standings

### Team Standings

Show all teams ranked by total score:

```
NHL Scrabble> standings
# or
NHL Scrabble> standings team
```

### Division Standings

Show teams grouped by division:

```
NHL Scrabble> standings division
```

### Conference Standings

Show teams grouped by conference:

```
NHL Scrabble> standings conference
```

## Playoff Information

View the playoff bracket:

```
NHL Scrabble> playoff
```

Shows:

- Top 8 teams from Eastern Conference
- Top 8 teams from Western Conference
- Seeds, teams, divisions, and scores

## Statistics

View overall NHL Scrabble statistics:

```
NHL Scrabble> stats
```

Shows:

- Total number of teams
- Total number of players
- Total combined score
- Average team score
- Average player score
- Top team and score
- Top player and score

## Refreshing Data

Re-fetch data from the NHL API without restarting:

```
NHL Scrabble> refresh
```

This is useful if:

- Rosters have changed
- You want fresh data
- Previous fetch had errors

## Getting Help

### General Help

Show all available commands:

```
NHL Scrabble> help
```

### Command-Specific Help

Get detailed help for a specific command:

```
NHL Scrabble> help show
NHL Scrabble> help compare
NHL Scrabble> help filter
```

## Tab Completion

Interactive mode supports tab completion for:

**Commands**: Type part of a command and press Tab:

```
NHL Scrabble> sh<TAB>
# Completes to: show
```

**Team abbreviations**: Auto-complete team names:

```
NHL Scrabble> show team TO<TAB>
# Completes to: TOR
```

**Player names**: Auto-complete player names (top 100 by score):

```
NHL Scrabble> show player McD<TAB>
# Completes to: McDavid
```

## Command History

Navigate previous commands using arrow keys:

- **Up arrow**: Go to previous command
- **Down arrow**: Go to next command
- **Ctrl+R**: Reverse search through history

Command history persists across sessions in `~/.nhl_scrabble_history`.

## Example Session

Here's a typical interactive session:

```bash
$ nhl-scrabble interactive
Fetching NHL data...
Data loaded successfully!

NHL Scrabble Interactive Mode
Type 'help' for available commands
Type 'exit' to quit

# Check top scorers
NHL Scrabble> top 5

# Look at a specific team
NHL Scrabble> show team EDM

# Compare two stars
NHL Scrabble> compare McDavid Ovechkin

# Search for players
NHL Scrabble> search kov

# View conference standings
NHL Scrabble> standings conference

# Exit when done
NHL Scrabble> exit

Goodbye!
```

## Tips and Tricks

**Speed Up Startup**: Use `--no-fetch` with cached data:

```bash
# First run: fetch data
nhl-scrabble interactive

# Subsequent runs: use cached data
nhl-scrabble interactive --no-fetch
```

**Case Insensitive**: All commands and searches are case-insensitive:

```
# These all work
NHL Scrabble> show team TOR
NHL Scrabble> show team tor
NHL Scrabble> SHOW TEAM TOR
```

**Partial Name Matching**: Player search uses fuzzy matching:

```
# Find McDavid
NHL Scrabble> show player mc
NHL Scrabble> show player McDavid
NHL Scrabble> show player Connor
```

**Quick Navigation**: Use Tab completion and history to work faster:

```
# Type "sh" then Tab to complete "show"
# Use Up arrow to repeat previous commands
# Use Ctrl+R to search command history
```

## Advanced Usage

### Combining with Shell Commands

Pipe interactive mode output:

```bash
# Save output
nhl-scrabble interactive > session.log

# Filter output
nhl-scrabble interactive | grep "Ovechkin"
```

### Scripting Interactive Commands

While interactive mode doesn't support batch input directly, you can use expect or similar tools:

```bash
#!/usr/bin/expect
spawn nhl-scrabble interactive --no-fetch
expect "NHL Scrabble>"
send "top 10\r"
expect "NHL Scrabble>"
send "exit\r"
expect eof
```

## Troubleshooting

**"No data loaded" error**:

```
NHL Scrabble> top
No data loaded. Use 'refresh' to fetch data.
```

**Solution**: Run `refresh` command or restart without `--no-fetch`.

**Player/team not found**:

```
NHL Scrabble> show player Smith
Player not found: Smith
```

**Solution**: Use more specific name (e.g., "Mike Smith") or search first:

```
NHL Scrabble> search Smith
```

**Command not recognized**:

```
NHL Scrabble> teams
Unknown command: teams
Type 'help' for available commands
```

**Solution**: Use `help` to see correct command name (`standings` in this case).

## Next Steps

- **Learn more about output**: See [Understanding Output Tutorial](02-understanding-output.md)
- **Automate analysis**: See [CLI Reference](../reference/cli.md)
- **Contribute**: See [First Contribution Tutorial](03-first-contribution.md)

## Summary

Interactive mode provides a powerful way to explore NHL Scrabble data:

✅ Fast ad-hoc queries
✅ No scripting required
✅ Tab completion and history
✅ Comprehensive command set
✅ Works with cached data

Start exploring:

```bash
nhl-scrabble interactive
```

Type `help` for all available commands!
