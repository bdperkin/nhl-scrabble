# Consolidate Exporters and Formatters Architecture

**GitHub Issue**: TBD (create issue)

## Priority

**LOW** - Nice to Have (Future Enhancement)

Architectural cleanup to simplify the codebase and reduce duplication between exporters and formatters.

## Estimated Effort

3-5 hours

## Description

Consolidate the confusing dual architecture of exporters and formatters by deprecating redundant CSV exporter functionality. Currently the project has both `formatters/` (return strings) and `exporters/` (write to files), which creates confusion and duplication for CSV output.

**Problem**: CSVExporter provides file-writing methods that duplicate CSVFormatter functionality, while ExcelExporter provides legitimate multi-sheet workbook functionality that formatters cannot easily replicate.

**Goal**: Establish clear, consistent pattern where formatters handle all string-based outputs and only complex binary formats (Excel) need dedicated exporters.

## Current State

### Formatters (`src/nhl_scrabble/formatters/`)

**Pattern**: Return formatted strings via factory pattern

```python
from nhl_scrabble.formatters import get_formatter

formatter = get_formatter('csv')  # or 'json', 'html', etc.
output = formatter.format(data)
```

**All formatters**:

- `CSVFormatter` - Returns CSV string
- `HTMLFormatter` - Returns HTML string
- `JSONFormatter` - Returns JSON string
- `YAMLFormatter` - Returns YAML string
- `XMLFormatter` - Returns XML string
- `MarkdownFormatter` - Returns Markdown string
- `TableFormatter` - Returns table string
- `TextFormatter` - Returns text report
- `TemplateFormatter` - Returns custom template output

**Usage**: CLI `--format` option for stdout or file writing

### Exporters (`src/nhl_scrabble/exporters/`)

**Pattern**: Write directly to files (take `Path` parameter)

#### CSVExporter (`csv_exporter.py`) - **REDUNDANT** ⚠️

```python
from nhl_scrabble.exporters.csv_exporter import CSVExporter

exporter = CSVExporter()
exporter.export_team_scores(teams, Path("teams.csv"))
exporter.export_player_scores(players, Path("players.csv"))
exporter.export_division_standings(divisions, Path("divisions.csv"))
exporter.export_conference_standings(conferences, Path("conferences.csv"))
exporter.export_playoff_standings(playoffs, Path("playoffs.csv"))
```

**Issues**:

- ❌ **Not used in production code** - Only tested, never used in CLI or library
- ❌ **Duplicates CSVFormatter** - Same CSV generation, just writes to file
- ❌ **In vulture allowlist** - All 5 methods marked as "public API" to suppress dead code warnings
- ❌ **Creates confusion** - Users don't know whether to use formatter or exporter

#### ExcelExporter (`excel_exporter.py`) - **LEGITIMATE** ✅

```python
from nhl_scrabble.exporters.excel_exporter import ExcelExporter

exporter = ExcelExporter()
exporter.export_full_report(
    team_scores=teams,
    all_players=players,
    division_standings=divisions,
    conference_standings=conferences,
    playoff_standings=playoffs,
    output=Path("report.xlsx"),
    sheets=["teams", "players", "divisions"]  # Multi-sheet workbook
)
```

**Why keep**:

- ✅ **Actually used** - Used in `cli.py` for `--format excel`
- ✅ **Complex functionality** - Multi-sheet workbooks with formatting
- ✅ **Binary format** - openpyxl requires file-based operations
- ✅ **Rich features** - Cell formatting, column widths, styling
- ✅ **Cannot easily return as string** - XLSX is binary format

### Architecture Comparison

| Feature                  | CSVFormatter  | CSVExporter            | ExcelExporter          |
| ------------------------ | ------------- | ---------------------- | ---------------------- |
| **Output**               | String        | File                   | File (binary)          |
| **Used in CLI**          | ✅ Yes        | ❌ No                  | ✅ Yes                 |
| **Used in tests**        | ✅ Yes        | ✅ Yes                 | ✅ Yes                 |
| **In allowlist**         | ❌ No         | ✅ Yes (all 5 methods) | ✅ Yes (1 method)      |
| **Duplicates formatter** | N/A           | ✅ Yes                 | ❌ No                  |
| **Justification**        | Clean pattern | None                   | Multi-sheet complexity |

### CLI Usage

**Current (confusing)**:

```bash
# CSV via formatter (what users actually use)
nhl-scrabble analyze --format csv --output report.csv

# CSV via exporter (not exposed, only in code)
# Not available via CLI!

# Excel via exporter (legitimate)
nhl-scrabble analyze --format excel --output report.xlsx
```

**Problem**: Users might find CSVExporter in docs/code and wonder why it exists separately from CSVFormatter.

