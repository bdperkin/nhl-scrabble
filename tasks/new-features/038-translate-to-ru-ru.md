# Translate to Russian (Russia) - ru_RU

**GitHub Issue**: #514 - https://github.com/bdperkin/nhl-scrabble/issues/514

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Complete translation of all 254 strings to Russian (Russia variant - ru_RU locale). Cyrillic encoding, complex grammar cases, requires professional translator

## Current State

- **Status**: 0/254 strings translated
- **Location**: `src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po`
- **Locale initialized**: Yes (empty template exists)

## Proposed Solution

1. **Professional Translator** (recommended) or native speaker
2. Translate all 254 strings preserving:
   - Format placeholders: {count}, {name}, %(var)s
   - Rich markup: [green], [/green], [bold], etc.
   - Hockey terminology appropriate for Russia
3. Test in CLI, Web, and TUI interfaces
4. Update TRANSLATING.md status

## Acceptance Criteria

- [ ] All 254 strings translated to Russian
- [ ] Natural, idiomatic Russian language used
- [ ] Russia hockey terminology used correctly
- [ ] All format placeholders preserved
- [ ] All Rich markup tags in English
- [ ] Translations compile: `make i18n-compile`
- [ ] Tests pass: `pytest tests/unit/test_i18n_translations.py`
- [ ] Tested in CLI: `NHL_SCRABBLE_LANG=ru_RU nhl-scrabble analyze`
- [ ] TRANSLATING.md updated to show completion

## Related Files

- `src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po`
- `TRANSLATING.md`

## Dependencies

- Task 023: Translation file structure - COMPLETE
- Native Russian speaker or professional translator
