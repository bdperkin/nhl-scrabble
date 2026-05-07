# Fix Windows Permission Test Failures in test_historical_storage.py

**GitHub Issue**: #535 - https://github.com/bdperkin/nhl-scrabble/issues/535

## Priority

**MEDIUM** - Platform Support / Test Coverage

## Estimated Effort

4-6 hours

## Description

Fix 5 permission-related test failures on Windows in test_historical_storage.py. All tests fail because Windows doesn't respect `chmod` permissions the same way as Unix systems, causing tests that expect PermissionError to never raise the exception.

## Current State

**5 Tests failing on Windows:**
```
FAILED tests/unit/test_historical_storage.py::TestLoadSeasonEdgeCases::test_load_season_permission_denied
FAILED tests/unit/test_historical_storage.py::TestErrorMessages::test_save_error_message_includes_season
FAILED tests/unit/test_historical_storage.py::TestHistoricalDataStoreInit::test_init_directory_creation_permission_error
FAILED tests/unit/test_historical_storage.py::TestSaveSeasonEdgeCases::test_save_season_write_fails_permission_denied
FAILED tests/unit/test_historical_storage.py::TestRecoveryLogic::test_load_after_save_failure
```

**Error:**
```
Failed: DID NOT RAISE <class 'nhl_scrabble.exceptions.HistoricalDataStoreError'>
```

**Affected Platforms:**
- Windows (all Python versions: 3.12, 3.13, 3.14)
- Ubuntu/macOS: ✅ Passing

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Made non-blocking in PR #532 to prevent false CI failures

## Root Cause Analysis

**Windows chmod Behavior:**
- Unix: `os.chmod(path, 0o000)` makes file/directory inaccessible → PermissionError
- Windows: `os.chmod(path, 0o000)` only affects read/write attributes, NOT permissions
- Windows uses Access Control Lists (ACLs), not Unix-style permissions
- Tests using `chmod` to simulate permission errors don't work on Windows

**Example failing test pattern:**
```python
# This works on Unix but NOT on Windows
os.chmod(file_path, 0o000)  # Remove all permissions
with open(file_path, 'r') as f:  # Expects PermissionError
    data = f.read()  # On Windows: still works! No error raised
```

## Proposed Solution

### Recommended Approach: Skip on Windows

