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

- [ ] Test passes on Windows (Python 3.12, 3.13, 3.14)
- [ ] Test still passes on Ubuntu
- [ ] Test still passes on macOS
- [ ] Locale detection works on Windows
- [ ] Translation files load correctly on Windows
- [ ] UTF-8 encoding handled properly on Windows
- [ ] No new test failures introduced
- [ ] Documentation updated if behavior changes

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

*To be filled during implementation:*
- Root cause identified
- Fix approach chosen
- Windows locale detection method used
- Files modified
- Test results on all platforms
- Date of fix completion
