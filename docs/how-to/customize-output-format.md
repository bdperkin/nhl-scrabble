# How to Customize Output Format

Control NHL Scrabble report formatting and content.

## Problem

You want to customize what appears in reports.

## Solutions

### Change number of players shown

```bash
# Show top 50 players (default: 20)
nhl-scrabble analyze --top-players 50

# Show top 10 players per team (default: 5)
nhl-scrabble analyze --top-team-players 10

# Combine both
nhl-scrabble analyze --top-players 100 --top-team-players 15
```

### Change output format

```bash
# Text format (default)
nhl-scrabble analyze --format text

# JSON format
nhl-scrabble analyze --format json

# HTML format (future)
# nhl-scrabble analyze --format html
```

### Save to file

```bash
# Save to specific file
nhl-scrabble analyze --output report.txt

# Save with timestamp
nhl-scrabble analyze --output "report-$(date +%Y%m%d).txt"

# Save to directory
mkdir -p reports
nhl-scrabble analyze --output reports/latest.txt
```

### Verbose output

```bash
# Enable debug logging
nhl-scrabble analyze --verbose
```

## Environment variables

Set defaults:

```bash
export NHL_SCRABBLE_OUTPUT_FORMAT=json
export NHL_SCRABBLE_TOP_PLAYERS=50
export NHL_SCRABBLE_TOP_TEAM_PLAYERS=10
```

## Related

- [CLI Reference](../reference/cli.md) - All CLI options
- [Configuration Reference](../reference/configuration.md) - All settings
