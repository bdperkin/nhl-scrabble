# Add pytest-clarity for Improved Assertion Diffs

**GitHub Issue**: #123 - https://github.com/bdperkin/nhl-scrabble/issues/123

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

15-30 minutes

## Description

Add pytest-clarity plugin to enhance assertion error output with better diff formatting, colored output, and clearer visualization of differences between expected and actual values.

Currently, pytest assertion errors show basic text diffs which can be hard to read, especially for:

- Complex data structures (nested dictionaries, lists)
- Long strings with subtle differences
- API responses with many fields
- JSON objects with deep nesting

pytest-clarity enhances assertion failures with:

- Clearer visual diffs with syntax highlighting
- Better formatting for complex objects
- Side-by-side comparison for easier scanning
- Color-coded additions and deletions
- Smart diff algorithms for nested structures

**Impact**: Faster debugging of test failures, better visibility into assertion differences, improved developer experience

**ROI**: Very High - minimal setup effort (5 minutes), immediate improvement when debugging test failures

## Current State

Tests use default pytest assertion rewriting which shows basic text diffs:

**Current assertion output** (hard to read):

```python
# Test code
def test_team_score():
    expected = {
        "team_abbrev": "TOR",
        "total_score": 1234,
        "players": [
            {"firstName": "Auston", "lastName": "Matthews", "score": 156},
            {"firstName": "Mitch", "lastName": "Marner", "score": 145},
            {"firstName": "William", "lastName": "Nylander", "score": 138},
        ],
        "division": "Atlantic",
        "conference": "Eastern",
    }
    actual = get_team_score("TOR")
    assert actual == expected

# Current pytest output (hard to parse):
    def test_team_score():
        expected = {...}
        actual = get_team_score("TOR")
>       assert actual == expected
E       AssertionError: assert {'conference': 'Eastern', 'division': 'Atlantic', 'players': [{'firstName': 'Auston', 'lastName': 'Matthews', 'score': 156}, {'firstName': 'Mitch', 'lastName': 'Marner', 'score': 145}, {'firstName': 'William', 'lastName': 'Nylander', 'score': 138}], 'team_abbrev': 'TOR', 'total_score': 1234} == {'conference': 'Eastern', 'division': 'Atlantic', 'players': [{'firstName': 'Auston', 'lastName': 'Matthews', 'score': 156}, {'firstName': 'Mitch', 'lastName': 'Marner', 'score': 145}, {'firstName': 'William', 'lastName': 'Nylander', 'score': 139}], 'team_abbrev': 'TOR', 'total_score': 1235}
E
E       Full diff:
E       - {'conference': 'Eastern',
E       -  'division': 'Atlantic',
E       -  'players': [{'firstName': 'Auston', 'lastName': 'Matthews', 'score': 156},
E       -              {'firstName': 'Mitch', 'lastName': 'Marner', 'score': 145},
E       -              {'firstName': 'William', 'lastName': 'Nylander', 'score': 138}],
E       -  'team_abbrev': 'TOR',
E       -  'total_score': 1234}
E       + {'conference': 'Eastern',
E       +  'division': 'Atlantic',
E       +  'players': [{'firstName': 'Auston', 'lastName': 'Matthews', 'score': 156},
E       +              {'firstName': 'Mitch', 'lastName': 'Marner', 'score': 145},
E       +              {'firstName': 'William', 'lastName': 'Nylander', 'score': 139}],
E       +  'team_abbrev': 'TOR',
E       +  'total_score': 1235}
```

**Problems with current output:**

- Shows entire structure twice (- for expected, + for actual)
- Hard to spot the actual differences (score: 138 vs 139, total: 1234 vs 1235)
- No color coding in diff
- No highlighting of changed values
- Repetitive output for large objects

**Missing features:**

- No pytest-clarity in dependencies
- No smart diff highlighting
- No color-coded changes
- No side-by-side comparison
- No nested structure visualization

## Proposed Solution

Add pytest-clarity for automatically enhanced assertion error output:

