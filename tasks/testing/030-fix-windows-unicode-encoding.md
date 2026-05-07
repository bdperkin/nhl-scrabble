# Fix Windows Test Failure: test_save_season_unicode_data

**GitHub Issue**: #536 - https://github.com/bdperkin/nhl-scrabble/issues/536

## Priority

**HIGH** - Data Integrity / Unicode Support

## Estimated Effort

2-3 hours

## Description

Fix test_historical_storage.py::TestSaveSeasonEdgeCases::test_save_season_unicode_data failing on Windows. Unicode characters (é) are corrupted when saving/loading data, appearing as U+FFFD (replacement character) instead of proper characters.

## Current State

**Test failing on Windows:**
```
FAILED tests/unit/test_historical_storage.py::TestSaveSeasonEdgeCases::test_save_season_unicode_data
AssertionError: assert 'Montréal Canadiens' == 'Montr[U+FFFD]al Canadiens'
                                                      ^
```

**Character Corruption:**
- Expected: `Montréal` (with é)
- Got: `Montr[U+FFFD]al` (with Unicode replacement character U+FFFD)

**Affected Platforms:**
- Windows (all Python versions: 3.12, 3.13, 3.14)
- Ubuntu/macOS: ✅ Passing (UTF-8 by default)

**Discovery:**
- Identified in nightly workflow run: https://github.com/bdperkin/nhl-scrabble/actions/runs/25503287135
- Made non-blocking in PR #532 to prevent false CI failures

## Root Cause Analysis

**Windows Encoding Issues:**
1. **Default encoding is NOT UTF-8** on Windows:
   - Windows uses system codepage (cp1252, cp1251, etc.)
   - `open()` without `encoding=` parameter uses system default
   - UTF-8 characters get corrupted when read/written with wrong encoding

2. **Python 3.15+ UTF-8 Mode:**
   - Python 3.15 enables UTF-8 mode by default
   - Earlier versions on Windows use legacy encodings
   - Test fails on 3.12-3.14 but might pass on 3.15+

3. **File I/O without explicit encoding:**
   ```python
   # WRONG - uses system default encoding on Windows
   with open(file_path, 'w') as f:
       json.dump(data, f)

   # CORRECT - explicit UTF-8 encoding
   with open(file_path, 'w', encoding='utf-8') as f:
       json.dump(data, f)
   ```

## Proposed Solution

### Fix: Add Explicit UTF-8 Encoding

**Step 1: Find all file operations in historical storage**
```bash
grep -n "open(" src/nhl_scrabble/storage/historical.py
```

**Step 2: Add `encoding='utf-8'` to all file operations**

**Example fixes needed:**
```python
# BEFORE (line numbers from grep)
with open(season_file, 'w') as f:
    json.dump(data, f, indent=2)

with open(season_file, 'r') as f:
    return json.load(f)

# AFTER
with open(season_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

with open(season_file, 'r', encoding='utf-8') as f:
    return json.load(f)
```

**Step 3: Also ensure JSON dump uses UTF-8**
```python
# Ensure ASCII=False for proper Unicode handling
with open(season_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

## Implementation Steps

1. **Locate all file operations** in historical storage module:
   ```bash
   cd src/nhl_scrabble/storage/
   grep -n "open(" historical.py
   ```

2. **Review each `open()` call**:
   - Reading files: Add `encoding='utf-8'`
   - Writing files: Add `encoding='utf-8'`
   - Check if `json.dump()` needs `ensure_ascii=False`

3. **Common patterns to fix**:
   ```python
   # Pattern 1: Save season data
   def save_season(self, season_id: str, data: dict) -> None:
       season_file = self.data_dir / f"{season_id}.json"
       with open(season_file, 'w', encoding='utf-8') as f:  # ADD encoding
           json.dump(data, f, indent=2, ensure_ascii=False)  # ADD ensure_ascii=False

   # Pattern 2: Load season data
   def load_season(self, season_id: str) -> dict:
       season_file = self.data_dir / f"{season_id}.json"
       with open(season_file, 'r', encoding='utf-8') as f:  # ADD encoding
           return json.load(f)

   # Pattern 3: List seasons
   def list_seasons(self) -> list[str]:
       # May need encoding if reading file metadata
       pass
   ```

4. **Test fix locally** (if Windows available):
   ```bash
   pytest tests/unit/test_historical_storage.py::TestSaveSeasonEdgeCases::test_save_season_unicode_data -v
   ```

5. **Verify on all platforms**:
   - Windows: UTF-8 encoding now explicit
   - Ubuntu: Still works (UTF-8 is default)
   - macOS: Still works (UTF-8 is default)

6. **Check for similar issues** in other modules:
   ```bash
   # Find all open() calls without encoding parameter
   grep -rn "open(" src/ | grep -v "encoding="
   ```

## Testing Strategy

**Test File Content:**
```python
# Test data with Unicode characters
test_data = {
    "teams": [
        {"name": "Montréal Canadiens", "city": "Montréal"},
        {"name": "San José Sharks", "city": "San José"},
        {"name": "Malmö Redhawks", "city": "Malmö"},
    ],
    "players": [
        {"name": "Artūrs Šilovs"},
        {"name": "Lūkas Dostāls"},
        {"name": "Björk"},
    ]
}
```

**Local Testing:**
```bash
# Run Unicode test
pytest tests/unit/test_historical_storage.py::TestSaveSeasonEdgeCases::test_save_season_unicode_data -v

