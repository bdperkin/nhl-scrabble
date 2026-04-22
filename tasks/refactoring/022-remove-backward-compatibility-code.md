# Remove Backward Compatibility Code Before First Release

**GitHub Issue**: [#329](https://github.com/bdperkin/nhl-scrabble/issues/329)

## Priority

**MEDIUM** - Should Do (Next Month)

Code cleanup task to be completed before first public release to ensure clean, maintainable codebase without legacy cruft.

## Estimated Effort

2-4 hours

## Description

Remove all code that has been intentionally kept for backward compatibility across the project. Since we have not yet made a public release (currently pre-release v2.0.0), there are no external users relying on legacy interfaces. This is the ideal time to clean up the codebase and remove any deprecated or legacy code before establishing the public API contract with v2.0.0 release.

**Rationale**: First release should be as clean as possible without technical debt from legacy compatibility code. Once we release v2.0.0 publicly, we'll need to maintain backward compatibility for external users, making cleanup much harder.

## Current State

Several locations in the codebase contain code explicitly marked as "kept for backward compatibility":

### 1. Legacy CLI Report Generators (`src/nhl_scrabble/cli.py`)

Three legacy report generation functions that duplicate functionality now provided by the formatter factory pattern:

```python
def generate_json_report(  # Kept for backward compatibility
    teams: dict[str, Any],
    divisions: dict[str, Any],
    conferences: dict[str, Any],
    playoffs: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    """Generate JSON report using the formatter factory.

    This function is kept for backward compatibility with code that directly
    imports and calls it. New code should use get_formatter('json').format(data).
    """
    from nhl_scrabble.formatters import get_formatter

    data = {
        "teams": teams,
        "divisions": divisions,
        "conferences": conferences,
        "playoffs": playoffs,
        "summary": summary,
    }
    return get_formatter("json").format(data)


def generate_html_report(  # Kept for backward compatibility
    teams: dict[str, Any],
    divisions: dict[str, Any],
    conferences: dict[str, Any],
    playoffs: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    """Generate HTML report using the formatter factory."""
    from nhl_scrabble.formatters import get_formatter

    data = {
        "teams": teams,
        "divisions": divisions,
        "conferences": conferences,
        "playoffs": playoffs,
        "summary": summary,
    }
    return get_formatter("html").format(data)


def generate_csv_report(
    teams: dict[str, Any],
    divisions: dict[str, Any],
    conferences: dict[str, Any],
    playoffs: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    """Generate CSV report using the formatter factory."""
    from nhl_scrabble.formatters import get_formatter

    data = {
        "teams": teams,
        "divisions": divisions,
        "conferences": conferences,
        "playoffs": playoffs,
        "summary": summary,
    }
    return get_formatter("csv").format(data)
```

**Issues**:

- These functions are never called internally in the codebase
- They exist only as a compatibility shim for potential external callers
- They duplicate the formatter factory pattern functionality
- Listed in `.vulture_allowlist` to suppress dead code warnings

### 2. Static ScrabbleScorer Method (`src/nhl_scrabble/scoring/scrabble.py`)

The `calculate_score()` method has a docstring noting backward compatibility:

```python
@staticmethod
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name using standard values.

    This static method maintains backward compatibility with existing code.
    New code should create a ScrabbleScorer instance and use score_player().

    Args:
        name: The name to score (spaces ignored, case-insensitive)

    Returns:
        Total Scrabble score for the name

    Example:
        >>> ScrabbleScorer.calculate_score("Ovechkin")
        29
    """
    return sum(ScrabbleScorer.SCRABBLE_VALUES.get(char.upper(), 0) for char in name if char.isalpha())
```

**Analysis Needed**:

- Verify if this is genuinely backward compatibility or the primary API
- Check all callers to determine if this is legacy or intentional design
- This may be intentional static method design, not legacy code

### 3. Vulture Allowlist (`.vulture_allowlist`)

Four entries for legacy functions:

```
# Legacy CLI report generators (kept for backward compatibility)
generate_json_report  # cli.py - legacy JSON report generator
generate_html_report  # cli.py - legacy HTML report generator
generate_csv_report  # cli.py - legacy CSV report generator
generate_json_report  # SeasonComparison method - public API for backward compatibility
```

**Issues**:

- Allowlist masks dead code that should be removed
- Makes it harder to detect actual unused code in the future

### 4. Test References

Some tests may reference backward compatibility for validation purposes. These should be updated after removing the legacy code.

## Proposed Solution

### Phase 1: Remove Legacy CLI Functions

1. **Delete functions from `cli.py`**:

   - Remove `generate_json_report()`
   - Remove `generate_html_report()`
   - Remove `generate_csv_report()`

1. **Update `.vulture_allowlist`**:

   - Remove entries for the three deleted functions
   - Keep SeasonComparison.generate_json_report if it's public API (needs verification)

### Phase 2: Evaluate ScrabbleScorer Static Method

1. **Analyze usage**:

   - Search all callers of `ScrabbleScorer.calculate_score()`
   - Determine if this is legacy or intentional design

1. **Decision**:

   - **If legacy**: Remove static method, update callers to use instance method
   - **If intentional**: Update docstring to remove "backward compatibility" language
   - **If uncertain**: Keep as-is and document as primary API

### Phase 3: Update Tests

1. **Search for test references**:

   - Find tests mentioning "backward" or "backwards" compatibility
   - Update or remove as appropriate

1. **Verify removal**:

   - Run full test suite to ensure nothing breaks
   - Check for any import errors or missing references

## Implementation Steps

1. **Verify no external usage**:

   ```bash
   # Search for direct imports of legacy functions
   git grep "from nhl_scrabble.cli import generate_json_report"
   git grep "from nhl_scrabble.cli import generate_html_report"
   git grep "from nhl_scrabble.cli import generate_csv_report"
   ```

1. **Remove legacy CLI functions**:

   - Open `src/nhl_scrabble/cli.py`
   - Delete `generate_json_report()` function (lines ~TBD)
   - Delete `generate_html_report()` function (lines ~TBD)
   - Delete `generate_csv_report()` function (lines ~TBD)

1. **Update vulture allowlist**:

   - Open `.vulture_allowlist`
   - Remove three CLI function entries
   - Verify SeasonComparison.generate_json_report is still needed

1. **Analyze ScrabbleScorer.calculate_score()**:

   ```bash
   # Find all callers
   git grep "ScrabbleScorer.calculate_score"
   git grep "calculate_score"
   ```

   - If only used internally: Consider keeping as primary API
   - If marked legacy but widely used: Update docstring
   - If truly legacy: Remove and update callers

1. **Update tests**:

   ```bash
   # Find backward compatibility references
   git grep -i "backward" tests/
   git grep -i "backwards" tests/
   ```

   - Update test docstrings/comments as needed
   - Ensure all tests still pass

1. **Run full test suite**:

   ```bash
   make test           # Unit and integration tests
   make quality        # All quality checks
   tox -p auto         # Full tox matrix
   ```

1. **Update documentation**:

   - Search docs/ for backward compatibility references
   - Update any migration guides or changelogs
   - Remove outdated upgrade instructions

## Testing Strategy

### Unit Tests

- **Formatter tests**: Verify formatter factory works without legacy functions
- **ScrabbleScorer tests**: Ensure scoring still works after any changes
- **No regressions**: All existing tests must pass

### Integration Tests

- **CLI tests**: Verify all output formats work via --format option
- **End-to-end**: Run full analysis with all formatters

### Quality Checks

```bash
# Verify no dead code introduced
tox -e vulture

# Verify no type errors
tox -e mypy

# Verify no linting issues
tox -e ruff-check

# Full quality suite
make quality
```

### Manual Verification

1. **Search for references**:

   ```bash
   # No imports of legacy functions
   git grep "generate_json_report"
   git grep "generate_html_report"
   git grep "generate_csv_report"

   # No backward compatibility comments remaining
   git grep -i "backward compatibility"
   git grep -i "backwards compatibility"
   git grep -i "kept for backward"
   ```

1. **Run analyzer with all formats**:

   ```bash
   nhl-scrabble analyze --format json
   nhl-scrabble analyze --format html
   nhl-scrabble analyze --format csv
   # ... test all 9 formats
   ```

## Acceptance Criteria

- [ ] `generate_json_report()` removed from `cli.py`
- [ ] `generate_html_report()` removed from `cli.py`
- [ ] `generate_csv_report()` removed from `cli.py`
- [ ] Legacy function entries removed from `.vulture_allowlist`
- [ ] ScrabbleScorer.calculate_score() evaluated and decision documented
- [ ] No references to "backward compatibility" in code (except historical CHANGELOG)
- [ ] No imports of removed functions anywhere in codebase
- [ ] All unit tests pass (`make test`)
- [ ] All integration tests pass
- [ ] All quality checks pass (`make quality`)
- [ ] All tox environments pass (`tox -p auto`)
- [ ] Vulture reports no false positives
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated with removed functions

## Related Files

- `src/nhl_scrabble/cli.py` - Contains 3 legacy report generators
- `src/nhl_scrabble/scoring/scrabble.py` - Contains static method with compatibility note
- `.vulture_allowlist` - Contains entries for legacy functions
- `tests/unit/test_cli.py` - May test legacy functions
- `tests/unit/test_scrabble.py` - Tests ScrabbleScorer
- `docs/` - May reference old APIs
- `CHANGELOG.md` - Should document removal

## Dependencies

**None** - This task can be completed independently.

**Blocking**: Should be completed before v2.0.0 release to avoid establishing deprecated API as public contract.

## Additional Notes

### Why Remove Now?

1. **Pre-release status**: Currently v2.0.0 is in development, no public release yet
1. **No external users**: No one depends on these legacy interfaces
1. **Clean slate**: First release should establish clean, maintainable API
1. **Avoid debt**: Once released, we must maintain backward compatibility

### Breaking Changes Acceptable

Since this is pre-release:

- ✅ OK to remove functions before v2.0.0 release
- ✅ OK to change APIs before public release
- ❌ NOT OK to remove after v2.0.0 release without deprecation cycle

### Post-Release Process

After v2.0.0 release, any backward compatibility changes must follow:

1. Mark function as deprecated with warnings
1. Document in CHANGELOG and migration guide
1. Maintain for at least one minor version
1. Remove in next major version (v3.0.0)

### Risk Assessment

**Low Risk**:

- All code is internal to the package
- No external dependencies on legacy functions
- Full test coverage ensures no breakage
- Can be easily reverted if issues found

**Validation Period**:

- Complete task at least 1 week before v2.0.0 release
- Allow time for testing and validation
- Monitor for any unforeseen issues

## Implementation Notes

*To be filled during implementation:*

### Actual Implementation

*What was actually done, any deviations from plan*

### Challenges Encountered

*Any unexpected issues or complications*

### Deviations from Plan

*Changes to the proposed solution and why*

### Actual vs Estimated Effort

- **Estimated**: 2-4h
- **Actual**: TBD
- **Reason**: TBD
