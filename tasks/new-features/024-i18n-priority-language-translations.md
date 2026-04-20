# Translate to Priority Languages

**GitHub Issue**: #252 - https://github.com/bdperkin/nhl-scrabble/issues/252

**Parent Task**: #218 - Internationalization and Localization (sub-task 6 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Translate all strings to three priority languages: English (template), French Canadian, and Swedish. This provides immediate value for major NHL markets while establishing the translation workflow. Sixth and final sub-task of i18n/l10n implementation.

**Parent Task**: tasks/new-features/016-internationalization-localization.md

## Proposed Solution

### Phase 1: English (en_US) - Template (2h)

English is the source language, but review for:

- Consistent terminology
- Clear, translatable strings
- Proper capitalization
- Professional tone

### Phase 2: French Canadian (fr_CA) - 3-4h

~200-300 strings to translate:

```po
# src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
msgid "Analyzing NHL rosters..."
msgstr "Analyse des effectifs de la LNH..."

msgid "Team"
msgstr "Équipe"

msgid "Score"
msgstr "Score"

msgid "Player"
msgstr "Joueur"

msgid "Found {count} players"
msgstr "Trouvé {count} joueurs"
```

### Phase 3: Swedish (sv_SE) - 3-4h

```po
# src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po
msgid "Analyzing NHL rosters..."
msgstr "Analyserar NHL-spelartrupper..."

msgid "Team"
msgstr "Lag"

msgid "Score"
msgstr "Poäng"

msgid "Player"
msgstr "Spelare"
```

### Translation Approach Options

1. **Professional Translation Service**

   - Pros: Highest quality, native speakers
   - Cons: Cost ($0.10-0.25/word = $200-500)
   - Timeline: 1-2 weeks

1. **Community Contributions**

   - Pros: Free, community engagement
   - Cons: Requires review, slower
   - Timeline: Variable

1. **Machine Translation + Review**

   - Pros: Fast initial draft
   - Cons: Requires native speaker review
   - Tools: DeepL, Google Translate
   - Timeline: 1-2 days + review

1. **Hybrid Approach** (Recommended)

   - Machine translation for initial draft
   - Native speaker review and corrections
   - Community contributions for remaining locales
   - Best balance of speed and quality

## Implementation Steps

1. **Review English Strings** (2h)

   - Audit all msgid strings
   - Fix awkward phrasing
   - Ensure consistency
   - Document terminology

1. **Translate French Canadian** (3-4h)

   - Use DeepL/Google for initial draft
   - Review by French speaker
   - Compile and test
   - Verify in CLI, Web, TUI

1. **Translate Swedish** (3-4h)

   - Same process as French
   - Review by Swedish speaker
   - Compile and test
   - Verify all interfaces

1. **Compile and Test** (1-2h)

   - Compile all .po files to .mo
   - Test each locale in all interfaces
   - Fix translation issues
   - Verify string length fits UI

## Testing Strategy

```bash
# Test French
nhl-scrabble analyze --locale fr_CA
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze

# Test Swedish
nhl-scrabble analyze --locale sv_SE

# Test web interface
curl http://localhost:8000/?lang=fr_CA
curl http://localhost:8000/?lang=sv_SE
```

## Acceptance Criteria

- [ ] English strings reviewed and cleaned up
- [ ] French Canadian translation complete (~200-300 strings)
- [ ] Swedish translation complete (~200-300 strings)
- [ ] All .po files compiled to .mo
- [ ] Translations tested in CLI
- [ ] Translations tested in Web interface
- [ ] Translations tested in TUI/interactive mode
- [ ] String length verified fits UI
- [ ] Terminology consistent across interfaces
- [ ] Documentation updated with translation status

## Related Files

- `src/nhl_scrabble/locales/en_US/LC_MESSAGES/messages.po` - English template
- `src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po` - French translation
- `src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po` - Swedish translation
- `TRANSLATING.md` - Translation status and contributors

## Dependencies

- **Prerequisites**: All previous i18n sub-tasks (1-5)
- **Parent**: #218

## Additional Notes

**Remaining Locales:**

After Phase 1 (en_US, fr_CA, sv_SE), remaining locales can be translated by:

- Community contributors
- Professional services (if budget available)
- Machine translation + review
- Native speaker volunteers from hockey communities

Priority order for remaining 9 locales:

1. de_DE (German) - Large NHL fanbase
1. fi_FI (Finnish) - Strong hockey culture
1. ru_RU (Russian) - Many NHL players
1. cs_CZ (Czech) - Hockey tradition
   5-9. Other locales as resources permit

**Translation Quality Standards:**

- Natural, fluent language (not literal translation)
- Consistent terminology across all strings
- Appropriate formality level
- Tested by native speakers
- UI strings fit within allocated space
- Technical terms translated appropriately

## Implementation Notes

*To be filled during implementation:*

- Translation method used
- Translators/reviewers credited
- Translation issues encountered
- String length problems resolved
- Actual effort vs estimated
