# Fix Windows Test Failure: test_search_to_file

**GitHub Issue**: #533 - https://github.com/bdperkin/nhl-scrabble/issues/533

## Priority

**MEDIUM** - Platform Support

## Estimated Effort

2-4 hours

## Description

Fix test_cli_comprehensive.py::TestOtherCommands::test_search_to_file failing on Windows. The test expects exit code 0 but gets exit code 1, indicating a command failure specific to Windows platform.

## Current State

**Test failing on Windows:**
```
FAILED tests/unit/test_cli_comprehensive.py::TestOtherCommands::test_search_to_file - assert 1 == 0
```

**Affected Platforms:**
- Windows (all Python versions: 3.12, 3.13, 3.14)
- Ubuntu/macOS: ✅ Passing

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Made non-blocking in PR #532 to prevent false CI failures

## Root Cause Analysis

Likely Windows-specific issues:
1. **Path separator differences**: Windows uses backslashes (`\`), Unix uses forward slashes (`/`)
2. **File path handling**: Different absolute path formats (`C:\path` vs `/path`)
3. **Temporary file creation**: Windows temp directory handling differs
4. **Line endings**: CRLF vs LF may affect file content comparison

## Proposed Solution

### Investigation Steps

1. **Read the test implementation**:
   ```bash
   # Examine test logic
   cat tests/unit/test_cli_comprehensive.py | grep -A 30 "def test_search_to_file"
   ```

2. **Check file path handling**:
   - Review how output file path is constructed
   - Verify path normalization using `os.path.normpath()` or `pathlib.Path`
   - Check if absolute paths are correctly handled on Windows

3. **Review CLI search command**:
   ```bash
   # Check search implementation
   grep -r "def search" src/nhl_scrabble/cli.py
   ```

### Potential Fixes

**Option 1: Normalize file paths**
```python
import os
from pathlib import Path

# In test or CLI code
output_path = Path(output_file).resolve()  # Cross-platform path handling
```

**Option 2: Use platform-specific temp directories**
```python
import tempfile

# Instead of hardcoded paths
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    output_file = f.name
```

**Option 3: Platform-specific test expectations**
```python
import sys
import pytest

@pytest.mark.skipif(sys.platform == "win32", reason="Path handling differs on Windows")
def test_search_to_file():
    # Existing test logic
    pass

# Or adapt the test
def test_search_to_file():
    if sys.platform == "win32":
        # Windows-specific expectations
        expected_path = Path("C:/...").as_posix()
    else:
        expected_path = "/..."
```

## Implementation Steps

1. **Reproduce locally** (if Windows environment available):
   ```bash
   pytest tests/unit/test_cli_comprehensive.py::TestOtherCommands::test_search_to_file -v
   ```

2. **Add debugging to test**:
   ```python
   import sys
   print(f"Platform: {sys.platform}")
   print(f"Output file: {output_file}")
   print(f"Exit code: {result.exit_code}")
   print(f"Output: {result.output}")
   ```

3. **Implement fix** based on findings:
   - Update file path handling in CLI code
   - Or update test to handle Windows paths
   - Or skip test on Windows if truly platform-specific

4. **Verify fix**:
   - Test on Windows (via GitHub Actions or local Windows VM)
   - Ensure Ubuntu/macOS still pass
   - Run full test suite to check for regressions

5. **Update nightly workflow** (make Windows tests blocking again):
   - Remove experimental flag from Windows tests in `.github/workflows/nightly.yml`
   - Once all Windows tests pass

## Testing Strategy

**Local Testing:**
```bash
# Run specific test
pytest tests/unit/test_cli_comprehensive.py::TestOtherCommands::test_search_to_file -v

# Run all CLI tests
pytest tests/unit/test_cli_comprehensive.py -v

# Run on all platforms (via CI)
git push origin feature/fix-windows-test-search
```

**GitHub Actions Testing:**
- Windows-latest (Python 3.12, 3.13, 3.14)
- Ubuntu-latest (verify no regression)
- macOS-latest (verify no regression)

## Acceptance Criteria

- [ ] Test passes on Windows (Python 3.12, 3.13, 3.14)
- [ ] Test still passes on Ubuntu
- [ ] Test still passes on macOS
- [ ] No new test failures introduced
- [ ] File path handling is cross-platform compatible
- [ ] Code uses `pathlib.Path` or `os.path` for portability
- [ ] Documentation updated if test behavior changes

## Related Files

- `tests/unit/test_cli_comprehensive.py` - Test file containing failing test
- `src/nhl_scrabble/cli.py` - CLI implementation (search command)
- `.github/workflows/nightly.yml` - Workflow (Windows experimental flag)

## Dependencies

None - standalone bug fix

## Related Issues

- #534: test_success_messages_translatable (Windows i18n test)
- #535: Windows permission test failures (5 tests)
- #536: test_save_season_unicode_data (Windows encoding)
- #537: test_list_continues_after_individual_error (Windows)

## Additional Notes

**Platform Testing Resources:**
- GitHub Actions provides Windows runners for free
- Can test locally with Windows VM or WSL (with limitations)
- Cross-platform path handling best practices: use `pathlib.Path`

**Best Practices:**
- Always use `pathlib.Path` for cross-platform compatibility
- Avoid hardcoded path separators (`/` or `\`)
- Use `os.path.join()` or `Path.joinpath()` for path construction
- Test on all target platforms before marking as complete

## Implementation Notes

*To be filled during implementation:*
- Root cause identified
- Fix approach chosen
- Files modified
- Test results on all platforms
- Date of fix completion