# Run all historical storage tests
pytest tests/unit/test_historical_storage.py -v

# Test actual file content
python -c "
from nhl_scrabble.storage.historical import HistoricalDataStore
store = HistoricalDataStore()
data = {'team': 'Montréal Canadiens'}
store.save_season('test', data)
loaded = store.load_season('test')
assert loaded['team'] == 'Montréal Canadiens'
print('✅ Unicode preserved!')
"
```

**CI Testing:**
- Windows-latest (Python 3.12, 3.13, 3.14)
- Ubuntu-latest (verify no regression)
- macOS-latest (verify no regression)

## Acceptance Criteria

- [ ] All file operations use `encoding='utf-8'`
- [ ] Test passes on Windows (Python 3.12, 3.13, 3.14)
- [ ] Test still passes on Ubuntu
- [ ] Test still passes on macOS
- [ ] Unicode characters preserved correctly in saved files
- [ ] `json.dump()` uses `ensure_ascii=False` for proper Unicode
- [ ] No new test failures introduced
- [ ] Verified with multiple Unicode characters (é, ñ, ö, å, etc.)

## Related Files

- `src/nhl_scrabble/storage/historical.py` - Main file to fix (all `open()` calls)
- `tests/unit/test_historical_storage.py` - Test file with failing test
- `.github/workflows/nightly.yml` - Workflow (Windows experimental flag)

## Dependencies

None - standalone bug fix

## Related Issues

- #533: test_search_to_file (Windows file handling)
- #534: test_success_messages_translatable (Windows i18n)
- #535: Windows permission test failures (different issue)
- #537: test_list_continues_after_individual_error (Windows)

## Additional Notes

**Python Encoding Best Practices:**
- **Always specify encoding** for text files in Python
- Use `encoding='utf-8'` for cross-platform compatibility
- Never rely on system default encoding
- Use `ensure_ascii=False` in JSON to preserve Unicode

**Why Windows Uses Different Encoding:**
- Historical reasons (pre-Unicode era)
- System codepage varies by Windows locale
- English Windows: cp1252 (Western European)
- Russian Windows: cp1251 (Cyrillic)
- UTF-8 not default until Python 3.15's UTF-8 mode

**PEP 597 - UTF-8 Mode:**
- Python 3.10+: Can enable with `PYTHONUTF8=1` env var
- Python 3.15+: UTF-8 mode enabled by default
- Still best practice to be explicit with `encoding='utf-8'`

**Similar Issues to Check:**
- Any other file I/O in the project
- Log file writing
- Configuration file reading
- Report generation

**Testing Unicode:**
```python
# Good Unicode test characters:
# - é (French)
# - ñ (Spanish)
# - ö, å (Swedish/Nordic)
# - ů, č (Czech)
# - ā, ē (Latvian)
# - ł (Polish)
# All should be in SUPPORTED_LOCALES
```

## Implementation Notes

*To be filled during implementation:*
- Number of `open()` calls fixed
- Files modified
- Test results on all platforms
- Additional Unicode characters tested
- Date of fix completion
