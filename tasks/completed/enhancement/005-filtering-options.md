# Add Advanced Filtering Options

**GitHub Issue**: #145 - https://github.com/bdperkin/nhl-scrabble/issues/145

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-5 hours

## Description

Add CLI filtering options to view specific teams, divisions, conferences, or players without re-running full analysis.

Currently shows all data. Users cannot:

- Filter by division/conference
- Show specific teams only
- Filter players by score range
- Exclude teams from results

## Proposed Solution

```bash
# Filter by division
nhl-scrabble analyze --division Atlantic

# Filter by conference
nhl-scrabble analyze --conference Eastern

# Filter by teams
nhl-scrabble analyze --teams TOR,MTL,OTT

# Filter players by score
nhl-scrabble analyze --min-score 50 --max-score 100

# Exclude teams
nhl-scrabble analyze --exclude BOS,NYR
```

## Implementation Steps

1. Add filter options to CLI
1. Implement filter logic
1. Update reports to respect filters
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Division filtering works
- [ ] Conference filtering works
- [ ] Team filtering works
- [ ] Score range filtering works
- [ ] Exclusion filtering works
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/cli.py` - Add filter options
- `src/nhl_scrabble/filters.py` - New module

## Dependencies

None

## Additional Notes

**Benefits**: Faster queries, targeted analysis, better UX

## Implementation Notes

*To be filled during implementation*
