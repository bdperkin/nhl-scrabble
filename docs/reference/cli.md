# CLI Reference

Complete command-line interface reference for `nhl-scrabble`.

## Synopsis

```bash
nhl-scrabble [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option      | Description                |
| ----------- | -------------------------- |
| `--version` | Show version and exit      |
| `--help`    | Show help message and exit |

## Commands

### `analyze`

Run the NHL Scrabble score analyzer.

**Synopsis**:

```bash
nhl-scrabble analyze [OPTIONS]
```

**Description**:

Fetches current NHL roster data from the official NHL API and calculates Scrabble scores for all player names. Generates comprehensive reports showing team, division, and conference standings based on Scrabble scores.

**Options**:

| Option                   | Type   | Default | Description                                      |
| ------------------------ | ------ | ------- | ------------------------------------------------ |
| `--format FORMAT`        | choice | `text`  | Output format: `text` or `json`                  |
| `-o, --output PATH`      | path   | stdout  | Output file path (writes to stdout if not given) |
| `-v, --verbose`          | flag   | false   | Enable verbose logging (DEBUG level)             |
| `--no-cache`             | flag   | false   | Disable API response caching                     |
| `--clear-cache`          | flag   | false   | Clear API cache before running                   |
| `--top-players INT`      | int    | 20      | Number of top players to show in rankings        |
| `--top-team-players INT` | int    | 5       | Number of top players per team to show           |
| `--help`                 | flag   | false   | Show command help and exit                       |

**Examples**:

```bash
# Basic usage (output to stdout)
nhl-scrabble analyze

# Save to file
nhl-scrabble analyze --output report.txt

# JSON format
nhl-scrabble analyze --format json --output report.json

# Verbose logging
nhl-scrabble analyze --verbose

# Show more players
nhl-scrabble analyze --top-players 50 --top-team-players 10

# Fresh data (bypass cache)
nhl-scrabble analyze --no-cache

# Clear cache and run
nhl-scrabble analyze --clear-cache

# Combine options
nhl-scrabble analyze --format json --output report.json --verbose --top-players 100
```

**Output**:

The command generates a comprehensive report with the following sections:

1. **Header** - Tool name and version
1. **Conference Standings** - Eastern and Western conference rankings
1. **Division Standings** - All 4 divisions with team rankings
1. **Mock Playoff Bracket** - Simulated playoff seeding
1. **Team Details** - Individual team breakdowns with top players
1. **Top Players** - League-wide player rankings
1. **Statistical Summary** - League statistics and distributions

See [Understanding Output Tutorial](../tutorials/02-understanding-output.md) for details.

**Performance**:

- **Fetch time**: ~5-15 seconds (depends on network and NHL API)
- **Processing time**: \<1 second
- **Total runtime**: ~6-16 seconds typically

With caching enabled (default), subsequent runs complete in \<2 seconds.

**Error Handling**:

The command validates output paths before fetching data. Common errors:

| Error                                    | Cause                                      | Solution                |
| ---------------------------------------- | ------------------------------------------ | ----------------------- |
| "Output directory does not exist"        | Parent directory of --output doesn't exist | Create directory first  |
| "Output directory is not writable"       | No write permission to directory           | Check permissions       |
| "Output file exists but is not writable" | Existing file is read-only                 | Change file permissions |
| "NHL API Error"                          | Network or API issue                       | Check connection, retry |

### `search`

Search for NHL players by name with advanced filtering.

**Synopsis**:

```bash
nhl-scrabble search [QUERY] [OPTIONS]
```

**Description**:

Search the NHL player database by name with support for exact matching, fuzzy matching, and wildcard patterns. Filter results by Scrabble score, team, division, or conference.

**Arguments**:

| Argument | Type   | Required | Description                              |
| -------- | ------ | -------- | ---------------------------------------- |
| `QUERY`  | string | no       | Search query (name or pattern to search) |

**Options**:

| Option                  | Type   | Default | Description                                      |
| ----------------------- | ------ | ------- | ------------------------------------------------ |
| `-f, --fuzzy`           | flag   | false   | Enable fuzzy matching for typo tolerance         |
| `--min-score INT`       | int    | none    | Filter players with score >= INT                 |
| `--max-score INT`       | int    | none    | Filter players with score \<= INT                |
| `-t, --team CODE`       | string | none    | Filter by team abbreviation (e.g., TOR, EDM)     |
| `-d, --division NAME`   | string | none    | Filter by division name                          |
| `-c, --conference NAME` | string | none    | Filter by conference name (Eastern/Western)      |
| `-n, --limit INT`       | int    | 20      | Maximum number of results to show                |
| `-v, --verbose`         | flag   | false   | Enable verbose logging (DEBUG level)             |
| `-q, --quiet`           | flag   | false   | Suppress progress bars                           |
| `--format FORMAT`       | choice | `text`  | Output format: `text` or `json`                  |
| `-o, --output PATH`     | path   | stdout  | Output file path (writes to stdout if not given) |
| `--help`                | flag   | false   | Show command help and exit                       |

**Examples**:

```bash
# Exact search
nhl-scrabble search "Connor McDavid"

