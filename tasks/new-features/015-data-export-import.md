# Add Data Export/Import Functionality

**GitHub Issue**: #158 - https://github.com/bdperkin/nhl-scrabble/issues/158

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-5 hours

## Description

Add ability to export/import complete datasets for backup, sharing, and offline analysis.

## Proposed Solution

```bash
# Export data
nhl-scrabble export --format json --output data.json
nhl-scrabble export --format sqlite --output data.db

# Import data
nhl-scrabble import data.json
nhl-scrabble analyze --import data.json --offline
```

## Acceptance Criteria

- [ ] JSON export/import working
- [ ] SQLite export/import working
- [ ] Offline analysis with imported data
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/export_import.py`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
