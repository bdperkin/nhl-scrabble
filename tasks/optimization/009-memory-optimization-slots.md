# Memory Optimization with __slots__

**GitHub Issue**: #140 - https://github.com/bdperkin/nhl-scrabble/issues/140

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Reduce memory usage by adding `__slots__` to dataclasses and Pydantic models to prevent `__dict__` overhead.

With ~700 player objects and ~32 team objects, memory savings can be significant (30-50% reduction per instance).

## Current State

```python
# src/nhl_scrabble/models/player.py
@dataclass
class PlayerScore:
    name: str
    team: str
    score: int
    # Has __dict__ overhead
```

## Proposed Solution

### Dataclasses with __slots__

```python
from dataclasses import dataclass

@dataclass(slots=True)  # Python 3.10+
class PlayerScore:
    name: str
    team: str
    score: int
```

### Pydantic with config

```python
from pydantic import BaseModel

class Player(BaseModel):
    firstName: str
    lastName: str

    class Config:
        slots = True  # Pydantic v2
```

## Implementation Steps

1. Add `slots=True` to all dataclasses
1. Add slots config to Pydantic models
1. Measure memory reduction
1. Add tests
1. Update documentation

## Testing Strategy

```python
import sys

def test_slots_reduces_memory():
    player = PlayerScore("Test", "TOR", 100)

    # Verify __slots__ present
    assert hasattr(PlayerScore, "__slots__")

    # Verify no __dict__
    assert not hasattr(player, "__dict__")
```

## Acceptance Criteria

- [ ] __slots__ added to all dataclasses
- [ ] __slots__ added to Pydantic models
- [ ] Memory reduction measured (30-50%)
- [ ] Tests verify __slots__ usage
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/models/*.py` - Add __slots__

## Dependencies

None (Python 3.10+ supports dataclass slots)

## Additional Notes

**Expected Improvement**: 30-50% memory reduction for model instances

## Implementation Notes

*To be filled during implementation*
