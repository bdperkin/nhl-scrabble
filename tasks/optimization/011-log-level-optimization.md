# Optimize Logging with Level Guards

**GitHub Issue**: #142 - https://github.com/bdperkin/nhl-scrabble/issues/142

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Add level guards to expensive logging operations to avoid computing log messages when they won't be displayed.

Currently, string formatting and JSON serialization happen even when log level is too high to display the message.

## Current State

```python
# src/nhl_scrabble/api/nhl_client.py
logger.debug(f"API response: {response.json()}")  # Always computed!
logger.debug(f"Processing {len(roster)} players")  # len() always called!
```

**Problem**: String formatting and function calls execute even when DEBUG is disabled.

## Proposed Solution

### Use isEnabledFor Guards

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"API response: {response.json()}")

if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Processing {len(roster)} players")
```

### Or Lazy Logging

```python
# Let logger handle formatting only if needed
logger.debug("API response: %s", lambda: response.json())
```

## Implementation Steps

1. Audit expensive debug logging
1. Add `isEnabledFor()` guards
1. Benchmark performance improvement
1. Add tests
1. Update documentation

## Testing Strategy

```python
def test_logging_skips_expensive_ops():
    logger.setLevel(logging.INFO)  # Disable DEBUG

    expensive_call_count = 0

    def expensive_operation():
        nonlocal expensive_call_count
        expensive_call_count += 1
        return "result"

    # Without guard (bad)
    logger.debug(f"Result: {expensive_operation()}")
    assert expensive_call_count == 1  # Called anyway!

    # With guard (good)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Result: {expensive_operation()}")
    assert expensive_call_count == 1  # Not called!
```

## Acceptance Criteria

- [ ] Level guards added to expensive logging
- [ ] Tests verify guard behavior
- [ ] Performance improvement measured
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Add guards
- `src/nhl_scrabble/processors/*.py` - Add guards

## Dependencies

None

## Additional Notes

**Expected Improvement**: 5-10% faster in production (INFO level) due to avoided string formatting

## Implementation Notes

*To be filled during implementation*