**Step 1: Add pytest-clarity to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "pytest-xdist>=3.5.0",
    "pytest-randomly>=3.15.0",
    "pytest-sugar>=1.0.0",
    "pytest-clarity>=1.0.1",  # Add improved assertion diffs
    "beautifulsoup4>=4.12.0",
]
```

**Step 2: pytest-clarity works automatically** (no configuration needed):

```bash
# After installation, pytest-clarity automatically enhances assertion output
pytest
```

**Step 3: Enhanced assertion output** (with pytest-clarity):

```python
# Same test code
def test_team_score():
    expected = {...}
    actual = get_team_score("TOR")
    assert actual == expected

# With pytest-clarity (much clearer!):
    def test_team_score():
        expected = {...}
        actual = get_team_score("TOR")
>       assert actual == expected
E       AssertionError: assert actual == expected
E
E       Dict difference:
E
E         {
E           'conference': 'Eastern',
E           'division': 'Atlantic',
E           'players': [
E             {'firstName': 'Auston', 'lastName': 'Matthews', 'score': 156},
E             {'firstName': 'Mitch', 'lastName': 'Marner', 'score': 145},
E       -     {'firstName': 'William', 'lastName': 'Nylander', 'score': 138},  ← Expected
E       +     {'firstName': 'William', 'lastName': 'Nylander', 'score': 139},  ← Actual
E           ],
E           'team_abbrev': 'TOR',
E       -   'total_score': 1234,  ← Expected
E       +   'total_score': 1235,  ← Actual
E         }
```

**Differences are immediately obvious:**

- Only changed lines shown with - and +
- Unchanged lines shown once (not duplicated)
- Colors: Red for expected (-), Green for actual (+)
- Annotations show which is which
- Much easier to scan and identify the issue!

**Step 4: Works with all assertion types**:

```python
# String differences
assert "Hello World" == "Hello Wurld"
# pytest-clarity shows character-by-character diff with colors

# List differences
assert [1, 2, 3, 4] == [1, 2, 5, 4]
# pytest-clarity highlights index 2: 3 vs 5

# Complex nested structures
assert nested_dict == other_nested_dict
# pytest-clarity shows tree-like diff with path to changes
```

**Step 5: Configuration options** (optional):

```toml
# pyproject.toml (optional, defaults are good)
[tool.pytest.ini_options]
# pytest-clarity respects standard pytest options
# No special configuration needed

# To disable for specific test (rare):
# Use pytest.raises() or custom comparison
```

## Implementation Steps

1. **Add pytest-clarity to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.test]`
   - Add `pytest-clarity>=1.0.1`

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Test locally**:

   - Create a failing test to verify output
   - Run `pytest` and observe enhanced diff
   - Verify colors display correctly
   - Check nested structure formatting

1. **Test with existing tests**:

   - Run `pytest` on all tests
   - Verify any failures show enhanced diffs
   - Check no conflicts with other plugins

1. **Verify CI compatibility**:

   - pytest-clarity works in CI (no special handling needed)
   - Colors may be disabled in non-interactive terminals
   - Diffs still readable without colors

1. **Document usage**:

   - Add to CONTRIBUTING.md
   - Note automatic activation
   - Document how to disable if needed

## Testing Strategy

**Manual Verification** (create test that fails):

```python
# tests/test_clarity_verification.py (temporary, for verification)
def test_clarity_dict_diff():
    """Verify pytest-clarity enhances dict diffs."""
    expected = {
        "team": "TOR",
        "score": 100,
        "players": ["Matthews", "Marner"],
    }
    actual = {
        "team": "TOR",
        "score": 105,
        "players": ["Matthews", "Nylander"],
    }
    assert actual == expected  # This will fail, showing enhanced diff

def test_clarity_string_diff():
    """Verify pytest-clarity enhances string diffs."""
    assert "Hello World" == "Hello Wurld"  # Character-level diff

def test_clarity_list_diff():
    """Verify pytest-clarity enhances list diffs."""
    assert [1, 2, 3, 4] == [1, 2, 5, 4]  # Index-level diff

# Run and verify output:
# pytest tests/test_clarity_verification.py -v
#
# Should show:
# - Enhanced diffs with colors
# - Only changed parts highlighted
# - Clear indication of expected vs actual
#
# After verification, delete this file
```

