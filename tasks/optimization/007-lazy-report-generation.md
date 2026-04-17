# Implement Lazy Report Generation

**GitHub Issue**: #138 - https://github.com/bdperkin/nhl-scrabble/issues/138

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Implement lazy evaluation for report generation to avoid computing reports that are never displayed or saved.

Currently, all reports are generated eagerly even if not needed:

- Stats report computed even in quiet mode
- Division reports generated when only showing top players
- Playoff bracket calculated when only viewing team standings

This wastes CPU and memory when users want specific output.

## Current State

```python
# src/nhl_scrabble/cli.py
def analyze():
    # Generate ALL reports upfront
    team_report = TeamReport(team_scores).generate()
    division_report = DivisionReport(divisions).generate()
    conference_report = ConferenceReport(conferences).generate()
    playoff_report = PlayoffReport(playoff_bracket).generate()
    stats_report = StatsReport(all_players).generate()

    # But might only use one
    if output_format == "text":
        print(team_report)  # Only this used!
```

## Proposed Solution

### 1. Lazy Report Properties

```python
class ReportGenerator:
    def __init__(self, data):
        self.data = data
        self._team_report = None
        self._division_report = None
        self._playoff_report = None

    @property
    def team_report(self) -> str:
        """Generate team report lazily."""
        if self._team_report is None:
            self._team_report = TeamReport(self.data.teams).generate()
        return self._team_report

    @property
    def playoff_report(self) -> str:
        """Generate playoff report lazily."""
        if self._playoff_report is None:
            self._playoff_report = PlayoffReport(
                self.data.playoff_bracket
            ).generate()
        return self._playoff_report
```

### 2. Generator-Based Reports

```python
from typing import Iterator

class TeamReport:
    def generate_lazy(self) -> Iterator[str]:
        """Generate report sections on demand."""
        yield self._generate_header()
        yield self._generate_top_teams()
        yield self._generate_team_details()
        yield self._generate_footer()
```

### 3. Conditional Report Loading

```python
def analyze(output_filter: str | None = None):
    data = fetch_nhl_data()

    reports = ReportGenerator(data)

    # Only generate requested reports
    if output_filter == "teams":
        print(reports.team_report)  # Only this computed
    elif output_filter == "playoffs":
        print(reports.playoff_report)  # Only this computed
    else:
        # Generate all (default behavior)
        print(reports.full_report)
```

## Implementation Steps

1. Create `ReportGenerator` class with lazy properties
1. Convert reports to use lazy evaluation
1. Add CLI options for report filtering
1. Add tests for lazy behavior
1. Benchmark performance improvements
1. Update documentation

## Testing Strategy

```python
def test_lazy_report_generation():
    data = create_test_data()
    reports = ReportGenerator(data)

    # Access only team report
    team = reports.team_report

    # Verify other reports not generated
    assert reports._playoff_report is None
    assert reports._stats_report is None
```

## Acceptance Criteria

- [ ] Lazy properties implemented
- [ ] Reports generated only when accessed
- [ ] CLI options for report filtering
- [ ] Performance improvement measured
- [ ] Tests verify lazy behavior
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/reports/generator.py` - New lazy generator
- `src/nhl_scrabble/cli.py` - Use lazy reports
- `tests/unit/test_lazy_reports.py` - New tests

## Dependencies

None

## Additional Notes

**Benefits**:

- Faster execution for targeted queries
- Reduced memory usage
- Better user experience

**Expected Improvement**:

- 40-60% faster when viewing single report type
- 50% memory reduction for filtered views

## Implementation Notes

*To be filled during implementation*
