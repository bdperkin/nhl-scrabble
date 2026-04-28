# How to Export to JSON

Export NHL Scrabble data in JSON format for programmatic use.

## Problem

You want to use NHL Scrabble data in other applications, spreadsheets, or scripts.

## Solution

### Basic JSON export

```bash
nhl-scrabble analyze --format json --output report.json
```

### JSON structure

```json
{
  "teams": {
    "TOR": {
      "total": 2234,
      "players": [...],
      "division": "Atlantic",
      "conference": "Eastern",
      "avg_per_player": 93.1
    }
  },
  "divisions": {...},
  "conferences": {...},
  "playoffs": {...},
  "summary": {
    "total_teams": 32,
    "total_players": 768
  }
}
```

### Use with Python

```python
import json

with open("report.json") as f:
    data = json.load(f)

# Access team data
toronto = data["teams"]["TOR"]
print(f"Toronto total: {toronto['total']}")

# Find highest scoring player
all_players = []
for team in data["teams"].values():
    all_players.extend(team["players"])

top_player = max(all_players, key=lambda p: p["score"])
print(f"Top player: {top_player['firstName']} {top_player['lastName']}")
```

### Use with jq (command-line)

```bash
# Pretty print
cat report.json | jq '.'

# Get specific team score
cat report.json | jq '.teams.TOR.total'

# List all team totals
cat report.json | jq '.teams | to_entries | .[] | {team: .key, total: .value.total}'

# Top 5 teams
cat report.json | jq '.teams | to_entries | sort_by(.value.total) | reverse | .[0:5]'
```

### Import to Excel/Google Sheets

1. Export JSON: `nhl-scrabble analyze --format json --output data.json`
1. Open Excel/Sheets
1. Use "Import from JSON" feature
1. Select fields to import
1. Create pivot tables and charts

## Related

- [JSON Schema Reference](../reference/json-schema.md) - Complete JSON structure
- [CLI Reference](../reference/cli.md) - CLI options
- Python API - Use programmatically
