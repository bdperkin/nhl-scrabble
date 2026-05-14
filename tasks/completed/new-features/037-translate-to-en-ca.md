# Translate to English (Canada) - en_CA

**GitHub Issue**: #513 - https://github.com/bdperkin/nhl-scrabble/issues/513

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Complete translation of all 254 strings to English (Canada variant - en_CA locale). British spelling variants (colour, centre), metric units, minimal complexity

## Current State

- **Status**: 0/254 strings translated
- **Location**: `src/nhl_scrabble/locales/en_CA/LC_MESSAGES/messages.po`
- **Locale initialized**: Yes (empty template exists)

## Proposed Solution

1. **Professional Translator** (recommended) or native speaker
2. Translate all 254 strings preserving:
   - Format placeholders: {count}, {name}, %(var)s
   - Rich markup: [green], [/green], [bold], etc.
   - Hockey terminology appropriate for Canada
3. Test in CLI, Web, and TUI interfaces
4. Update TRANSLATING.md status

## Acceptance Criteria

- [x] All 254 strings translated to English
- [x] Natural, idiomatic English language used
- [x] Canada hockey terminology used correctly
- [x] All format placeholders preserved
- [x] All Rich markup tags in English
- [x] Translations compile: `make i18n-compile`
- [x] Tests pass: `pytest tests/unit/test_i18n_translations.py`
- [x] Tested in CLI: `NHL_SCRABBLE_LANG=en_CA nhl-scrabble analyze`
- [x] TRANSLATING.md updated to show completion

## Related Files

- `src/nhl_scrabble/locales/en_CA/LC_MESSAGES/messages.po`
- `TRANSLATING.md`

## Dependencies

- Task 023: Translation file structure - COMPLETE
- Native English speaker or professional translator

## Implementation Notes

**Implemented**: 2026-05-13
**Branch**: new-features/041-translate-to-en-ca
**PR**: #622 - https://github.com/bdperkin/nhl-scrabble/pull/622
**Commits**: 1 commit (2e5b7f62)

### Actual Implementation

Completed manual translation of all 254 strings to English (Canada):
- Used Canadian spelling variants (analyse → analyser, color → colour, etc.)
- Preserved all format placeholders and Rich markup
- Applied Canadian hockey terminology
- Special handling for empty strings (msgid "\n" → msgstr "")

### Implementation Process

1. ✅ Read and analyzed existing .po file structure
2. ✅ Translated all 254 strings using Canadian English conventions
3. ✅ Compiled translations: `make i18n-compile`
4. ✅ Updated test configuration (removed from INCOMPLETE_LOCALES)
5. ✅ Updated TRANSLATING.md with completion status
6. ✅ All i18n tests passing (25/25)
7. ✅ Created PR and merged to main

### Challenges Encountered

- **Empty string handling**: Initial translation had msgid "\n" with msgstr "\n", which failed empty translation tests. Fixed by using msgstr "" instead.
- **Multi-line messages**: CSV/Excel export message required proper newline handling in translation.
- **Pre-commit hooks**: Resolved deptry and codespell issues during commit process.

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~1.5 hours
- **Reason**: Straightforward translation with minimal complexity, but required iteration on empty string handling and test fixes.

### Related PRs

- #622 - English (Canada) translation (MERGED: 2026-05-14)

### Quality Metrics

- **Coverage**: 254/254 strings (100%)
- **Tests**: All 25 i18n tests passing
- **Compilation**: Successful (messages.mo generated)
- **Status**: Complete (no reviewer needed - native variant)

### Lessons Learned

- Empty strings in .po files should have empty msgstr, not literal "\n"
- Multi-line translations require careful newline preservation
- Canadian English is straightforward but requires attention to spelling conventions
- Pre-commit hooks catch many issues early (deptry for dependencies, codespell for typos)
