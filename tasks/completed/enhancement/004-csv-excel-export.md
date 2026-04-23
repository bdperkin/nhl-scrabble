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
                writer.writerow(
                    [
                        team.abbrev,
                        team.total_score,
                        len(team.players),
                        team.average_score,
                    ]
                )
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

- [x] CSV export implemented
- [x] Excel export implemented
- [x] CLI options added
- [x] Multiple Excel sheets supported
- [x] Tests verify export formats
- [x] Documentation updated

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

**Implemented**: 2026-04-18
**Branch**: enhancement/004-csv-excel-export
**PR**: #203 - https://github.com/bdperkin/nhl-scrabble/pull/203
**Commits**: 1 commit (a356084)
**Merged**: 2026-04-18

### Actual Implementation

Successfully implemented CSV and Excel export formats with comprehensive functionality:

**CSV Exporter** (`src/nhl_scrabble/exporters/csv_exporter.py`):

- `CSVExporter` class with 5 export methods
- Exports for teams, players, divisions, conferences, and playoffs
- UTF-8 encoding support for international player names
- Automatic sorting by total score descending
- Simple, spreadsheet-friendly format
- 100% test coverage

**Excel Exporter** (`src/nhl_scrabble/exporters/excel_exporter.py`):

- `ExcelExporter` class with multi-sheet support
- Professional formatting with styled headers (#366092 blue background)
- Auto-adjusted column widths for readability
- Support for 5 sheets: Teams, Players, Divisions, Conferences, Playoffs
- Customizable sheet selection via `--sheets` CLI option
- Graceful ImportError handling when openpyxl not installed
- 94.67% test coverage

**CLI Integration** (`src/nhl_scrabble/cli.py`):

- Added `csv` and `excel` to `--format` option choices
- Added `--sheets` option for Excel sheet customization
- Validation requiring `--output` for CSV/Excel formats
- Proper error messages with usage examples
- Updated help text and documentation

**Dependencies**:

- Added `openpyxl>=3.1.0` in `[export]` optional dependency group
- Added to `dev` group for comprehensive development environment
- Updated `uv.lock` with new dependencies (et-xmlfile, openpyxl)

**Quality Assurance**:

- Created `.vulture_allowlist` for public API methods
- Updated `.pre-commit-config.yaml` to use vulture allowlist
- All 18 new tests passing
- All CI checks passing (except experimental Python 3.15-dev)
- Type hints throughout (mypy strict mode passing)
- Docstrings for all public methods (interrogate passing)

### Challenges Encountered

**1. Model Structure Discovery**:

- Needed to understand `PlayoffTeam`, `DivisionStandings`, and `ConferenceStandings` structures
- Solution: Read model files and adapted tests to match actual data structures

**2. Vulture False Positives**:

- Public API methods flagged as unused since they're not called in tests
- Solution: Created `.vulture_allowlist` with documented exceptions
- Updated pre-commit hook to use allowlist

**3. Type Checking Complexity**:

- Path imports triggered TC003 rule (move to TYPE_CHECKING block)
- Solution: Used `# noqa: TC003` for runtime Path usage (needed for file operations)

**4. Excel Complexity Warning**:

- `export_full_report` method flagged for complexity (14 branches)
- Solution: Added `# noqa: C901, PLR0912` - method is inherently complex but well-structured

### Deviations from Plan

**Minor adjustments**:

- CSV export simplified to focus on team scores (as primary use case)
- Other export methods (players, divisions, etc.) available but not exposed in CLI by default
- Excel is the recommended format for comprehensive multi-sheet reports

**Additional features**:

- Added validation requiring `--output` for CSV/Excel (prevents confusion)
- Professional Excel formatting exceeds original specification
- Vulture allowlist system for better dead code detection

### Actual vs Estimated Effort

- **Estimated**: 3-4h
- **Actual**: ~3.5h
- **Breakdown**:
  - Implementation: 1.5h (CSV + Excel exporters, CLI integration)
  - Testing: 1h (18 comprehensive tests)
  - Quality fixes: 0.5h (vulture allowlist, type hints, mypy)
  - Documentation: 0.5h (CHANGELOG, docstrings, CLI help)

### Related PRs

- #203 - CSV and Excel export implementation (merged)

### Lessons Learned

**Best Practices Confirmed**:

1. Comprehensive testing catches integration issues early
1. Type hints throughout code improves maintainability
1. Vulture allowlist better than noqa comments for public APIs
1. Professional formatting in Excel exports adds significant value
1. Clear error messages with examples improve UX

**Technical Insights**:

1. openpyxl provides excellent Excel formatting capabilities
1. CSV module handles UTF-8 encoding seamlessly
1. Path type checking requires runtime availability (can't use TYPE_CHECKING)
1. Multi-sheet Excel exports are more valuable than multiple CSV files

**Process Improvements**:

1. Test data model structures before writing tests
1. Pre-commit hooks should test on all files before committing new hooks
1. Vulture allowlists scale better than per-line noqa comments
1. Public API methods need allowlisting even if tested (vulture sees tests as separate)

### Usage Examples

```bash
# CSV export (team scores)
nhl-scrabble analyze --format csv --output report.csv

# Excel export (all 5 sheets)
nhl-scrabble analyze --format excel --output full_report.xlsx

# Excel export (selected sheets)
nhl-scrabble analyze --format excel --sheets teams,players --output teams_players.xlsx

# Excel export (playoffs only)
nhl-scrabble analyze --format excel --sheets playoffs --output playoffs.xlsx

# Invalid usage (caught with helpful error)
nhl-scrabble analyze --format csv
# Error: CSV format requires --output option
# Example: nhl-scrabble analyze --format csv --output report.csv
```

### Test Coverage

**CSV Exporter**: 100% coverage

- Team scores export (dict and list input)
- Player scores export with sorting
- Division standings export
- Conference standings export
- Playoff standings export
- UTF-8 encoding support
- Proper sorting verification

**Excel Exporter**: 94.67% coverage

- Team scores export with formatting
- Player scores export
- Full report with all sheets
- Selective sheet export
- Header formatting
- Column auto-sizing
- UTF-8 encoding support
- Sorting verification

**Uncovered lines**: Only `ImportError` fallback path and optional formatting attributes

### Future Enhancements

Potential improvements for future iterations:

1. Add CSV export for all data types (players, divisions, etc.) to CLI
1. Support for custom Excel themes/colors
1. Chart generation in Excel sheets
1. Pandas DataFrame export option
1. Google Sheets API integration
1. Configurable number formats in Excel
