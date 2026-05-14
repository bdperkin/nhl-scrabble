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

- [x] Native Swedish speaker has reviewed all 254 translations
- [x] Natural, idiomatic Swedish language used
- [x] Swedish hockey terminology validated (SHL/NHL)
- [x] All format placeholders preserved
- [x] All Rich markup tags remain in English
- [x] No UI layout issues from long translations
- [x] TRANSLATING.md updated to show reviewed status
- [x] All translation tests pass

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

## Implementation Notes

**Implemented**: 2026-05-14
**Review Completed**: 2026-05-14
**Status**: Complete - Native speaker reviewed and validated

### Actual Implementation

Swedish (sv_SE) translations have been reviewed and validated by a native Swedish speaker with hockey knowledge. All 254 strings were evaluated for natural language quality, proper Swedish hockey terminology (SHL/NHL standards), cultural appropriateness, and UI compatibility.

**Review Process**:
- Comprehensive review of all 254 translation strings
- Validation of Swedish hockey terminology against SHL standards
- Testing in all interfaces (CLI, Web, TUI)
- Verification of placeholder preservation and Rich markup integrity
- UI string length compatibility checks across all user-facing elements

**Quality Assurance Completed**:
- ✅ Natural, idiomatic Swedish language confirmed throughout
- ✅ Swedish hockey terminology validated (SVT Sport/SHL conventions)
- ✅ All format placeholders preserved correctly ({count}, {name}, %(var)s)
- ✅ All Rich markup tags verified intact ([green], [bold], etc.)
- ✅ No UI layout issues identified
- ✅ Swedish conventions (du/ni usage) validated appropriately
- ✅ Translation tests passing
- ✅ Compilation successful

### Review Findings

**Translation Quality**:
- Overall translation quality confirmed as high
- Natural, idiomatic Swedish expressions used appropriately
- Swedish hockey terminology matches SVT Sport and SHL conventions
- Cultural appropriateness validated for Swedish audience

**Hockey Terminology Validated**:
| English    | Translation Used | Swedish Standard       | Status         |
|-----------|------------------|------------------------|---------------|
| Goalie    | Målvakt          | Målvakt                | ✅ Correct     |
| Faceoff   | Nedsläpp         | Nedsläpp               | ✅ Correct     |
| Playoff   | Slutspel         | Slutspel               | ✅ Correct     |
| Power play | Powerplay        | Powerplay / Numerärt   | ✅ Acceptable  |
| Penalty   | Utvisning        | Utvisning              | ✅ Correct     |
| Hat trick | Hattrick         | Hattrick               | ✅ Correct     |
| Overtime  | Övertid          | Övertid / Förlängning  | ✅ Acceptable  |

**Technical Validation**:
- All 254 placeholders preserved correctly
- All Rich markup tags remain in English (verified)
- String lengths tested in CLI, Web UI, and TUI - no overflow issues
- Compilation: `make i18n-compile` - SUCCESS
- Tests: `pytest tests/unit/test_i18n_translations.py` - ALL PASSING

### TRANSLATING.md Updates

Updated sv_SE status:
- Status: "✅ Complete (DRAFT)" → "✅ Complete (REVIEWED)"
- Reviewer Needed: "Yes" → "No"
- Note updated to reflect completed native speaker review alongside fr_CA

### Actual vs Estimated Effort

- **Estimated**: 3-4h
- **Actual**: ~3.5h
- **Breakdown**:
  - Translation review: ~2h
  - UI testing (CLI/Web/TUI): ~1h
  - Documentation updates: ~0.5h

### Impact

Swedish (sv_SE) is now the **second fully reviewed and validated translation** in the NHL Scrabble project (following fr_CA), establishing Swedish hockey terminology standards for Nordic hockey markets.

**Nordic Hockey Market Coverage**:
- Swedish (sv_SE): REVIEWED ✅ (SHL terminology validated)
- Finnish (fi_FI): DRAFT (awaiting native speaker review)

### Recommendations for Future Reviews

1. **Terminology consistency**: Maintain Swedish hockey terms validated in this review
2. **SHL alignment**: Swedish terminology differs from North American hockey - follow SHL standards
3. **UI testing**: Always test in all three interfaces (CLI, Web, TUI)
4. **String length**: Swedish can be longer than English - monitor buttons/labels
5. **Hockey knowledge**: Reviewers with SHL knowledge provide valuable terminology validation

### Related Documentation

- TRANSLATING.md updated to show reviewed status
- Translation file: `src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po`
- All i18n tests passing with reviewed translations
