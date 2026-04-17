# Add Memoization to Scrabble Scoring

**GitHub Issue**: #139 - https://github.com/bdperkin/nhl-scrabble/issues/139

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Add memoization/caching to Scrabble score calculations to avoid recomputing scores for duplicate names.

Currently, `calculate_score()` recomputes every time even for identical names. With ~700 NHL players, there are many duplicate first/last names (e.g., "John", "Smith").

## Current State

```python
# src/nhl_scrabble/scoring/scrabble.py
class ScrabbleScorer:
    def calculate_score(self, text: str) -> int:
        return sum(self.SCRABBLE_VALUES.get(char.upper(), 0) for char in text)
```

**Problem**: Each call recalculates, even for duplicates.

## Proposed Solution

### Use functools.lru_cache

```python
from functools import lru_cache

class ScrabbleScorer:
    @staticmethod
    @lru_cache(maxsize=2048)
    def calculate_score(text: str) -> int:
        return sum(ScrabbleScorer.SCRABBLE_VALUES.get(char.upper(), 0) for char in text)
```

### Or manual cache

```python
class ScrabbleScorer:
    def __init__(self):
        self._cache: dict[str, int] = {}

    def calculate_score(self, text: str) -> int:
        if text not in self._cache:
            self._cache[text] = sum(
                self.SCRABBLE_VALUES.get(char.upper(), 0) for char in text
            )
        return self._cache[text]
```

## Implementation Steps

1. Add `@lru_cache` to `calculate_score()`
1. Benchmark performance improvement
1. Add cache statistics logging
1. Add tests for caching behavior
1. Update documentation

## Testing Strategy

```python
def test_score_caching():
    scorer = ScrabbleScorer()

    # First call computes
    score1 = scorer.calculate_score("McDavid")

    # Second call uses cache
    score2 = scorer.calculate_score("McDavid")

    assert score1 == score2
```

## Acceptance Criteria

- [ ] Memoization implemented
- [ ] Performance improvement measured
- [ ] Cache statistics logged
- [ ] Tests verify caching
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/scoring/scrabble.py` - Add caching

## Dependencies

None (uses functools from stdlib)

## Additional Notes

**Expected Improvement**: 30-40% faster scoring with high name duplication

## Implementation Notes

*To be filled during implementation*
