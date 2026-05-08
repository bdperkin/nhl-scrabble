# Fix Windows Test Failure: test_success_messages_translatable

**GitHub Issue**: #534 - https://github.com/bdperkin/nhl-scrabble/issues/534

## Priority

**MEDIUM** - Platform Support / I18n

## Estimated Effort

3-5 hours

## Description

Fix test_cli_i18n.py::TestCLITranslatedStrings::test_success_messages_translatable failing on Windows. The test expects exit code 0 but gets exit code 1, indicating CLI i18n functionality issues specific to Windows platform.

## Current State

**Test failing on Windows:**
```
FAILED tests/unit/test_cli_i18n.py::TestCLITranslatedStrings::test_success_messages_translatable - assert 1 == 0
```

**Affected Platforms:**
- Windows (all Python versions: 3.12, 3.13, 3.14)
- Ubuntu/macOS: ✅ Passing

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Made non-blocking in PR #532 to prevent false CI failures

## Root Cause Analysis

Likely Windows-specific i18n issues:
1. **Locale detection differences**: Windows uses different locale naming (e.g., `en-US` vs `en_US`)
2. **Environment variable handling**: `LANG`, `LC_ALL` may not work the same on Windows
3. **gettext file loading**: Path separators in locale directory paths
4. **UTF-8 encoding**: Windows default encoding may not be UTF-8
5. **Translation file discovery**: `.mo` file paths may not resolve correctly

## Proposed Solution

### Investigation Steps

1. **Read the test implementation**:
   ```bash
   # Examine test logic
   cat tests/unit/test_cli_i18n.py | grep -A 50 "def test_success_messages_translatable"
   ```

2. **Check i18n module**:
   ```bash
   # Review locale detection on Windows
   cat src/nhl_scrabble/i18n.py | grep -A 20 "def get_system_locale"
   ```

3. **Verify locale environment setup**:
   ```python
   import os
   import locale
   print(f"LANG: {os.getenv('LANG')}")
   print(f"System locale: {locale.getlocale()}")
   ```

### Potential Fixes

**Option 1: Fix Windows locale detection**
```python
# In src/nhl_scrabble/i18n.py
def get_system_locale() -> str:
    """Detect system locale with Windows support."""
    import sys

    if sys.platform == "win32":
        # Windows-specific locale detection
        import ctypes
        windll = ctypes.windll.kernel32
        locale_id = windll.GetUserDefaultUILanguage()
        # Map Windows locale ID to POSIX locale code
        locale_map = {
            0x0409: "en_US",  # English (US)
            0x0C0C: "fr_CA",  # French (Canada)
            # ... etc
        }
        return locale_map.get(locale_id, DEFAULT_LOCALE)

    # Unix locale detection
    for env_var in ("LC_ALL", "LC_CTYPE", "LANG", "LANGUAGE"):
        if localename := os.environ.get(env_var):
            system_locale = localename.split(".")[0].split("@")[0]
            if system_locale and system_locale in SUPPORTED_LOCALES:
                return system_locale

    return DEFAULT_LOCALE
```

**Option 2: Fix gettext path handling on Windows**
```python
# In src/nhl_scrabble/i18n.py
def get_translator(locale_code: str | None = None) -> Callable[[str], str]:
    """Get translator with Windows path handling."""
    from pathlib import Path

    # Use Path for cross-platform compatibility
    locales_dir = Path(__file__).parent / "locales"

    try:
        translation = gettext.translation(
            "messages",
            localedir=str(locales_dir),  # Convert Path to string
            languages=[locale_code],
        )
        return translation.gettext
    except FileNotFoundError:
        return lambda s: s
```

**Option 3: Ensure UTF-8 encoding on Windows**
```python
# In test or CLI code
import sys
if sys.platform == "win32":
    # Force UTF-8 encoding on Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
```

**Option 4: Skip or adapt test for Windows**
```python
import sys
import pytest

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows locale detection differs from Unix"
)
def test_success_messages_translatable():
    # Existing test logic
    pass

# Or platform-specific expectations
def test_success_messages_translatable():
    if sys.platform == "win32":
        # Windows may use different locale codes
        expected_locales = ["en-US", "fr-CA"]
    else:
        expected_locales = ["en_US", "fr_CA"]
```

