# Improve Function Example Coverage in Docstrings

**GitHub Issue**: #353 - https://github.com/bdperkin/nhl-scrabble/issues/353

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Add usage examples to 50-100 functions that currently lack them, focusing on public APIs, complex functions, and commonly misunderstood utilities. This improves onboarding, reduces support questions, and makes the codebase more accessible.

## Current State

**Current Example Coverage**:

- Total functions: ~300 across codebase
- Functions with examples: ~180-210 (60-70%)
- Functions without examples: ~90-120 (30-40%)

**Impact**:

- Developers must read implementation to understand usage
- Higher cognitive load for new contributors
- More support questions
- Slower onboarding

**Functions Lacking Examples**:

- Utility functions (validators, helpers)
- Formatter classes
- Configuration helpers
- Some processor methods
- Internal APIs

**Example of Well-Documented Function**:

```python
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name.

    Args:
        name: The name to score (can include spaces)

    Returns:
        The total Scrabble score

    Examples:
        >>> ScrabbleScorer.calculate_score("ALEX")
        11
        >>> ScrabbleScorer.calculate_score("Ovechkin")
        20
    """
```

**Example of Function Needing Examples**:

```python
def validate_file_path(path: str | Path, must_exist: bool = False) -> Path:
    """Validate and normalize a file path.

    Args:
        path: File path to validate
        must_exist: Whether file must exist

    Returns:
        Normalized absolute Path object

    Raises:
        ValidationError: If path is invalid or doesn't exist

    # ❌ NO EXAMPLES - Users must guess usage!
    """
```

## Proposed Solution

Systematically add usage examples to 50-100 functions, prioritizing:

1. Public APIs (exported in `__all__`)
1. Complex functions (>20 lines, multiple params)
1. Validation/utility functions
1. Functions commonly referenced in docs
1. Functions with non-obvious behavior

### Target Functions by Module

**Priority 1: Validators** (~15 functions, 30 min):

- `nhl_scrabble/validators.py`
  - `validate_file_path()` - Path validation
  - `validate_team_abbreviation()` - Team code validation
  - `validate_player_name()` - Player name validation
  - `validate_api_response_structure()` - Response validation
  - `validate_output_format()` - Format validation

**Priority 2: Configuration** (~10 functions, 30 min):

- `nhl_scrabble/config.py`
  - `Config.from_env()` - Load from environment
  - `Config.from_file()` - Load from file
  - `Config.merge()` - Merge configurations
- `nhl_scrabble/config_validators.py`
  - Validation helper functions

**Priority 3: Formatters** (~20 functions, 1h):

- `nhl_scrabble/formatters/factory.py`
  - `get_formatter()` - Already has examples ✅
- `nhl_scrabble/formatters/json_formatter.py`
  - `JSONFormatter.format()` - Format to JSON
- `nhl_scrabble/formatters/yaml_formatter.py`
  - `YAMLFormatter.format()` - Format to YAML
- `nhl_scrabble/formatters/html_formatter.py`
  - `HTMLFormatter.format()` - Format to HTML
- `nhl_scrabble/formatters/template_formatter.py`
  - `TemplateFormatter.format()` - Custom templates
- Other formatter classes

**Priority 4: Processors** (~10 functions, 30 min):

- `nhl_scrabble/processors/team_processor.py`
  - `TeamProcessor.process_team()` - Process team data
  - `TeamProcessor.aggregate_scores()` - Aggregate scores
- `nhl_scrabble/processors/playoff_calculator.py`
  - `PlayoffCalculator.calculate_wild_cards()` - Calculate wild cards
  - `PlayoffCalculator.apply_tiebreakers()` - Apply tiebreakers

**Priority 5: Utilities** (~15 functions, 45 min):

- `nhl_scrabble/utils/retry.py`
  - `@retry` decorator - Retry logic
- `nhl_scrabble/rate_limiter.py`
  - `RateLimiter` usage examples
- `nhl_scrabble/search.py`
  - `PlayerSearch.search()` - Search players
  - `PlayerSearch.filter()` - Filter results
- `nhl_scrabble/filters.py`
  - Various filter functions

**Priority 6: Security** (~10 functions, 30 min):

- `nhl_scrabble/security/circuit_breaker.py`
  - Already has examples ✅
- `nhl_scrabble/security/dos_protection.py`
  - DoS protection usage
- `nhl_scrabble/security/ssrf_protection.py`
  - SSRF validation usage

### Example Template

**Standard Example Format**:

```python
def function_name(param1: type1, param2: type2 = default) -> return_type:
    """One-line summary.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: value)

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this is raised

    Examples:
        Basic usage:

        >>> result = function_name(value1, value2)
        >>> result
        expected_output

        With optional parameter:

        >>> result = function_name(value1, param2=custom_value)
        >>> result
        different_output

        Error case:

        >>> function_name(invalid_value)
        Traceback (most recent call last):
            ...
        ExceptionType: Error message
    """
```

## Implementation Steps

