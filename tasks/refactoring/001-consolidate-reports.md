# Consolidate Report Classes

**GitHub Issue**: #159 - https://github.com/bdperkin/nhl-scrabble/issues/159

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Consolidate duplicate logic across report classes into shared base class and utilities.

Currently, report classes duplicate header generation, formatting, pagination, and footer logic.

## Proposed Solution

```python
class BaseReport:
    def generate_header(self, title: str) -> str:
        """Shared header generation."""
        pass

    def generate_footer(self) -> str:
        """Shared footer generation."""
        pass

    def paginate(self, items: list, page_size: int) -> Iterator[list]:
        """Shared pagination logic."""
        pass
```

## Acceptance Criteria

- [ ] Common logic extracted to base class
- [ ] All reports inherit from base
- [ ] No duplicate code
- [ ] Tests pass

## Related Files

- `src/nhl_scrabble/reports/base.py`
- `src/nhl_scrabble/reports/*.py`

## Dependencies

None

## Implementation Notes

*To be filled during implementation*