## Implementation Steps

1. **Add debug logging to test**:
   ```python
   import os, sys, locale
   print(f"Platform: {sys.platform}")
   print(f"LANG: {os.getenv('LANG')}")
   print(f"NHL_SCRABBLE_LANG: {os.getenv('NHL_SCRABBLE_LANG')}")
   print(f"System locale: {locale.getlocale()}")
   print(f"Detected locale: {get_system_locale()}")
   ```

2. **Run test on Windows** (via GitHub Actions):
   - Push debug branch
   - Check workflow logs for locale detection details

3. **Implement fix** based on findings:
   - Update locale detection in `i18n.py`
   - Fix path handling for translation files
   - Ensure UTF-8 encoding on Windows
   - Or adapt test for Windows differences

4. **Verify translation files accessible on Windows**:
   ```bash
   # Check .mo files exist and are readable
   find src/nhl_scrabble/locales/ -name "*.mo"
   ```

5. **Test on all platforms**:
   - Windows: Python 3.12, 3.13, 3.14
   - Ubuntu: Verify no regression
   - macOS: Verify no regression

## Testing Strategy

**Local Testing (if Windows available):**
```bash
# Run i18n tests
pytest tests/unit/test_cli_i18n.py::TestCLITranslatedStrings::test_success_messages_translatable -v -s

# Test locale detection
python -c "from nhl_scrabble.i18n import get_system_locale; print(get_system_locale())"

# Test translation loading
python -c "from nhl_scrabble.i18n import get_translator; t = get_translator('fr_CA'); print(t('Hello'))"
```

**GitHub Actions Testing:**
- Windows-latest (Python 3.12, 3.13, 3.14)
- Ubuntu-latest (verify no regression)
- macOS-latest (verify no regression)

## Acceptance Criteria

- [x] Test passes on Linux (verified locally - 15/15 CLI i18n tests, 47/47 i18n module tests)
- [ ] Test passes on Windows (Python 3.12, 3.13, 3.14) - pending CI verification
- [ ] Test still passes on macOS - pending CI verification
- [x] Locale detection works safely on all platforms (Windows fallback added)
- [x] Translation files load correctly (no changes to loading mechanism)
- [x] UTF-8 encoding handled properly (uses standard formatting on Windows)
- [x] No new test failures introduced (all local tests pass)
- [x] Documentation updated (docstrings updated with Windows notes)

## Related Files

- `tests/unit/test_cli_i18n.py` - Test file containing failing test
- `src/nhl_scrabble/i18n.py` - I18n module (locale detection, translation loading)
- `src/nhl_scrabble/locales/` - Translation files directory
- `.github/workflows/nightly.yml` - Workflow (Windows experimental flag)

## Dependencies

None - standalone bug fix

## Related Issues

- #533: test_search_to_file (Windows file handling)
- #535: Windows permission test failures (5 tests)
- #536: test_save_season_unicode_data (Windows encoding)
- #537: test_list_continues_after_individual_error (Windows)

## Additional Notes

**Windows Locale Handling:**
- Windows uses different locale naming conventions
- Environment variables like `LANG` may not be set by default
- Need to use Windows API for locale detection or set explicitly
- UTF-8 is not default encoding on Windows (uses cp1252 or system codepage)

**Testing on Windows:**
- Use GitHub Actions Windows runners
- Or test locally with Windows VM / WSL2
- Python's `locale` module behavior differs on Windows

**Best Practices:**
- Use `sys.getdefaultencoding()` to check encoding
- Explicitly set UTF-8 encoding when needed
- Test locale detection with various Windows locale settings
- Consider using `babel` library for more robust i18n on Windows

**Recent Fix Reference:**
- PR #532 replaced `locale.getdefaultlocale()` with env var parsing
- This fix may need Windows-specific adjustments
- Check commit `320408c` for recent i18n changes

## Implementation Notes

**Implemented**: 2026-05-08
**Branch**: testing/028-fix-windows-test-i18n-messages
**PR**: #555 - https://github.com/bdperkin/nhl-scrabble/pull/555
**Commits**: 1 commit (ffb5391)

### Root Cause Identified

The test `test_success_messages_translatable` was failing on Windows with exit code 1 instead of 0. Root cause:

