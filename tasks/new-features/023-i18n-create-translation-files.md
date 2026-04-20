# Create Initial Translation File Structure

**GitHub Issue**: #251 - https://github.com/bdperkin/nhl-scrabble/issues/251

**Parent Task**: #218 - Internationalization and Localization (sub-task 5 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Initialize .po translation files for all 12 supported locales, set up directory structure, create template files, and document the translation contribution process. Fifth sub-task of i18n/l10n implementation.

**Parent Task**: tasks/new-features/016-internationalization-localization.md

## Proposed Solution

### Initialize All Locales

```bash
# Extract all strings to POT template
pybabel extract -F babel.cfg -k _ -o messages.pot src/

# Initialize each locale
for locale in en_US en_CA fr_CA sv_SE ru_RU fi_FI cs_CZ de_DE de_CH it_CH sk_SK lv_LV; do
    pybabel init -i messages.pot -d src/nhl_scrabble/locales -l $locale
done
```

### Result Directory Structure

```
src/nhl_scrabble/locales/
├── en_US/LC_MESSAGES/messages.po
├── en_CA/LC_MESSAGES/messages.po
├── fr_CA/LC_MESSAGES/messages.po
├── sv_SE/LC_MESSAGES/messages.po
├── ru_RU/LC_MESSAGES/messages.po
├── fi_FI/LC_MESSAGES/messages.po
├── cs_CZ/LC_MESSAGES/messages.po
├── de_DE/LC_MESSAGES/messages.po
├── de_CH/LC_MESSAGES/messages.po
├── it_CH/LC_MESSAGES/messages.po
├── sk_SK/LC_MESSAGES/messages.po
└── lv_LV/LC_MESSAGES/messages.po
```

### Create TRANSLATING.md Guide

```markdown
# Translation Guide

## Adding Translations

1. Edit the .po file for your locale
2. Find untranslated msgstr entries
3. Add your translation
4. Compile: `pybabel compile -d src/nhl_scrabble/locales`
5. Test the translation
6. Submit pull request

## Translation Tools

- **Poedit**: GUI editor for .po files
- **Weblate**: Web-based translation platform
- **Manual**: Text editor
```

## Implementation Steps

1. **Extract All Strings** (30 min)

   - Run pybabel extract across all modules
   - Verify messages.pot contains all strings
   - Review extracted strings for issues

1. **Initialize Locales** (1h)

   - Run pybabel init for each locale
   - Verify .po file structure
   - Set metadata (language team, charset, etc.)

1. **Create Translation Guide** (1h)

   - Write TRANSLATING.md documentation
   - Include contribution workflow
   - Document tools and best practices
   - Add examples

1. **Update CONTRIBUTING.md** (30 min)

   - Add translation section
   - Link to TRANSLATING.md
   - Explain translation workflow

## Acceptance Criteria

- [ ] messages.pot template created with all strings
- [ ] .po files initialized for all 12 locales
- [ ] Directory structure matches specification
- [ ] TRANSLATING.md guide created
- [ ] CONTRIBUTING.md updated with translation info
- [ ] Metadata set in all .po files
- [ ] Documentation complete

## Related Files

- `src/nhl_scrabble/locales/` - All locale directories
- `messages.pot` - Translation template
- `TRANSLATING.md` - New translation guide
- `CONTRIBUTING.md` - Updated contribution guide
- `babel.cfg` - Extraction configuration

## Dependencies

- **Prerequisites**:
  - Sub-task 1 (I18n Infrastructure)
  - Sub-task 2 (CLI i18n)
  - Sub-task 3 (Web i18n)
  - Sub-task 4 (TUI i18n)
- **Parent**: #218

## Implementation Notes

*To be filled during implementation*
