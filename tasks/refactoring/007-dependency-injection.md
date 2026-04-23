# Add Dependency Injection

**GitHub Issue**: #163 - https://github.com/bdperkin/nhl-scrabble/issues/163

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-10 hours

## Description

Implement dependency injection pattern to improve testability and reduce coupling between components.

## Proposed Solution

```python
from typing import Protocol


# Define interfaces
class APIClient(Protocol):
    def get_standings(self) -> Standings: ...


class ScoreCalculator(Protocol):
    def calculate(self, text: str) -> int: ...


# Inject dependencies
class Analyzer:
    def __init__(
        self,
        api_client: APIClient,
        scorer: ScoreCalculator,
    ):
        self.api_client = api_client
        self.scorer = scorer

    def analyze(self):
        data = self.api_client.get_standings()
        # Use injected dependencies
```

## Acceptance Criteria

- [ ] Protocol interfaces defined
- [ ] Constructor injection implemented
- [ ] Easier testing with mocks
- [ ] Reduced coupling
- [ ] Tests pass

## Related Files

- All core modules

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
