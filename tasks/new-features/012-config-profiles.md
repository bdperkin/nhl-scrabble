# Add Configuration Profiles

**GitHub Issue**: #155 - https://github.com/bdperkin/nhl-scrabble/issues/155

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Add support for named configuration profiles for different analysis scenarios.

## Proposed Solution

```bash
# Create profile
nhl-scrabble profile create playoff --top-players 30 --divisions Atlantic,Metropolitan

# Use profile
nhl-scrabble analyze --profile playoff
```

## Acceptance Criteria

- [ ] Profile creation working
- [ ] Profile loading working
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/profiles.py`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
