# Translate to Czech (Czech Republic) - cs_CZ

**GitHub Issue**: #516 - https://github.com/bdperkin/nhl-scrabble/issues/516

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

6-8 hours

## Description

Complete translation of all 254 strings to Czech (Czech Republic variant - cs_CZ locale). Complex declensions, Extraliga terminology, professional translator

## Current State

- **Status**: 0/254 strings translated
- **Location**: `src/nhl_scrabble/locales/cs_CZ/LC_MESSAGES/messages.po`
- **Locale initialized**: Yes (empty template exists)

## Proposed Solution

1. **Professional Translator** (recommended) or native speaker
2. Translate all 254 strings preserving:
   - Format placeholders: {count}, {name}, %(var)s
   - Rich markup: [green], [/green], [bold], etc.
   - Hockey terminology appropriate for Czech Republic
3. Test in CLI, Web, and TUI interfaces
4. Update TRANSLATING.md status

## Acceptance Criteria

- [ ] All 254 strings translated to Czech
- [ ] Natural, idiomatic Czech language used
- [ ] Czech Republic hockey terminology used correctly
- [ ] All format placeholders preserved
- [ ] All Rich markup tags in English
- [ ] Translations compile: `make i18n-compile`
- [ ] Tests pass: `pytest tests/unit/test_i18n_translations.py`
- [ ] Tested in CLI: `NHL_SCRABBLE_LANG=cs_CZ nhl-scrabble analyze`
- [ ] TRANSLATING.md updated to show completion

## Related Files

- `src/nhl_scrabble/locales/cs_CZ/LC_MESSAGES/messages.po`
- `TRANSLATING.md`

## Dependencies

- Task 023: Translation file structure - COMPLETE
- Native Czech speaker or professional translator
