# Translate to Latvian (Latvia) - lv_LV

**GitHub Issue**: #521 - https://github.com/bdperkin/nhl-scrabble/issues/521

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Complete translation of all 254 strings to Latvian (Latvia variant - lv_LV locale). Growing hockey market, professional translator recommended

## Current State

- **Status**: 0/254 strings translated
- **Location**: `src/nhl_scrabble/locales/lv_LV/LC_MESSAGES/messages.po`
- **Locale initialized**: Yes (empty template exists)

## Proposed Solution

1. **Professional Translator** (recommended) or native speaker
2. Translate all 254 strings preserving:
   - Format placeholders: {count}, {name}, %(var)s
   - Rich markup: [green], [/green], [bold], etc.
   - Hockey terminology appropriate for Latvia
3. Test in CLI, Web, and TUI interfaces
4. Update TRANSLATING.md status

## Acceptance Criteria

- [ ] All 254 strings translated to Latvian
- [ ] Natural, idiomatic Latvian language used
- [ ] Latvia hockey terminology used correctly
- [ ] All format placeholders preserved
- [ ] All Rich markup tags in English
- [ ] Translations compile: `make i18n-compile`
- [ ] Tests pass: `pytest tests/unit/test_i18n_translations.py`
- [ ] Tested in CLI: `NHL_SCRABBLE_LANG=lv_LV nhl-scrabble analyze`
- [ ] TRANSLATING.md updated to show completion

## Related Files

- `src/nhl_scrabble/locales/lv_LV/LC_MESSAGES/messages.po`
- `TRANSLATING.md`

## Dependencies

- Task 023: Translation file structure - COMPLETE
- Native Latvian speaker or professional translator