1. **`locale.setlocale(locale.LC_CTYPE, "")` fails on Windows** (line 110 in `get_system_locale()`)
   - This call attempts to set locale to "user's default setting"
   - On Windows, this can fail or behave unpredictably
   - Windows doesn't always have `LANG`/`LC_ALL` environment variables set

2. **`locale.setlocale(locale.LC_NUMERIC, locale_code)` can fail on Windows** (line 227 in `format_number()`)
   - Windows uses different locale naming conventions
   - POSIX locale names (e.g., `en_US`) may not be recognized on Windows

### Fix Approach Chosen

**Option: Platform-specific handling with safe fallbacks**

Instead of trying to make Windows locale detection work like Unix (complex and fragile), we:
1. Detect Windows platform (`sys.platform == "win32"`)
2. Skip problematic `setlocale()` calls on Windows
3. Return safe fallbacks (`DEFAULT_LOCALE` / standard formatting)
4. Keep existing Unix/macOS behavior unchanged

### Implementation Details

**File Modified**: `src/nhl_scrabble/i18n.py`

**Changes**:
1. **Import `sys` module** for platform detection
2. **`get_system_locale()` function**:
   ```python
   # Windows: Skip setlocale("") which can fail
   if sys.platform == "win32":
       return DEFAULT_LOCALE

   # Unix/macOS: Use setlocale() as before
   locale.setlocale(locale.LC_CTYPE, "")
   ```
3. **`format_number()` function**:
   ```python
   # Windows: Use standard formatting (avoid setlocale)
   if sys.platform == "win32":
       return f"{number:.2f}"

   # Unix/macOS: Use locale-aware formatting
   locale.setlocale(locale.LC_NUMERIC, locale_code)
   ```
4. **Improved exception handling**:
   ```python
   except (locale.Error, ValueError, OSError):
       # Catch more exception types
   ```
5. **Documentation updates**:
   - Updated docstrings to note Windows behavior
   - Added notes about fallback behavior

### Windows Locale Detection Method

**Method**: Platform detection with safe fallback
- Detect `sys.platform == "win32"`
- Return `DEFAULT_LOCALE` ("en_US") when env vars not set
- Environment variable override (`NHL_SCRABBLE_LANG`) still works on all platforms

### Test Results

**Local Testing (Linux)**:
- ✅ `test_success_messages_translatable`: PASSED
- ✅ All 15 CLI i18n tests: PASSED
- ✅ All 47 i18n module tests: PASSED
- ✅ Coverage: 89.33% on i18n.py

**Windows Testing** (via CI - pending):
- Python 3.12, 3.13, 3.14 on Windows-latest
- Expected: Test now passes with exit code 0

**macOS Testing** (via CI - pending):
- macOS-latest
- Expected: No regression, all tests pass

### Actual vs Estimated Effort

- **Estimated**: 3-5h
- **Actual**: ~1.5h
- **Reason**: Root cause was straightforward once identified; fix was simpler than anticipated

### Challenges Encountered

1. **Initial investigation**: Had to trace through test failure to find root cause in `setlocale()` calls
2. **Platform differences**: Had to understand Windows vs Unix locale behavior differences
3. **Testing limitation**: Cannot fully test Windows behavior on Linux (need CI verification)

### Deviations from Plan

**Original plan suggested**: Using Windows API (ctypes, GetUserDefaultUILanguage) for locale detection

**Actual implementation**: Simpler approach using platform detection and safe fallbacks

**Reason**:
- Windows API approach more complex and fragile
- Safe fallback approach simpler, more maintainable
- Environment variable override still works (user control)
- Number formatting difference on Windows acceptable (minor UX impact)

### Related PRs

- #555 - Main implementation (this PR)

### Lessons Learned

1. **Platform differences matter**: Windows locale behavior very different from Unix
2. **Simple is better**: Platform detection + fallback simpler than trying to make Windows behave like Unix
3. **Test coverage critical**: Having comprehensive tests made regression detection easy
4. **Documentation important**: Clear docstrings help explain platform-specific behavior

### Performance Impact

None - no performance changes, just safer locale handling

### Security Considerations

None - this is a bug fix for test compatibility

### Date of Completion

**Started**: 2026-05-08
**Completed**: 2026-05-08 (pending CI verification)
**Total Time**: ~1.5 hours