**Compatibility Testing**:

```bash
# Test with other plugins
pytest --cov  # With coverage
pytest -n auto  # With parallel execution
pytest -v  # With pytest-sugar

# All should work together
```

**CI Testing**:

```bash
# In CI (non-interactive terminal):
pytest
# Diffs shown without colors (still readable)
```

## Acceptance Criteria

- [ ] pytest-clarity added to `[project.optional-dependencies.test]`
- [ ] Lock file updated with pytest-clarity
- [ ] Assertion failures show enhanced diffs
- [ ] Changed values highlighted (colors in terminal)
- [ ] Nested structures formatted clearly
- [ ] Unchanged lines not duplicated in diff
- [ ] Works with dictionaries, lists, strings, objects
- [ ] Compatible with pytest-cov (coverage)
- [ ] Compatible with pytest-xdist (parallel)
- [ ] Compatible with pytest-sugar (output formatting)
- [ ] CI output readable (with or without colors)
- [ ] Can be disabled if needed (standard pytest options)
- [ ] Documentation updated (CONTRIBUTING.md)

## Related Files

- `pyproject.toml` - Add pytest-clarity dependency
- `CONTRIBUTING.md` - Document enhanced diff output
- `uv.lock` - Updated with pytest-clarity
- `tests/**/*.py` - All tests (benefit from enhanced diffs on failure)

## Dependencies

**Recommended implementation order**:

- Implement after pytest-sugar (task 004)
- Works with all existing pytest plugins
- Independent enhancement (no blocking dependencies)

**No blocking dependencies** - Can be implemented independently

## Additional Notes

**Why pytest-clarity?**

- **Faster debugging**: Immediately see what's different
- **Better diffs**: Smart algorithms for complex structures
- **Less noise**: Only show what changed
- **Visual clarity**: Color coding and formatting
- **Zero config**: Works out of the box
- **Professional**: Better developer experience

**How pytest-clarity Works**:

```
Standard pytest assertion rewriting:
  1. Capture assertion failure
  2. Show entire expected value
  3. Show entire actual value
  4. Show basic text diff (line-by-line)

pytest-clarity enhancements:
  1. Capture assertion failure
  2. Analyze structure (dict, list, string, object)
  3. Compute smart diff (only changes)        ← Enhanced
  4. Format with colors and highlighting      ← Enhanced
  5. Show context around changes              ← Enhanced
  6. Annotate expected vs actual              ← Enhanced
```

**Diff Algorithm Comparison**:

| Aspect                | Standard pytest | With pytest-clarity    |
| --------------------- | --------------- | ---------------------- |
| **Dict diffs**        | Full dict twice | Only changed keys      |
| **List diffs**        | Full list twice | Only changed items     |
| **String diffs**      | Line-by-line    | Character-by-character |
| **Nested structures** | Flat comparison | Tree-like with paths   |
| **Colors**            | ❌ No           | ✅ Yes (red/green)     |
| **Annotations**       | ❌ No           | ✅ Yes (←)             |

**Visual Example - Dictionary**:

Standard pytest:

```
E       AssertionError: assert {'a': 1, 'b': 2, 'c': 3} == {'a': 1, 'b': 5, 'c': 3}
E
E       Full diff:
E       - {'a': 1, 'b': 2, 'c': 3}
E       + {'a': 1, 'b': 5, 'c': 3}
```

pytest-clarity:

```
E       AssertionError: assert actual == expected
E
E       Dict difference:
E         {
E           'a': 1,
E       -   'b': 2,  ← Expected
E       +   'b': 5,  ← Actual
E           'c': 3,
E         }
```

Much clearer! Only the different key is highlighted.

**Visual Example - Nested Structure**:

