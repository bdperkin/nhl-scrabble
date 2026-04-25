# Migrating from CSVExporter to CSVFormatter

## Overview

`CSVExporter` is deprecated in v2.1.0 and will be removed in v3.0.0.
Use `CSVFormatter` via the formatter factory pattern instead.

## Why This Change?

The project previously had two parallel architectures for CSV output:

- **CSVFormatter** - Returns CSV strings (flexible, used in CLI)
- **CSVExporter** - Writes directly to files (redundant)

This created confusion and maintenance burden. The formatter pattern is superior because:

1. **Simpler architecture** - One pattern for all string-based formats
1. **Consistent interface** - All formatters work the same way
1. **Flexibility** - Formatters return strings you can use anywhere (stdout, files, variables, tests)
1. **Less duplication** - No need to maintain parallel implementations
1. **Easier testing** - No file I/O mocking required

**Note**: `ExcelExporter` is **NOT** deprecated because it provides legitimate multi-sheet workbook functionality that formatters cannot easily replicate (binary format, cell styling, multi-sheet structure).

## Migration Timeline

- **v2.1.0** (current) - CSVExporter deprecated with warnings
- **v2.2.0** (future) - Deprecation warnings continue
- **v3.0.0** (future) - CSVExporter removed entirely

You have at least 6 months to migrate before removal.

## Migration Examples

### Export Team Scores

**Before (deprecated)**:

```python
from nhl_scrabble.exporters.csv_exporter import CSVExporter
from pathlib import Path

exporter = CSVExporter()  # DeprecationWarning!
exporter.export_team_scores(teams, Path("teams.csv"))  # DeprecationWarning!
```

**After (recommended)**:

```python
from nhl_scrabble.formatters import get_formatter
from pathlib import Path

# Prepare data structure for formatter
data = {
    "teams": {
        team.abbrev: {
            "total": team.total,
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
            "player_count": team.player_count,
        }
        for team in teams.values()
    },
    "summary": {"total_teams": len(teams)},
}

# Format and write
formatter = get_formatter("csv")
csv_string = formatter.format(data)
Path("teams.csv").write_text(csv_string)
```

### Export Player Scores

**Before**:

```python
exporter.export_player_scores(players, Path("players.csv"))
```

**After**:

```python
import csv
from pathlib import Path

# Player export requires custom CSV generation
# Use standard library csv module for custom formats
with Path("players.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "Player Name",
            "Team",
            "Division",
            "Conference",
            "First Name Score",
            "Last Name Score",
            "Total Score",
        ]
    )

    for player in sorted(players, key=lambda p: p.full_score, reverse=True):
        writer.writerow(
            [
                player.full_name,
                player.team,
                player.division,
                player.conference,
                player.first_score,
                player.last_score,
                player.full_score,
            ]
        )
```

### Export Division Standings

**Before**:

```python
exporter.export_division_standings(divisions, Path("divisions.csv"))
```

**After**:

```python
import csv
from pathlib import Path

with Path("divisions.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["Division", "Team", "Total Score", "Player Count", "Average Score"]
    )

    for division_name in sorted(divisions.keys()):
        standing = divisions[division_name]
        for team in standing.teams:
            writer.writerow(
                [
                    division_name,
                    team.abbrev,
                    team.total,
                    team.player_count,
                    f"{team.avg_per_player:.2f}",
                ]
            )
```

### Export Conference Standings

**Before**:

```python
exporter.export_conference_standings(conferences, Path("conferences.csv"))
```

**After**:

```python
import csv
from pathlib import Path

with Path("conferences.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "Conference",
            "Team",
            "Division",
            "Total Score",
            "Player Count",
            "Average Score",
        ]
    )

    for conference_name in sorted(conferences.keys()):
        standing = conferences[conference_name]
        for team in standing.teams:
            writer.writerow(
                [
                    conference_name,
                    team.abbrev,
                    team.division,
                    team.total,
                    team.player_count,
                    f"{team.avg_per_player:.2f}",
                ]
            )
```

### Export Playoff Standings

**Before**:

```python
exporter.export_playoff_standings(playoffs, Path("playoffs.csv"))
```

**After**:

```python
import csv
from pathlib import Path

with Path("playoffs.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "Conference",
            "Seed",
            "Team",
            "Division",
            "Total Score",
            "Average Score",
            "Status",
        ]
    )

    for conference_name in sorted(playoffs.keys()):
        teams = playoffs[conference_name]
        for seed, team in enumerate(teams, start=1):
            writer.writerow(
                [
                    conference_name,
                    seed,
                    team.abbrev,
                    team.division,
                    team.total,
                    f"{team.avg:.2f}",
                    team.status_indicator,
                ]
            )
```

## Suppressing Deprecation Warnings (Temporary)

If you need to suppress deprecation warnings while you migrate (not recommended for long-term):

```python
import warnings

# Suppress only during migration period
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)

    # Your deprecated code here
    exporter = CSVExporter()
    exporter.export_team_scores(teams, output)
```

**Note**: This is a temporary workaround. You should migrate to the formatter pattern before v3.0.0.

## Alternative: Use Standard Library CSV Module

For simple CSV exports, you can use Python's built-in `csv` module directly:

```python
import csv
from pathlib import Path

# Write any data structure to CSV
with Path("output.csv").open("w", newline="") as f:
    writer = csv.writer(f)

    # Write header
    writer.writerow(["Column1", "Column2", "Column3"])

    # Write data rows
    for item in data:
        writer.writerow([item.field1, item.field2, item.field3])
```

This gives you full control over CSV structure and formatting.

## Benefits of Formatter Pattern

### Flexibility

Formatters return strings, which you can:

- Write to files: `Path("out.csv").write_text(csv_string)`
- Print to stdout: `print(csv_string)`
- Store in variables: `data = csv_string`
- Send over network: `response.body = csv_string`
- Test easily: `assert "expected" in csv_string`

### Consistency

All formatters work the same way:

```python
from nhl_scrabble.formatters import get_formatter

# All formats use same interface
json_formatter = get_formatter("json")
csv_formatter = get_formatter("csv")
html_formatter = get_formatter("html")

# All return strings
json_output = json_formatter.format(data)
csv_output = csv_formatter.format(data)
html_output = html_formatter.format(data)
```

### Testing

Formatters are easier to test (no file I/O):

```python
def test_csv_formatter():
    """Test CSV formatter output."""
    formatter = get_formatter("csv")
    output = formatter.format(data)

    # No file mocking required!
    assert "Rank,Team" in output
    assert "TOR" in output
```

## CLI Usage Unchanged

The CLI continues to work as before:

```bash
# CSV output (uses CSVFormatter internally)
nhl-scrabble analyze --format csv --output report.csv

# Excel output (uses ExcelExporter - NOT deprecated)
nhl-scrabble analyze --format excel --output report.xlsx
```

No CLI changes required - the deprecation only affects programmatic use of `CSVExporter`.

## Getting Help

If you have questions about migration:

1. Check this guide first
1. Review the [CSVFormatter documentation](../../reference/formatters.md)
1. See [formatter examples](../tutorials/output-formats.md)
1. Open an issue: https://github.com/bdperkin/nhl-scrabble/issues

## Summary

- **Use**: `CSVFormatter` via `get_formatter('csv')`
- **Don't use**: `CSVExporter` (deprecated)
- **Timeline**: Removed in v3.0.0 (6+ months notice)
- **Benefits**: Simpler, more flexible, consistent with other formatters
- **Excel**: `ExcelExporter` is NOT deprecated (legitimate use case)

Migrate now to avoid breaking changes in v3.0.0!