1. **Identify target functions** (30 min)

   ```bash
   # Find functions without examples
   python scripts/find_functions_without_examples.py

   # Or manually review each module
   ```

1. **Create example addition script** (30 min)

   ```python
   # scripts/find_functions_without_examples.py
   """Find functions lacking usage examples in docstrings."""

   import ast
   from pathlib import Path


   def has_examples(docstring: str | None) -> bool:
       """Check if docstring contains examples."""
       if not docstring:
           return False
       return "Examples:" in docstring or ">>>" in docstring


   def find_functions_without_examples(file_path: Path) -> list[str]:
       """Find functions in a file without examples."""
       content = file_path.read_text()
       tree = ast.parse(content)

       functions_without_examples = []

       for node in ast.walk(tree):
           if isinstance(node, ast.FunctionDef):
               docstring = ast.get_docstring(node)
               if not has_examples(docstring):
                   functions_without_examples.append(node.name)

       return functions_without_examples
   ```

1. **Add examples to validators** (30 min)

   - Open `src/nhl_scrabble/validators.py`
   - Add examples to each validation function
   - Test examples with pytest --doctest-modules
   - Commit: "docs: Add examples to validation functions"

1. **Add examples to configuration** (30 min)

   - Open `src/nhl_scrabble/config.py`
   - Add examples to Config class methods
   - Add examples to config_validators.py
   - Test and commit

1. **Add examples to formatters** (1 hour)

   - Work through each formatter module
   - Add examples showing input → output
   - Include template examples for TemplateFormatter
   - Test and commit

1. **Add examples to processors** (30 min)

   - Open processor modules
   - Add examples with sample data
   - Show expected processing results
   - Test and commit

1. **Add examples to utilities** (45 min)

   - Add examples to retry decorator
   - Add examples to rate limiter
   - Add examples to search/filter functions
   - Test and commit

1. **Add examples to security** (30 min)

   - Add examples to DoS protection
   - Add examples to SSRF validation
   - Test and commit

1. **Verify coverage improvement** (15 min)

   ```bash
   # Run doctest on all modules
   pytest --doctest-modules src/nhl_scrabble/ -v

   # Check example coverage
   python scripts/find_functions_without_examples.py

   # Target: <10% functions without examples
   ```

1. **Update documentation** (15 min)

   - Update audit report with new metrics
   - Document example coverage improvement
   - Add to quality checklist

## Testing Strategy

### Manual Testing

**Test Each Example**:

```bash
# Test validators
pytest --doctest-modules src/nhl_scrabble/validators.py -v

# Test formatters
pytest --doctest-modules src/nhl_scrabble/formatters/ -v

# Test all modules
pytest --doctest-modules src/nhl_scrabble/ -v
```

**Verify Example Quality**:

- Examples execute without errors
- Examples show realistic usage
- Examples cover common use cases
- Examples are concise and clear

### Coverage Measurement

**Before**:

```bash
python scripts/find_functions_without_examples.py

# Expected output:
# Functions without examples: 90-120 (30-40%)
```

**After**:

```bash
python scripts/find_functions_without_examples.py

# Target output:
# Functions without examples: <30 (<10%)
```

### Example Categories

Add examples for:

- ✅ Basic usage (required)
- ✅ With optional parameters (if applicable)
- ✅ Error cases (if function raises exceptions)
- ✅ Edge cases (if non-obvious)

## Acceptance Criteria

- [x] 50-100 functions have new usage examples
- [x] All validator functions have examples
- [x] All configuration functions have examples
- [x] All formatter classes have examples
- [x] All processor methods have examples
- [x] Key utility functions have examples
- [x] Security functions have examples
- [x] All new examples pass doctest
- [x] Example coverage >90% (target)
- [x] Documentation updated with metrics

## Related Files

**Modified Files** (~20 files):

- `src/nhl_scrabble/validators.py` - Add validation examples
- `src/nhl_scrabble/config.py` - Add config examples
- `src/nhl_scrabble/config_validators.py` - Add validator examples
- `src/nhl_scrabble/formatters/*.py` - Add formatter examples (8 files)
- `src/nhl_scrabble/processors/*.py` - Add processor examples (2 files)
- `src/nhl_scrabble/utils/retry.py` - Add retry examples
- `src/nhl_scrabble/rate_limiter.py` - Add rate limiter examples
- `src/nhl_scrabble/search.py` - Add search examples
- `src/nhl_scrabble/filters.py` - Add filter examples
- `src/nhl_scrabble/security/*.py` - Add security examples (3 files)

**New Files**:

- `scripts/find_functions_without_examples.py` - Coverage analysis

**Documentation Updates**:

- `docs/audit/documentation-audit-2026-04-23.md` - Update metrics
- `docs/audit/README.md` - Update coverage tracking

## Dependencies

**Required Tools**:

- pytest (for doctest validation)
- Python AST module (for function discovery)

**Task Dependencies**:

- Documentation audit completed (task 013) ✅
- Automated example testing (task 026) - Recommended for validation

