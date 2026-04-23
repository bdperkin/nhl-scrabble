# Implement Consistent Error Handling Strategy

**GitHub Issue**: #162 - https://github.com/bdperkin/nhl-scrabble/issues/162

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Implement consistent error handling with custom exception hierarchy, proper logging, and user-friendly error messages.

## Proposed Solution

```python
# Custom exceptions
class NHLScrabbleError(Exception):
    """Base exception for all NHL Scrabble errors."""

    pass


class APIError(NHLScrabbleError):
    """NHL API errors."""

    pass


class DataValidationError(NHLScrabbleError):
    """Data validation errors."""

    pass


# Consistent error handling
try:
    data = api_client.fetch()
except APIError as e:
    logger.error(f"API error: {e}")
    raise NHLScrabbleError("Failed to fetch NHL data") from e
```

## Acceptance Criteria

- [ ] Exception hierarchy defined
- [ ] All errors use custom exceptions
- [ ] User-friendly error messages
- [ ] Proper logging
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/exceptions.py`
- All Python files

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
