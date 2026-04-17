# Add Offline Mode Support

**GitHub Issue**: #154 - https://github.com/bdperkin/nhl-scrabble/issues/154

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-5 hours

## Description

Add offline mode that works with cached/downloaded data when NHL API is unavailable.

## Proposed Solution

```bash
# Download data for offline use
nhl-scrabble download --season 20232024

# Use offline mode
nhl-scrabble analyze --offline
```

## Acceptance Criteria

- [ ] Offline data download working
- [ ] Offline analysis working
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/offline.py`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