# Fuzzy search (tolerates typos)
nhl-scrabble search McDavd --fuzzy

# Wildcard search
nhl-scrabble search "Connor*"

# Find high-scoring players
nhl-scrabble search --min-score 50

# Find players on a team
nhl-scrabble search --team TOR

# Combine filters
nhl-scrabble search "Connor*" --team EDM --min-score 30

# Show more results
nhl-scrabble search McDavid --fuzzy --limit 50

# JSON output
nhl-scrabble search --min-score 60 --format json --output high-scorers.json

# Division search
nhl-scrabble search --division Pacific --min-score 35

# Conference search
nhl-scrabble search --conference Eastern --limit 100
```

**Search Modes**:

1. **Exact Search** (default): Case-insensitive substring matching

   ```bash
   nhl-scrabble search "McDavid"  # Finds "Connor McDavid"
   ```

1. **Fuzzy Search**: Uses similarity matching to handle typos

   ```bash
   nhl-scrabble search "McDavd" --fuzzy  # Still finds "McDavid"
   ```

1. **Wildcard Search**: Supports `*` (any chars) and `?` (single char)

   ```bash
   nhl-scrabble search "Connor*"    # Finds all "Connor ..."
   nhl-scrabble search "?lex*"      # Finds "Alex ..."
   ```

**Output**:

Text format shows:

- Search parameters used
- Number of results found
- Player details: name, score, team, division
- Score breakdown (first name + last name)

JSON format includes:

- Query information
- Result count
- Database statistics
- Full player data as array

**Performance**:

- **First search**: ~5-15 seconds (fetches all player data)
- **Subsequent searches**: \<2 seconds (uses cached data)
- **Search time**: \<0.1 seconds (instant once data is loaded)

**Filtering**:

Filters can be combined and are applied in order:

1. Team filter
1. Division filter
1. Conference filter
1. Score range filters
1. Name search
1. Result limit

**Error Handling**:

| Error               | Cause                     | Solution         |
| ------------------- | ------------------------- | ---------------- |
| "NHL API Error"     | Network or API issue      | Check connection |
| "No players found"  | No matches for criteria   | Broaden search   |
| "Invalid team code" | Unknown team abbreviation | Use valid code   |

### Future Commands (Planned)

**`nhl-scrabble compare`** (Planned)

Compare teams or players:

```bash
nhl-scrabble compare TOR BOS              # Compare two teams
nhl-scrabble compare --player "Ovechkin"  # Show player history
```

**`nhl-scrabble history`** (Planned)

Show historical trends:

```bash
nhl-scrabble history --team TOR           # Team score over time
nhl-scrabble history --league             # League-wide trends
```

**`nhl-scrabble export`** (Planned)

Export in various formats:

```bash
nhl-scrabble export --format csv         # CSV export
nhl-scrabble export --format html        # HTML report
```

## Exit Codes

| Code | Meaning                        |
| ---- | ------------------------------ |
| 0    | Success                        |
| 1    | General error (unspecified)    |
| 2    | Invalid command-line arguments |

## Environment Variables

The CLI respects these environment variables (in addition to those in [Environment Variables Reference](environment-variables.md)):

| Variable                        | Description               | Default |
| ------------------------------- | ------------------------- | ------- |
| `NHL_SCRABBLE_OUTPUT_FORMAT`    | Default output format     | `text`  |
| `NHL_SCRABBLE_VERBOSE`          | Enable verbose logging    | `false` |
| `NHL_SCRABBLE_TOP_PLAYERS`      | Default top players count | `20`    |
| `NHL_SCRABBLE_TOP_TEAM_PLAYERS` | Default top team players  | `5`     |
| `NHL_SCRABBLE_CACHE_ENABLED`    | Enable API caching        | `true`  |

**Priority**: Command-line options override environment variables.

**Example**:

```bash
# Set defaults via environment
export NHL_SCRABBLE_OUTPUT_FORMAT=json
export NHL_SCRABBLE_VERBOSE=true

