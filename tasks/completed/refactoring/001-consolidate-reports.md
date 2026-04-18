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

- [x] Common logic extracted to base class
- [x] All reports inherit from base
- [x] No duplicate code
- [x] Tests pass

## Related Files

- `src/nhl_scrabble/reports/base.py`
- `src/nhl_scrabble/reports/*.py`
- `tests/unit/test_base_reporter.py` (new)
- `CHANGELOG.md`
- `pyproject.toml`

## Dependencies

None

## Implementation Notes

**Implemented**: 2026-04-17
**Branch**: refactoring/001-consolidate-reports
**PR**: #184 - https://github.com/bdperkin/nhl-scrabble/pull/184
**Commits**: 1 commit (4f07437)

### Actual Implementation

Successfully extracted common patterns into BaseReporter utility methods:

**Utility Methods Added:**

1. `_sort_by_key()` - Generic sorting with configurable key function and direction
1. `_take_top()` - Simple pagination/limiting to top N items
1. `_paginate()` - Generic pagination into chunks (for future use)
1. `_format_score()` - Integer formatting with configurable width
1. `_format_average()` - Float formatting with configurable width and decimals
1. `_format_team_list()` - Sorted, comma-separated team list formatting

**Report Class Updates:**

- TeamReporter: Replaced inline sorting/limiting with `_sort_by_key()` and `_take_top()`
- DivisionReporter: Replaced inline sorting and formatting with utilities
- ConferenceReporter: Replaced inline sorting and formatting with utilities
- StatsReporter: Replaced inline sorting/limiting with `_sort_by_key()` and `_take_top()`
- PlayoffReporter: Replaced inline formatting with `_format_score()` and `_format_average()`

**Import Improvements:**

- Moved `Callable`, `Iterable`, `Iterator` from `typing` to `collections.abc` (Python 3.10+ best practice)

### Challenges Encountered

- **Ruff SLF001 errors**: Tests need to access protected methods (`_format_header`, etc.)
  - Solution: Added `SLF001` to test file ignores in `pyproject.toml`
- **Black formatting**: Minor line length adjustments in report classes
  - Solution: Let Black reformat (consistent with project style)

### Deviations from Plan

**Additions beyond original scope:**

- Added `_paginate()` method for future use (comprehensive approach)
- Added `_format_team_list()` for consistent team listing
- Added TypeVar `T` for generic type safety in sorting/pagination methods
- Created comprehensive test suite (29 tests) covering all edge cases

**Approach differences:**

- Used `collections.abc` imports instead of `typing` (modern Python 3.10+ practice)
- Made utilities more configurable (width, decimals parameters) for flexibility
- Added detailed docstrings beyond minimum requirements

### Actual vs Estimated Effort

- **Estimated**: 6-8 hours
- **Actual**: ~3 hours
- **Variance**: -50% (faster than estimated)
- **Reason**:
  - Reports were already well-structured with clear patterns
  - Base class already existed with header/subheader methods
  - Less duplication than initially assumed
  - No complex edge cases to handle

### Related PRs

- #184 - Main implementation (this PR)

### Lessons Learned

**Code Quality:**

- The existing report classes were already well-designed, minimizing refactoring complexity
- Starting with a solid base class (BaseReporter) made extension straightforward
- Type hints and generics (`TypeVar`) improve utility method flexibility

**Testing:**

- Testing utility methods separately from report classes is valuable
- Concrete test implementations help demonstrate proper usage
- Edge case testing (empty lists, large numbers, etc.) builds confidence

**Performance:**

- Utility method overhead is negligible compared to existing inline code
- Test coverage increased from 91.81% to 92.17% (+0.36%)
- All 234 tests pass (205 existing + 29 new)

**Process:**

- Pre-commit hooks caught import style issues early (UP035)
- Black formatting adjustments were minimal and automatic
- GitHub Actions CI/CD will validate on multiple Python versions

### Test Coverage

- **Total tests**: 234 (205 existing + 29 new)
- **New test file**: `tests/unit/test_base_reporter.py` with 29 comprehensive tests
- **Coverage**: 92.17% overall (+0.36% from 91.81%)
- **All base utility methods**: 100% coverage

### Code Metrics

- **Files changed**: 9 files
- **Lines added**: +353
- **Lines removed**: -31
- **Net change**: +322 lines
- **Utility methods**: 6 new methods in BaseReporter
- **Reports updated**: 5 report classes