## Proposed Solution

### Phase 1: Deprecate CSVExporter

**Mark as deprecated** (with deprecation warnings):

```python
# src/nhl_scrabble/exporters/csv_exporter.py

import warnings
from pathlib import Path
from typing import Any

from nhl_scrabble.formatters import get_formatter
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


class CSVExporter:
    """CSV export functionality (DEPRECATED).

    .. deprecated:: 2.1.0
        Use :class:`~nhl_scrabble.formatters.csv_formatter.CSVFormatter` instead.
        CSVExporter will be removed in version 3.0.0.

    This class is deprecated. Use the formatter pattern instead:

    .. code-block:: python

        from nhl_scrabble.formatters import get_formatter

        formatter = get_formatter('csv')
        csv_string = formatter.format(data)
        Path("output.csv").write_text(csv_string)

    Examples:
        >>> # OLD (deprecated):
        >>> exporter = CSVExporter()
        >>> exporter.export_team_scores(teams, Path("teams.csv"))

        >>> # NEW (recommended):
        >>> from nhl_scrabble.formatters import get_formatter
        >>> formatter = get_formatter('csv')
        >>> Path("teams.csv").write_text(formatter.format(data))
    """

    def __init__(self) -> None:
        """Initialize CSV exporter with deprecation warning."""
        warnings.warn(
            "CSVExporter is deprecated and will be removed in version 3.0.0. "
            "Use nhl_scrabble.formatters.get_formatter('csv') instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def export_team_scores(
        self, teams: dict[str, TeamScore] | list[TeamScore], output: Path
    ) -> None:
        """Export team scores to CSV file (DEPRECATED).

        .. deprecated:: 2.1.0
            Use :func:`~nhl_scrabble.formatters.get_formatter` with 'csv' format.

        Args:
            teams: Dictionary or list of TeamScore objects
            output: Output file path
        """
        warnings.warn(
            "CSVExporter.export_team_scores() is deprecated. "
            "Use get_formatter('csv').format(data) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Delegate to formatter (backward compatibility implementation)
        from nhl_scrabble.formatters import get_formatter

        # Convert teams to formatter data structure
        team_list = list(teams.values()) if isinstance(teams, dict) else teams
        data = {
            "teams": {
                team.abbrev: {
                    "total": team.total,
                    "division": team.division,
                    "conference": team.conference,
                    "avg_per_player": team.avg_per_player,
                    "players": [],
                }
                for team in team_list
            },
            "summary": {},
        }

        formatter = get_formatter('csv')
        output.write_text(formatter.format(data))

    # Similar deprecation for other methods...
```

### Phase 2: Update Documentation

**Update all references**:

1. **README.md** - Remove CSVExporter examples, show formatter pattern
1. **CHANGELOG.md** - Document deprecation in v2.1.0 release notes
1. **API docs** - Add deprecation notices
1. **How-to guides** - Update CSV export examples
1. **Migration guide** - Create guide for CSVExporter → CSVFormatter

**Example migration guide** (`docs/how-to/migrate-csv-exporter.md`):

````markdown
# Migrating from CSVExporter to CSVFormatter

## Overview

`CSVExporter` is deprecated in v2.1.0 and will be removed in v3.0.0.
Use `CSVFormatter` via the formatter factory pattern instead.

## Migration Examples

### Export Team Scores

**Before (deprecated)**:
```python
from nhl_scrabble.exporters.csv_exporter import CSVExporter
from pathlib import Path

exporter = CSVExporter()
exporter.export_team_scores(teams, Path("teams.csv"))
````

**After (recommended)**:

```python
from nhl_scrabble.formatters import get_formatter
from pathlib import Path

# Prepare data
data = {
    "teams": {
        team.abbrev: {
            "total": team.total,
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for team in teams.values()
    },
    "summary": {"total_teams": len(teams)},
}

# Format and write
formatter = get_formatter('csv')
Path("teams.csv").write_text(formatter.format(data))
```

### Export Player Scores

**Before**:

```python
exporter.export_player_scores(players, Path("players.csv"))
```

**After**:

```python
# Player export requires custom CSV generation
# Use CSVFormatter for team standings or write custom CSV
import csv
from pathlib import Path

with Path("players.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Player", "Team", "Score"])
    for player in sorted(players, key=lambda p: p.full_score, reverse=True):
        writer.writerow([player.full_name, player.team, player.full_score])
```

## Why This Change?

1. **Simpler architecture** - One pattern for all string-based formats
1. **Consistent interface** - All formatters work the same way
1. **Flexibility** - Formatters return strings you can use anywhere
1. **Less duplication** - No need to maintain parallel implementations

````

### Phase 3: Extend CSVFormatter (Optional)

**If needed**, enhance CSVFormatter to support specialized exports:

```python
# src/nhl_scrabble/formatters/csv_formatter.py