**Why skip:**
- Simulating Unix permission behavior on Windows is complex
- Tests verify Unix permission handling, which doesn't apply to Windows
- Production code works correctly on Windows (just can't be tested the same way)
- Windows ACL testing would require completely different test logic

**Implementation:**
```python
import sys
import pytest

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows doesn't support Unix-style chmod permissions (uses ACLs)"
)
class TestLoadSeasonEdgeCases:
    def test_load_season_permission_denied(self):
        # Existing test logic
        os.chmod(season_file, 0o000)
        with pytest.raises(HistoricalDataStoreError):
            store.load_season("20222023")
```

### Alternative Approach: Mock PermissionError

If skipping is not acceptable, mock the file operations:

```python
import sys
from unittest.mock import patch, mock_open

def test_load_season_permission_denied(self):
    """Test permission denied error handling."""
    if sys.platform == "win32":
        # On Windows: mock the permission error
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(HistoricalDataStoreError, match="permission"):
                store.load_season("20222023")
    else:
        # On Unix: use real chmod
        os.chmod(season_file, 0o000)
        with pytest.raises(HistoricalDataStoreError):
            store.load_season("20222023")
        os.chmod(season_file, 0o644)  # Restore
```

### Alternative Approach: Windows ACL Testing

Most complex but most accurate for Windows:

```python
import sys

if sys.platform == "win32":
    import win32security
    import ntsecuritycon

    def remove_windows_permissions(path):
        """Remove Windows ACL permissions."""
        # Get current security descriptor
        sd = win32security.GetFileSecurity(
            path, win32security.DACL_SECURITY_INFORMATION
        )
        # Create empty DACL (no access for anyone)
        dacl = win32security.ACL()
        # Set the new DACL
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(
            path, win32security.DACL_SECURITY_INFORMATION, sd
        )
```

**Note:** This requires `pywin32` dependency, which is not currently in the project.

## Implementation Steps

### Option 1: Skip Tests (Recommended)

1. **Add skip decorator to affected test classes/methods**:
   ```python
   import sys
   import pytest

   @pytest.mark.skipif(sys.platform == "win32", reason="Windows ACL permissions differ from Unix")
   class TestLoadSeasonEdgeCases:
       # All tests in class will be skipped on Windows
       pass
   ```

2. **Or skip individual tests**:
   ```python
   @pytest.mark.skipif(sys.platform == "win32", reason="Windows ACL permissions differ from Unix")
   def test_load_season_permission_denied(self):
       # Test logic
       pass
   ```

3. **List all affected tests**:
   - `TestLoadSeasonEdgeCases::test_load_season_permission_denied`
   - `TestErrorMessages::test_save_error_message_includes_season`
   - `TestHistoricalDataStoreInit::test_init_directory_creation_permission_error`
   - `TestSaveSeasonEdgeCases::test_save_season_write_fails_permission_denied`
   - `TestRecoveryLogic::test_load_after_save_failure`

4. **Add docstring notes**:
   ```python
   def test_load_season_permission_denied(self):
       """Test permission denied error handling.

       Note: Skipped on Windows as it uses ACL permissions instead of
       Unix-style chmod. The production code handles Windows permissions
       correctly; this test specifically validates Unix permission behavior.
       """
   ```

5. **Verify tests still pass on Unix**:
   ```bash
   pytest tests/unit/test_historical_storage.py -v
   ```

6. **Verify tests are skipped on Windows**:
   - Check GitHub Actions Windows workflow logs
   - Should show: `SKIPPED [1] test_historical_storage.py:123: Windows ACL permissions differ from Unix`

### Option 2: Mock PermissionError (If skip not acceptable)

1. **Add platform-specific logic to each test**
2. **Mock file operations on Windows**
3. **Keep real chmod testing on Unix**
4. **More complex but tests still run on Windows**

## Testing Strategy

**Local Testing (Unix):**
```bash
# Run all permission tests
pytest tests/unit/test_historical_storage.py::TestLoadSeasonEdgeCases -v
pytest tests/unit/test_historical_storage.py::TestErrorMessages -v
pytest tests/unit/test_historical_storage.py::TestHistoricalDataStoreInit -v
pytest tests/unit/test_historical_storage.py::TestSaveSeasonEdgeCases -v
pytest tests/unit/test_historical_storage.py::TestRecoveryLogic -v

# Verify tests still pass
pytest tests/unit/test_historical_storage.py -v
```

**Windows Testing:**
```bash
# Verify tests are skipped (not failed)
pytest tests/unit/test_historical_storage.py -v
# Should show: "5 skipped" for permission tests

# Check skip reason is displayed
pytest tests/unit/test_historical_storage.py -v -rs
```

**CI Testing:**
- Windows-latest: Verify 5 tests skipped
- Ubuntu-latest: Verify 5 tests pass
- macOS-latest: Verify 5 tests pass

## Acceptance Criteria

- [ ] Tests no longer fail on Windows (skipped or mocked)
- [ ] Tests still pass on Ubuntu
- [ ] Tests still pass on macOS
- [ ] Skip reason clearly documented in code
- [ ] Test coverage maintained (skipped tests don't reduce coverage on Windows)
- [ ] No new test failures introduced
- [ ] Docstrings explain Windows skip reason

## Related Files

- `tests/unit/test_historical_storage.py` - Test file with 5 failing tests
- `src/nhl_scrabble/storage/historical.py` - Production code (works correctly on Windows)
- `.github/workflows/nightly.yml` - Workflow (Windows experimental flag)

## Dependencies

None - standalone bug fix

## Related Issues

- #533: test_search_to_file (Windows file handling)
- #534: test_success_messages_translatable (Windows i18n)
- #536: test_save_season_unicode_data (Windows encoding)
- #537: test_list_continues_after_individual_error (Windows, may be related to permissions)

## Additional Notes

**Windows vs Unix Permissions:**
- Unix uses simple permission bits (rwxrwxrwx)
- Windows uses Access Control Lists (ACLs) with complex security descriptors
- `os.chmod()` on Windows only affects read-only attribute, not access control
- Testing permission errors on Windows requires different approach

**Why Production Code Works:**
- Windows file operations raise PermissionError when ACLs deny access
- Production code handles PermissionError correctly regardless of how it's triggered
- Tests verify Unix permission simulation, not Windows ACL behavior

**Test Coverage Impact:**
- Skipping tests on Windows reduces platform-specific coverage
- But testing Unix permission behavior on Windows is meaningless
- Windows ACL testing would require separate tests with different logic

**Best Practices:**
- Skip platform-specific tests when behavior fundamentally differs
- Document why tests are skipped in code comments
- Consider platform-specific tests if behavior needs verification
- Don't use `chmod` to simulate permissions on Windows

**Similar Issues in Other Projects:**
- pytest itself skips many Unix permission tests on Windows
- Common practice to skip Unix-specific permission tests
- Some projects use conditional logic; others skip entirely

## Implementation Notes

*To be filled during implementation:*
- Approach chosen (skip vs mock vs ACL)
- Number of tests modified
- Skip decorator added to which classes/methods
- Verification on all platforms
- Date of fix completion
