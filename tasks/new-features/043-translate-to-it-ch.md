# Translate to Italian (Switzerland) - it_CH

**GitHub Issue**: #519 - https://github.com/bdperkin/nhl-scrabble/issues/519

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Complete translation of all 254 strings to Italian (Switzerland variant - it_CH locale). NLA/NLB terminology, professional translator recommended

## Current State

- **Status**: 0/254 strings translated
- **Location**: `src/nhl_scrabble/locales/it_CH/LC_MESSAGES/messages.po`
- **Locale initialized**: Yes (empty template exists)

## Proposed Solution

1. **Professional Translator** (recommended) or native speaker
2. Translate all 254 strings preserving:
   - Format placeholders: {count}, {name}, %(var)s
   - Rich markup: [green], [/green], [bold], etc.
   - Hockey terminology appropriate for Switzerland
3. Test in CLI, Web, and TUI interfaces
4. Update TRANSLATING.md status

## Acceptance Criteria

- [ ] All 254 strings translated to Italian
- [ ] Natural, idiomatic Italian language used
- [ ] Switzerland hockey terminology used correctly
- [ ] All format placeholders preserved
- [ ] All Rich markup tags in English
- [ ] Translations compile: `make i18n-compile`
- [ ] Tests pass: `pytest tests/unit/test_i18n_translations.py`
- [ ] Tested in CLI: `NHL_SCRABBLE_LANG=it_CH nhl-scrabble analyze`
- [ ] TRANSLATING.md updated to show completion

## Related Files

- `src/nhl_scrabble/locales/it_CH/LC_MESSAGES/messages.po`
- `TRANSLATING.md`

## Dependencies

- Task 023: Translation file structure - COMPLETE
- Native Italian speaker or professional translator