**Related Tasks**:

- Task 025: Add link validation
- Task 026: Add example testing (ensures examples work)

## Additional Notes

### Benefits

**For New Contributors**:

- Easier to understand function usage
- Lower barrier to entry
- Faster onboarding
- Self-documenting code

**For Existing Developers**:

- Quick reference without reading implementation
- Examples serve as mini-tests
- Easier to use unfamiliar modules
- Reduced cognitive load

**For Users**:

- Better documentation
- Working example code
- Fewer support questions
- Higher quality perception

### Example Writing Guidelines

**Good Examples**:

```python
Examples:
    Basic validation:

    >>> validate_file_path("/tmp/output.txt")
    PosixPath('/tmp/output.txt')

    Check file exists:

    >>> validate_file_path("/tmp/output.txt", must_exist=True)
    Traceback (most recent call last):
        ...
    ValidationError: File does not exist: /tmp/output.txt
```

**Poor Examples**:

```python
Examples:
    >>> validate_file_path(path)  # ❌ What is 'path'?
    result

    >>> x = validate_file_path(y)  # ❌ Unclear names
    >>> print(x)  # ❌ No output shown
```

### Function Prioritization Criteria

**High Priority** (must have examples):

1. Public APIs (in `__all__`)
1. Functions with >3 parameters
1. Functions with complex behavior
1. Functions raising multiple exceptions
1. Functions commonly used (imported >5 times)

**Medium Priority** (should have examples):

1. Helper functions used in docs
1. Validation/conversion functions
1. Factory/builder methods
1. Configuration loaders

**Low Priority** (optional):

1. Private functions (leading `_`)
1. Trivial getters/setters
1. Simple property accessors
1. Abstract method stubs

### Doctest Best Practices

**Use Normalized Whitespace**:

```python
# Good - handles whitespace differences
>>> result = get_data()  # doctest: +NORMALIZE_WHITESPACE
>>> result
{'key': 'value'}
```

**Use Ellipsis for Variable Output**:

```python
# Good - handles timestamps, IDs, etc.
>>> result = get_stats()
>>> result  # doctest: +ELLIPSIS
{'timestamp': '2026-04-...', 'count': 42}
```

**Skip Complex Examples**:

```python
# Good - skip examples needing network/files
>>> # doctest: +SKIP
>>> data = fetch_from_api()
```

### Coverage Tracking

**Metrics to Track**:

- Total functions: ~300
- Functions with examples: Before: ~60-70%, After: >90%
- Modules with 100% example coverage
- Example test pass rate: 100%

**Measurement Script**:

```bash
# Run coverage analysis
python scripts/find_functions_without_examples.py --stats

# Expected output:
# Module                        Functions  With Examples  Coverage
# validators.py                      15             15     100%
# config.py                          12             12     100%
# formatters/json_formatter.py        5              5     100%
# ...
# Total                             300            275      92%
```

### Time Estimates by Priority

| Priority       | Functions | Est. Time  | Focus                         |
| -------------- | --------- | ---------- | ----------------------------- |
| 1 - Validators | 15        | 30 min     | Path, team, player validation |
| 2 - Config     | 10        | 30 min     | Loading, merging configs      |
| 3 - Formatters | 20        | 1 hour     | JSON, YAML, HTML, templates   |
| 4 - Processors | 10        | 30 min     | Team processing, playoffs     |
| 5 - Utilities  | 15        | 45 min     | Retry, rate limit, search     |
| 6 - Security   | 10        | 30 min     | DoS, SSRF protection          |
| **Total**      | **80**    | **~3.75h** |                               |

### Documentation Audit Context

This task addresses **Gap #4** from the documentation audit:

> **Gap 4: Incomplete Function Examples**
>
> **Impact**: LOW-MEDIUM
> **Affected**: ~100 functions lacking usage examples
>
> **Recommendation**: Add examples to 50-100 commonly used functions

**Audit Finding**:

- "Approximately 30-40% of functions lack usage examples in docstrings"
- "While simple functions may not need examples, complex ones would benefit greatly"
- Priority: MEDIUM
- Effort: 3-4 hours ✅

### Quality Checklist

For each example added, verify:

- [ ] Example uses realistic data
- [ ] Example executes without errors
- [ ] Example shows expected output
- [ ] Example covers common use case
- [ ] Example is concise (\<10 lines)
- [ ] Example follows doctest format
- [ ] Example tested with pytest --doctest-modules

### Future Enhancements

**Potential Improvements**:

1. Generate example gallery in documentation
1. Track example coverage over time
1. Add example complexity metrics
1. Generate examples from unit tests

**Not Included** (out of scope):

- Auto-generating examples from tests
- Interactive example playground
- Example performance benchmarking

## Implementation Notes

*To be filled during implementation:*

- Total functions enhanced
- Functions by priority (1-6)
- Time spent per priority
- Examples that were difficult to write
- Modules reaching 100% coverage
- Coverage improvement (before vs after)
- Any challenges encountered
- Deviations from plan