class CSVFormatter:
    """Format analysis data as CSV."""

    def __init__(self, export_type: str = "teams") -> None:
        """Initialize CSV formatter.

        Args:
            export_type: Type of export - "teams", "players", "divisions",
                        "conferences", or "playoffs"
        """
        self.export_type = export_type

    def format(self, data: dict[str, Any]) -> str:
        """Format data to CSV string.

        Generates different CSV structure based on export_type.
        """
        if self.export_type == "teams":
            return self._format_teams(data)
        elif self.export_type == "players":
            return self._format_players(data)
        # ... etc
````

**Usage**:

```python
# Teams CSV (default)
formatter = get_formatter('csv')
teams_csv = formatter.format(data)

# Players CSV
formatter = get_formatter('csv', export_type='players')
players_csv = formatter.format(data)
```

### Phase 4: Remove CSVExporter (v3.0.0)

**After deprecation period** (at least one minor version):

1. Delete `src/nhl_scrabble/exporters/csv_exporter.py`
1. Remove CSVExporter entries from `.vulture_allowlist`
1. Delete `tests/unit/test_csv_exporter.py`
1. Update CHANGELOG.md with removal notice
1. Remove migration guide (archive in historical docs)

**Keep**:

- ✅ `src/nhl_scrabble/exporters/excel_exporter.py` - Legitimate use case
- ✅ `src/nhl_scrabble/exporters/__init__.py` - For ExcelExporter
- ✅ `tests/unit/test_excel_exporter.py` - Still needed

## Implementation Steps

### Step 1: Add Deprecation Warnings

```bash
# Add deprecation warnings to all CSVExporter methods
# Update docstrings with deprecation notices
# Add DeprecationWarning to __init__ and all methods
```

### Step 2: Update Tests

```python
# tests/unit/test_csv_exporter.py

import warnings
import pytest

def test_csv_exporter_deprecated():
    """Test that CSVExporter raises deprecation warning."""
    with pytest.warns(DeprecationWarning, match="CSVExporter is deprecated"):
        from nhl_scrabble.exporters.csv_exporter import CSVExporter
        exporter = CSVExporter()

def test_export_team_scores_deprecated():
    """Test that export_team_scores raises deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_team_scores(teams, output)

        assert len(w) >= 2  # __init__ + method deprecation
        assert "deprecated" in str(w[-1].message).lower()
```

### Step 3: Create Migration Guide

```bash
# Create docs/how-to/migrate-csv-exporter.md
# Add to docs index and navigation
```

### Step 4: Update Documentation

```bash
# Update README.md
# Update CHANGELOG.md (v2.1.0 release notes)
# Update API documentation
# Update any tutorials/guides that use CSVExporter
```

### Step 5: Update Vulture Allowlist

Add deprecation comment:

```diff
 # CSV Exporter public API
+# DEPRECATED in v2.1.0 - Will be removed in v3.0.0
 export_team_scores  # CSVExporter method for exporting team scores
 export_player_scores  # CSVExporter method for exporting player scores
 export_division_standings  # CSVExporter method for exporting division standings
 export_conference_standings  # CSVExporter method for exporting conference standings
 export_playoff_standings  # CSVExporter method for exporting playoff standings
```

### Step 6: Version Bump

```bash
# Bump version to 2.1.0 in pyproject.toml
# Update __version__ in __init__.py
# Create git tag for v2.1.0
```

## Testing Strategy

### Deprecation Warning Tests

```python
# Test deprecation warnings are raised
def test_csv_exporter_deprecation_warnings():
    """Verify all CSVExporter methods raise DeprecationWarning."""
    with pytest.warns(DeprecationWarning):
        exporter = CSVExporter()

    with pytest.warns(DeprecationWarning):
        exporter.export_team_scores(teams, output)

    # Test all 5 methods...
```

### Backward Compatibility Tests

```python
# Test deprecated functionality still works
def test_csv_exporter_still_works():
    """Verify CSVExporter still produces correct output (deprecated)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        exporter = CSVExporter()
        exporter.export_team_scores(teams, output)

        # Verify output matches formatter output
        formatter_output = get_formatter('csv').format(data)
        assert output.read_text() == formatter_output
```

### Formatter Tests

```python
# Ensure CSVFormatter handles all use cases
def test_csv_formatter_all_data_types():
    """Test CSVFormatter handles teams, players, divisions, etc."""
    formatter = get_formatter('csv')

    # Test with team data
    team_csv = formatter.format(team_data)
    assert "Rank,Team" in team_csv

    # Test with full data
    full_csv = formatter.format(full_data)
    assert len(full_csv.split('\n')) > 1
```

