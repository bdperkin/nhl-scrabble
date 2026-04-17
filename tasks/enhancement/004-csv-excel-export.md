# Add CSV and Excel Export

**GitHub Issue**: #144 - https://github.com/bdperkin/nhl-scrabble/issues/144

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Add support for exporting reports to CSV and Excel formats for data analysis in spreadsheet applications.

Currently only supports text and JSON output. Users cannot easily:

- Import data into Excel/Google Sheets
- Perform custom analysis
- Create charts and visualizations
- Share data in business-friendly formats

## Proposed Solution

### 1. CSV Export

```python
import csv
from pathlib import Path

class CSVExporter:
    def export_team_scores(self, teams: list[TeamScore], output: Path):
        with output.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Team", "Total Score", "Player Count", "Average Score"])

            for team in teams:
                writer.writerow([
                    team.abbrev,
                    team.total_score,
                    len(team.players),
                    team.average_score,
                ])
```

### 2. Excel Export

```python
from openpyxl import Workbook

class ExcelExporter:
    def export_full_report(self, data, output: Path):
        wb = Workbook()

        # Team scores sheet
        ws_teams = wb.active
        ws_teams.title = "Teams"
        ws_teams.append(["Team", "Total Score", "Average"])

        for team in data.teams:
            ws_teams.append([team.abbrev, team.total_score, team.average_score])

        # Players sheet
        ws_players = wb.create_sheet("Players")
        ws_players.append(["Name", "Team", "Score"])

        for team in data.teams:
            for player in team.players:
                ws_players.append([player.name, team.abbrev, player.score])

        wb.save(output)
```

### 3. CLI Integration

```bash
# CSV export
nhl-scrabble analyze --format csv --output report.csv

# Excel export
nhl-scrabble analyze --format excel --output report.xlsx

# Multiple sheets in Excel
nhl-scrabble analyze --format excel --sheets teams,players,divisions --output full_report.xlsx
```

## Implementation Steps

1. Add `openpyxl` dependency
1. Create CSV exporter class
1. Create Excel exporter class
1. Add format options to CLI
1. Add tests for exports
1. Update documentation

## Acceptance Criteria

- [ ] CSV export implemented
- [ ] Excel export implemented
- [ ] CLI options added
- [ ] Multiple Excel sheets supported
- [ ] Tests verify export formats
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/exporters/csv_exporter.py` - New module
- `src/nhl_scrabble/exporters/excel_exporter.py` - New module
- `src/nhl_scrabble/cli.py` - Add format options
- `pyproject.toml` - Add openpyxl dependency

## Dependencies

- `openpyxl` - Excel file creation (new dependency)

## Additional Notes

**Benefits**:

- Business-friendly output
- Easy data analysis
- Chart creation
- Data sharing

## Implementation Notes

*To be filled during implementation*