# Now these use the environment defaults
nhl-scrabble analyze                    # JSON format, verbose
nhl-scrabble analyze --format text      # Override to text
```

## Configuration Files

**Not yet supported**. Configuration is via environment variables and command-line options only.

**Planned**: Support for `~/.nhl-scrabble/config.toml`:

```toml
[output]
format = "json"
top_players = 50

[api]
timeout = 30
retries = 5
```

## Shell Completion

**Not yet implemented**. Planned support for:

- Bash
- Zsh
- Fish
- PowerShell

## Programmatic Usage

Instead of CLI, use NHL Scrabble as a Python library:

```python
from nhl_scrabble.cli import run_analysis
from nhl_scrabble.config import Config

config = Config(output_format="json", verbose=True, top_players_count=50)

result = run_analysis(config)
print(result)
```

See [Python API Reference](code-api.md) for details.

## Logging

Control logging verbosity:

```bash
# Standard output (INFO level)
nhl-scrabble analyze

# Verbose output (DEBUG level)
nhl-scrabble analyze --verbose

# Quiet output (WARNING level) - not yet implemented
nhl-scrabble analyze --quiet
```

**Log format**:

```
2026-04-16 19:00:00 - nhl_scrabble.api.nhl_client - INFO - Fetching standings...
2026-04-16 19:00:01 - nhl_scrabble.api.nhl_client - DEBUG - GET https://api-web.nhle.com/v1/standings/now
2026-04-16 19:00:02 - nhl_scrabble.api.nhl_client - INFO - Successfully fetched 32 teams
```

**Log locations**:

- **stdout**: Standard and verbose logging
- **stderr**: Error messages
- **Files**: Not supported (use shell redirection if needed)

## Examples by Use Case

### Basic Analysis

```bash
# Run and view in terminal
nhl-scrabble analyze

# Save to file for later
nhl-scrabble analyze -o report.txt

# View saved report
cat report.txt
```

### Data Export

```bash
# Export as JSON
nhl-scrabble analyze --format json -o data.json

# Import to spreadsheet
python -m json.tool data.json > formatted.json
# Open in Excel/Sheets

# Query with jq
cat data.json | jq '.teams.TOR.total'
```

### Development & Debugging

```bash
# Verbose output
nhl-scrabble analyze --verbose

# Fresh data (no cache)
nhl-scrabble analyze --no-cache --verbose

# Clear cache
nhl-scrabble analyze --clear-cache
```

### Custom Reports

```bash
# Show top 100 players
nhl-scrabble analyze --top-players 100

# Show top 10 players per team
nhl-scrabble analyze --top-team-players 10

# Combine both
nhl-scrabble analyze --top-players 100 --top-team-players 10 -o full-report.txt
```

## Related

- [Configuration Reference](configuration.md) - All configuration options
- [Environment Variables](environment-variables.md) - Environment variable reference
- [Getting Started Tutorial](../tutorials/01-getting-started.md) - Introduction to CLI
- [How to Customize Output](../how-to/customize-output-format.md) - Output customization guide