## Acceptance Criteria

### Deprecation (v2.1.0)

- [ ] All CSVExporter methods raise DeprecationWarning
- [ ] Deprecation warnings include clear migration instructions
- [ ] CSVExporter still works (backward compatibility maintained)
- [ ] Docstrings updated with deprecation notices
- [ ] Migration guide created in docs/how-to/
- [ ] CHANGELOG.md documents deprecation
- [ ] README.md updated to show formatter pattern
- [ ] All tests pass with deprecation warnings
- [ ] Vulture allowlist updated with deprecation comments

### Documentation

- [ ] Migration guide complete with examples
- [ ] API docs show deprecation notices
- [ ] All tutorials updated to use formatter pattern
- [ ] How-to guides reference formatters, not exporters
- [ ] Clear timeline for removal (v3.0.0)

### Testing

- [ ] Deprecation warning tests added
- [ ] Backward compatibility tests pass
- [ ] CSVFormatter tests cover all use cases
- [ ] No test failures or regressions
- [ ] Test coverage maintained or improved

### Removal (v3.0.0 - Future)

- [ ] At least one minor version has passed (2.1.0 → 2.2.0 → 3.0.0)
- [ ] Delete `src/nhl_scrabble/exporters/csv_exporter.py`
- [ ] Delete `tests/unit/test_csv_exporter.py`
- [ ] Remove 5 CSVExporter entries from `.vulture_allowlist`
- [ ] Update CHANGELOG.md with removal notice
- [ ] Archive migration guide in historical docs
- [ ] ExcelExporter still works and is tested

## Related Files

- `src/nhl_scrabble/exporters/csv_exporter.py` - Deprecate this file
- `src/nhl_scrabble/exporters/excel_exporter.py` - Keep (legitimate use case)
- `src/nhl_scrabble/formatters/csv_formatter.py` - May need enhancement
- `.vulture_allowlist` - Update with deprecation comments
- `tests/unit/test_csv_exporter.py` - Add deprecation tests
- `docs/how-to/migrate-csv-exporter.md` - Create migration guide
- `README.md` - Update examples
- `CHANGELOG.md` - Document deprecation

## Dependencies

**Blocking**: None - can be done independently

**Blocked by**: Should wait until after v2.0.0 release to avoid breaking pre-release API

## Additional Notes

### Why Not Deprecate ExcelExporter?

ExcelExporter serves a legitimate purpose that formatters cannot easily replicate:

1. **Binary format** - XLSX files are binary, not text
1. **Multi-sheet workbooks** - Complex structure (teams, players, divisions, conferences, playoffs)
1. **Cell formatting** - Colors, fonts, borders, number formats
1. **Column sizing** - Auto-width, merged cells, headers
1. **openpyxl integration** - Library works with workbook objects, not strings

**CSVExporter**, by contrast:

- Returns plain text (like formatters)
- Single-sheet structure (simple)
- No special formatting needs
- Perfectly suited for formatter pattern

### Deprecation Timeline

**v2.1.0** (2026 Q2):

- Add deprecation warnings
- Create migration guide
- Update documentation

**v2.2.0** (2026 Q3):

- Maintain deprecation warnings
- Users have had 3+ months to migrate

**v3.0.0** (2027 Q1):

- Remove CSVExporter entirely
- Breaking change justified (major version)
- Users have had 6+ months notice

### Alternative: Keep Both?

**Considered but rejected**:

- ❌ Maintains confusion about which to use
- ❌ Increases maintenance burden (two implementations)
- ❌ Violates DRY principle
- ❌ Makes testing more complex
- ❌ Bloats codebase unnecessarily

**Formatter pattern is superior**:

- ✅ Returns strings (flexible - stdout, files, variables)
- ✅ Consistent interface across all formats
- ✅ Factory pattern is well-established
- ✅ Already used throughout CLI
- ✅ Easier to test (no file I/O mocking)

### Risk Assessment

**Low Risk**:

- CSVExporter not used in production CLI code
- Only appears in tests
- Deprecation period provides migration time
- Backward compatibility maintained during deprecation
- Clear migration path via formatters

**Mitigation**:

- Comprehensive deprecation warnings
- Detailed migration guide with examples
- Maintain functionality through v2.x series
- Only remove in major version (v3.0.0)

## Implementation Notes

*To be filled during implementation:*

### Actual Implementation

*What was actually done, any deviations from plan*

### Challenges Encountered

*Any unexpected issues or complications*

### Deviations from Plan

*Changes to the proposed solution and why*

### Actual vs Estimated Effort

- **Estimated**: 3-5h
- **Actual**: TBD
- **Reason**: TBD
