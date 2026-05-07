# Native Speaker Review of Swedish (sv_SE) Translations

**GitHub Issue**: #510 - https://github.com/bdperkin/nhl-scrabble/issues/510

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Review and validate the existing 254/254 AI-generated Swedish translations for natural language quality, proper hockey terminology, cultural appropriateness, and UI string length compatibility. The current translations are machine-translated drafts that require native speaker verification to ensure idiomatic Swedish and proper Swedish hockey terminology.

## Current State

Swedish (sv_SE) locale has complete translations:
- **Status**: 254/254 strings translated (100%)
- **Source**: AI-assisted machine translation
- **Quality**: DRAFT - requires native speaker review
- **Location**: `src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po`

## Proposed Solution

Engage a native Swedish speaker (preferably with hockey knowledge) to review all 254 translations for:

### 1. Swedish Hockey Terminology

Verify Swedish hockey terms are used correctly:

| English | Current Translation | Swedish Standard | Review |
|---------|-------------------|------------------|--------|
| Goalie | Målvakt | Målvakt | ✓ Verify |
| Faceoff | Nedsläpp | Nedsläpp | ✓ Verify |
| Playoff | Slutspel | Slutspel / Playoffs | ✓ Verify |
| Power play | Powerplay | Powerplay / Numerärt överläge | ✓ Verify |
| Penalty | Utvisning | Utvisning / Straff | ✓ Verify |
| Hat trick | Hattrick | Hattrick / Tre mål | ✓ Verify |
| Overtime | Övertid | Övertid / Förlängning | ✓ Verify |

### 2. SHL vs NHL Terminology

Verify appropriate terminology (SHL = Swedish Hockey League):
- Use terms familiar to Swedish NHL fans
- Maintain consistency with Swedish hockey broadcasting

## Implementation Steps

1. Prepare review environment with sv_SE locale
2. Review all 254 translations for natural Swedish
3. Validate hockey terminology against SHL standards
4. Verify placeholder and markup preservation
5. Test string lengths in UI
6. Update translations
7. Compile and test
8. Update TRANSLATING.md status to "✅ Complete (REVIEWED)"
9. Create pull request

## Acceptance Criteria

- [ ] Native Swedish speaker has reviewed all 254 translations
- [ ] Natural, idiomatic Swedish language used
- [ ] Swedish hockey terminology validated (SHL/NHL)
- [ ] All format placeholders preserved
- [ ] All Rich markup tags remain in English
- [ ] No UI layout issues from long translations
- [ ] TRANSLATING.md updated to show reviewed status
- [ ] All translation tests pass

## Related Files

- `src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po`
- `TRANSLATING.md`
- `tests/unit/test_i18n_translations.py`

## Dependencies

- **Task 024**: Priority language translations (sv_SE) - COMPLETE
- **Reviewer**: Native Swedish speaker with hockey knowledge

## Additional Notes

### Finding a Reviewer

- r/sweden, r/ishockey subreddits
- Swedish hockey forums (hockeysverige.se)
- Contact SHL teams' international fans
- Swedish open source communities

### Hockey Terminology Resources

- **SVT Sport**: Swedish public broadcasting hockey terms
- **Aftonbladet Hockey**: Swedish sports journalism
- **NHL.com Swedish**: NHL's Swedish language content
- **SHL.se**: Swedish Hockey League official terminology
