# Add Watch Mode for Auto-Refresh

**GitHub Issue**: #148 - https://github.com/bdperkin/nhl-scrabble/issues/148

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Add watch mode to automatically refresh data at intervals, useful for monitoring during active roster changes.

Currently requires manual re-runs to see updates.

## Proposed Solution

```bash
# Watch with default interval (5 min)
nhl-scrabble watch

# Custom interval
nhl-scrabble watch --interval 60

# Watch with filters
nhl-scrabble watch --teams TOR,MTL --interval 30
```

```python
import time

def watch_mode(interval: int = 300):
    while True:
        data = analyze()
        display(data)
        print(f"\nRefreshing in {interval}s... (Ctrl+C to stop)")
        time.sleep(interval)
```

## Implementation Steps

1. Add watch command to CLI
1. Implement refresh loop
1. Add interval option
1. Add graceful shutdown
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Watch mode implemented
- [ ] Custom intervals supported
- [ ] Graceful shutdown on Ctrl+C
- [ ] Works with filters
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/cli.py` - Add watch command

## Dependencies

None

## Additional Notes

**Benefits**: Monitor roster changes, live updates, convenient UX

## Implementation Notes

*To be filled during implementation*
