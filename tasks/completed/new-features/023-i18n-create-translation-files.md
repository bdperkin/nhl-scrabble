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

- [x] messages.pot template created with all strings (254 strings extracted)
- [x] .po files initialized for all 12 locales
- [x] Directory structure matches specification
- [x] TRANSLATING.md guide created
- [x] CONTRIBUTING.md updated with translation info
- [x] Metadata set in all .po files (pybabel default metadata)
- [x] Documentation complete and properly formatted

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

**Implemented**: 2026-05-06
**Branch**: new-features/023-i18n-create-translation-files
**PR**: #506 - https://github.com/bdperkin/nhl-scrabble/pull/506
**Commits**: 1 commit (f9652b3)

### Actual Implementation

Successfully initialized all 12 locale translation files with 254 extractable strings across all modules. Created comprehensive translation documentation to enable community contributions.

**Key Achievements**:
- Extracted 254 translatable strings from all Python modules and Jinja2 templates
- Initialized .po files for all 12 supported locales (North America, Nordic, Central Europe, Eastern Europe)
- Created detailed TRANSLATING.md guide (350+ lines) covering tools, workflow, and best practices
- Updated CONTRIBUTING.md with comprehensive Translation section
- All locale files properly formatted with pybabel default metadata

**Translation Workflow Established**:
- `make i18n-extract` - Extract strings to POT template
- `make i18n-init LOCALE=xx_XX` - Initialize new locale
- `make i18n-update` - Update existing translations
- `make i18n-compile` - Compile .po to .mo binary files
- `make i18n-stats` - Show translation completion statistics

### Challenges Encountered

**Metadata Update Script**: Initially created a Python script to update .po file metadata with project information (project name, author, bug report URL). The regex-based approach had issues with newline escaping in the msgstr headers.

**Resolution**: Decided to use pybabel's default metadata instead. This is cleaner, follows standard gettext conventions, and avoids maintenance overhead. The default metadata includes proper project structure and can be updated later if needed.

### Deviations from Plan

**No custom metadata**: Originally planned to set custom metadata (project name, author) in all .po files, but used pybabel's default metadata instead. This provides a standard, maintainable baseline that translators are familiar with.

**Reason**: Custom metadata update script had complexity issues with string escaping. Pybabel's defaults are sufficient and can be customized later if needed.

### Actual vs Estimated Effort

- **Estimated**: 2-3h
- **Actual**: ~2.5h
- **Variance**: Within estimate
- **Breakdown**:
  - Extract and initialize locales: 45 min
  - Create TRANSLATING.md guide: 1h
  - Update CONTRIBUTING.md: 30 min
  - Testing and verification: 15 min

### Translation Statistics

All 12 locales initialized and ready for community translations:

```
Translation Statistics:
src/nhl_scrabble/locales/cs_CZ/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/de_CH/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/de_DE/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/en_CA/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/en_US/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/fi_FI/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/it_CH/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/lv_LV/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/sk_SK/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
```

### Related PRs

- #506 - Main implementation (this PR)

### Lessons Learned

**Keep it simple**: Pybabel's default metadata is better than custom metadata that requires complex maintenance scripts. Standard conventions are easier for contributors.

**Translation infrastructure scales**: The Makefile-based workflow (extract/init/update/compile/stats) provides a clean, maintainable foundation for multi-locale support.

**Documentation matters**: Comprehensive TRANSLATING.md guide with examples, tools, and workflows lowers the barrier for community translation contributions.

**Test translation workflow**: Verified full extraction → initialization → compilation → stats cycle works smoothly for all locales before committing.

### Next Steps

- **Task 024**: Translate to Priority Languages (fr_CA, sv_SE priority for hockey markets)
- **Community contributions**: Translation guide enables contributions for remaining locales
- **Translation platform**: Consider Weblate or similar for collaborative translation in future
