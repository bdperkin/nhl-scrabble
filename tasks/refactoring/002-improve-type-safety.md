# Improve Type Safety

**GitHub Issue**: #160 - https://github.com/bdperkin/nhl-scrabble/issues/160

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-10 hours

## Description

Improve type safety throughout codebase with stricter type hints, eliminate `Any`, and add runtime type checking where needed.

## Proposed Solution

```python
# Replace Any with specific types
def process_data(data: Any) -> Any:  # Before
def process_data(data: list[TeamScore]) -> TeamScoreResult:  # After

# Add TypedDict for structured dicts
from typing import TypedDict

class PlayerDict(TypedDict):
    name: str
    team: str
    score: int

# Add runtime validation
from pydantic import validate_call

@validate_call
def calculate_score(text: str) -> int:
    pass
```

## Acceptance Criteria

- [ ] No `Any` types remain
- [ ] All functions have type hints
- [ ] MyPy strict mode passes
- [ ] Runtime validation added
- [ ] Tests pass

## Related Files

- All Python files

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