```python
# Complex nested structure
expected = {
    "team": "TOR",
    "players": [
        {"name": "Matthews", "stats": {"goals": 40, "assists": 30}},
        {"name": "Marner", "stats": {"goals": 25, "assists": 60}},
    ],
}

actual = {
    "team": "TOR",
    "players": [
        {"name": "Matthews", "stats": {"goals": 40, "assists": 30}},
        {"name": "Marner", "stats": {"goals": 25, "assists": 65}},  # Different
    ],
}

assert actual == expected
```

pytest-clarity output:

```
E       Dict difference at players[1].stats:
E         {
E           'goals': 25,
E       -   'assists': 60,  ← Expected
E       +   'assists': 65,  ← Actual
E         }
```

Shows the exact path to the difference: `players[1].stats.assists`!

**String Diff Example**:

```python
assert "Hello World" == "Hello Wurld"
```

pytest-clarity:

```
E       String difference:
E       - Hello World
E       + Hello Wurld
E               ^^
E       Character difference at index 7-8: 'o' → 'u'
```

Character-level precision!

**Compatibility Matrix**:

✅ **Works with**:

- pytest-cov (coverage collection)
- pytest-xdist (parallel execution)
- pytest-randomly (random order)
- pytest-timeout (timeouts)
- pytest-sugar (output formatting)
- pytest-mock (mocking)
- All standard pytest features

⚠️ **May conflict with**:

- Custom assertion rewriting (rare)
- Other diff enhancement plugins (choose one)

**Disabling pytest-clarity**:

```bash
# Method 1: Command line flag
pytest -p no:clarity

# Method 2: pytest.ini (not recommended)
[tool.pytest.ini_options]
addopts = ["-p", "no:clarity"]

# Method 3: For specific assertion (use custom comparison)
def test_without_clarity():
    # Use pytest.raises() or manual comparison
    pass
```

**Performance Impact**:

- Negligible overhead for passing tests
- Slightly slower diff computation for failing tests (\<50ms)
- Worth it for the improved clarity

**CI Environment Handling**:

```python
# pytest-clarity detects CI automatically:
import sys

if not sys.stdout.isatty():
    # Non-interactive terminal - disable colors
    use_colors = False
else:
    # Interactive terminal - use colors
    use_colors = True

# Diffs still enhanced, just without colors in CI
```

**Best Practices**:

```bash
# ✅ Good: Use clarity for all tests
pytest  # Enhanced diffs help debug failures quickly

# ✅ Good: Keep it enabled in CI
# Diffs still helpful even without colors

# ✅ Good: Use with pytest-sugar
# Both enhance output in complementary ways

# ❌ Bad: Disabling clarity globally
# Defeats the purpose

# ❌ Bad: Only using for specific tests
# You want enhanced diffs for ALL failures
```

**When pytest-clarity Helps Most**:

1. **API Response Testing**:

   ```python
   # Large JSON responses
   assert api_response == expected_response
   # Clarity shows exactly which fields differ
   ```

1. **Data Model Validation**:

   ```python
   # Pydantic models, dataclasses
   assert actual_model == expected_model
   # Clarity shows which fields mismatch
   ```

1. **Database Query Results**:

   ```python
   # Complex query results
   assert db_result == expected_result
   # Clarity highlights data differences
   ```

1. **Configuration Testing**:

   ```python
   # Nested config dicts
   assert loaded_config == expected_config
   # Clarity shows config path to difference
   ```

**Common Questions**:

**Q: Will this break CI?**
A: No, pytest-clarity works in CI, just without colors.

**Q: Can I disable it?**
A: Yes, `pytest -p no:clarity`, but why would you?

**Q: Does it work with all assertion types?**
A: Yes, dicts, lists, strings, objects, primitives.

**Q: Will it slow down tests?**
A: No, only affects failing tests, overhead \<50ms.

**Q: Does it work with pytest-sugar?**
A: Yes, they complement each other perfectly.

**Q: Can I customize the diff format?**
A: pytest-clarity uses sensible defaults (not customizable).

## Implementation Notes

*To be filled during implementation:*

- Developer feedback on enhanced diffs
- Any compatibility issues encountered
- Performance impact measured (should be \<50ms)
- Examples of particularly helpful diffs
- Screenshots of enhanced output (optional)
