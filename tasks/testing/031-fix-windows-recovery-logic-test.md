# Fix Windows Test Failure: test_list_continues_after_individual_error

**GitHub Issue**: #537 - https://github.com/bdperkin/nhl-scrabble/issues/537

## Priority

**MEDIUM** - Platform Support

## Estimated Effort

2-3 hours

## Description

Fix test_historical_storage.py::TestRecoveryLogic::test_list_continues_after_individual_error failing on Windows. Test expects an empty list but gets `['20222023']`, indicating different error handling behavior on Windows compared to Unix.

## Current State

**Test failing on Windows:**
```
FAILED tests/unit/test_historical_storage.py::TestRecoveryLogic::test_list_continues_after_individual_error
AssertionError: assert ['20222023'] == []
```

**Affected Platforms:**
- Windows (all Python versions: 3.12, 3.13, 3.14)
- Ubuntu/macOS: ✅ Passing (returns empty list as expected)

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Made non-blocking in PR #532 to prevent false CI failures

## Root Cause Analysis

**Likely Causes:**

1. **Related to permission test failures** (issue #535):
   - Test may use `chmod` to simulate errors
   - Windows ignores `chmod` permission changes
   - File remains accessible on Windows, gets listed
   - Unix blocks access, file not listed

2. **Different error handling:**
   - Test expects certain errors to prevent listing
   - Windows doesn't raise those errors (permissions)
   - Data gets listed that shouldn't be

3. **File system behavior:**
   - Directory iteration works differently
   - Permission checks happen at different points
   - Windows may continue where Unix fails

## Investigation Steps

### Step 1: Read the Test

```bash
# Examine test implementation
grep -A 30 "def test_list_continues_after_individual_error" tests/unit/test_historical_storage.py
```

**Key questions:**
- What error scenario is being simulated?
- Does it use `chmod` for permissions?
- What should trigger the "individual error"?
- Why should the list be empty?

### Step 2: Check Test Logic

```python
def test_list_continues_after_individual_error(self):
    """Test listing continues even if individual files have errors."""
    # Likely creates some files
    # Makes one file unreadable (chmod 0o000?)
    # Expects list to skip unreadable file
    # But Windows file is still readable → shows up in list
```

### Step 3: Verify Related Permission Code

This test is likely related to the permission tests that also fail on Windows.

## Proposed Solution

### Option 1: Skip on Windows (If Permission-Related)

If test uses `chmod` to simulate errors:

```python
import sys
import pytest

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows doesn't support Unix-style chmod permissions (uses ACLs)"
)
def test_list_continues_after_individual_error(self):
    """Test listing continues even if individual files have errors.

    Note: Skipped on Windows as it uses chmod to simulate permission errors,
    which doesn't work the same on Windows due to ACL-based permissions.
    """
    # Existing test logic
    pass
```

### Option 2: Platform-Specific Expectations

If test can run on Windows with different expectations:

```python
import sys

def test_list_continues_after_individual_error(self):
    """Test listing continues even if individual files have errors."""
    # Setup: create files, make one problematic

    if sys.platform == "win32":
        # Windows: file is still accessible, should appear in list
        expected_seasons = ["20222023"]
    else:
        # Unix: file inaccessible due to chmod, should be skipped
        expected_seasons = []

    result = store.list_seasons()
    assert result == expected_seasons
```

### Option 3: Mock Errors on Windows

Use mocking to simulate errors instead of relying on `chmod`:

```python
import sys
from unittest.mock import patch

def test_list_continues_after_individual_error(self):
    """Test listing continues even if individual files have errors."""
    if sys.platform == "win32":
        # Mock permission error on Windows
        with patch("pathlib.Path.exists", side_effect=PermissionError):
            result = store.list_seasons()
            assert result == []
    else:
        # Use real chmod on Unix
        os.chmod(problem_file, 0o000)
        result = store.list_seasons()
        assert result == []
        os.chmod(problem_file, 0o644)
```

## Implementation Steps

1. **Read test implementation** to understand error simulation:
   ```bash
   cat tests/unit/test_historical_storage.py | grep -A 50 "test_list_continues_after_individual_error"
   ```

2. **Identify error simulation method**:
   - Uses `chmod`? → Skip on Windows (like task #029)
   - Uses other method? → May need different fix

3. **Check if related to task #029**:
   - If uses `chmod` for permissions
   - Likely needs same fix (skip on Windows)

4. **Choose appropriate fix**:
   - **If permission-related**: Skip on Windows
   - **If adaptable**: Platform-specific expectations
   - **If mockable**: Add Windows-specific mocking

5. **Implement fix** based on investigation

6. **Test on all platforms**:
   - Windows: Either skipped or passes with adjusted expectations
   - Unix: Still passes with original expectations

## Testing Strategy

**Investigation:**
```bash
# Read the test
pytest tests/unit/test_historical_storage.py::TestRecoveryLogic::test_list_continues_after_individual_error -v --tb=long

# Run with verbose output to see what's happening
pytest tests/unit/test_historical_storage.py::TestRecoveryLogic::test_list_continues_after_individual_error -v -s
```

**After Fix:**
```bash
# Run specific test
pytest tests/unit/test_historical_storage.py::TestRecoveryLogic::test_list_continues_after_individual_error -v

# Run all recovery logic tests
pytest tests/unit/test_historical_storage.py::TestRecoveryLogic -v

# Run all historical storage tests
pytest tests/unit/test_historical_storage.py -v
```

**CI Testing:**
- Windows-latest (Python 3.12, 3.13, 3.14)
- Ubuntu-latest (verify no regression)
- macOS-latest (verify no regression)

## Acceptance Criteria

- [ ] Test passes or is appropriately skipped on Windows
- [ ] Test still passes on Ubuntu with original behavior
- [ ] Test still passes on macOS with original behavior
- [ ] Fix is consistent with approach used in task #029 (if permission-related)
- [ ] Docstring explains Windows behavior difference
- [ ] No new test failures introduced

## Related Files

- `tests/unit/test_historical_storage.py` - Test file (TestRecoveryLogic class)
- `src/nhl_scrabble/storage/historical.py` - Production code (list_seasons method)
- `.github/workflows/nightly.yml` - Workflow (Windows experimental flag)

## Dependencies

**Investigation dependency:**
- Must read test implementation first to determine fix approach

**Possible code dependency:**
- Task #029 (Windows permission tests) - likely uses similar approach

## Related Issues

- **#535** (Task #029): Windows permission test failures - **LIKELY RELATED**
  - If this test uses `chmod`, same fix applies
  - Should use consistent approach
- #533: test_search_to_file (Windows file handling)
- #534: test_success_messages_translatable (Windows i18n)
- #536: test_save_season_unicode_data (Windows encoding)

## Additional Notes

**Test Name Analysis:**
- "list_continues_after_individual_error" suggests error handling during iteration
- "individual error" implies some items fail but others succeed
- Empty list expectation suggests all items should fail to list
- Windows returning data suggests errors aren't happening

**Common Patterns:**
- Unix permission errors prevent file access
- Windows permissions work differently
- Tests simulating Unix errors don't work on Windows

**Investigation Priority:**
1. Read test to confirm it uses `chmod`
2. If yes → Same fix as task #029 (skip on Windows)
3. If no → Investigate actual error mechanism
4. Determine if Windows behavior is acceptable

**Coordination with Task #029:**
- If both use `chmod`, can fix together
- Use same skip pattern
- Update same test file
- One PR can fix both

## Implementation Notes

*To be filled during implementation:*
- Test implementation reviewed (uses chmod? other error method?)
- Root cause confirmed
- Fix approach chosen (skip vs adapt vs mock)
- Relationship to task #029 confirmed
- Files modified
- Test results on all platforms
- Date of fix completion
