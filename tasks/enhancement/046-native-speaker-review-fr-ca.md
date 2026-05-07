# Native Speaker Review of French Canadian (fr_CA) Translations

**GitHub Issue**: #509 - https://github.com/bdperkin/nhl-scrabble/issues/509

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Review and validate the existing 254/254 AI-generated French Canadian translations for natural language quality, proper hockey terminology, cultural appropriateness, and UI string length compatibility. The current translations are machine-translated drafts that require native speaker verification to ensure idiomatic French and proper Quebec hockey terminology.

## Current State

French Canadian (fr_CA) locale has complete translations:
- **Status**: 254/254 strings translated (100%)
- **Source**: AI-assisted machine translation (DeepL/GPT)
- **Quality**: DRAFT - requires native speaker review
- **Location**: `src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po`

Current translations work functionally but may have issues:
1. Unnatural phrasing or non-idiomatic expressions
2. Hockey terminology may not match Quebec conventions
3. Formal vs informal language choice needs validation
4. String lengths may cause UI layout issues
5. Cultural appropriateness needs verification

## Proposed Solution

Engage a native French Canadian speaker (preferably with hockey knowledge) to review all 254 translations for:

### 1. Natural Language Quality

Review each translation for idiomatic French:

```po
# Example - needs review
msgid "Analysis complete!"
msgstr "Analyse terminée!"  # Is this natural? Or "Analyse complétée!" or "C'est fait!"?

msgid "Fetching team data..."
msgstr "Récupération des données d'équipe..."  # Natural or too formal?
```

### 2. Hockey Terminology Accuracy

Verify Quebec hockey terms are used correctly:

| English | Current Translation | Quebec Standard | Review |
|---------|-------------------|-----------------|--------|
| Goalie | Gardien | Gardien de but / Gardien | ✓ Verify |
| Faceoff | Mise au jeu | Mise au jeu / Mise en jeu | ✓ Verify |
| Playoff | Séries éliminatoires | Séries / Playoffs | ✓ Verify |
| Power play | Avantage numérique | Supériorité numérique / Avantage | ✓ Verify |
| Penalty | Pénalité | Punition / Pénalité | ✓ Verify |

### 3. Placeholder Preservation

Verify all format placeholders are intact:

```po
# Must preserve {count}, {name}, etc.
msgid "Found {count} players"
msgstr "Trouvé {count} joueurs"  # ✓ {count} preserved

msgid "Team: {team_name}"
msgstr "Équipe : {team_name}"  # ✓ {team_name} preserved
```

### 4. Rich Markup Non-Translation

Ensure Rich console markup tags are not translated:

```po
# Markup must stay in English
msgid "[green]Success![/green]"
msgstr "[green]Succès![/green]"  # ✓ Correct

# NOT:
msgstr "[vert]Succès![/vert]"  # ✗ Wrong - breaks formatting
```

### 5. UI String Length Compatibility

Check that translated strings fit in UI elements:

```po
# Short strings are critical for buttons/labels
msgid "Analyze"
msgstr "Analyser"  # 8 chars vs 7 - OK

msgid "Configuration"
msgstr "Configuration"  # Same length - OK

# Flag long translations
msgid "Top Scorers"
msgstr "Meilleurs buteurs"  # 17 vs 11 - may need "Top buteurs"
```

### 6. Cultural Appropriateness

Verify:
- Formal vs informal address (tu vs vous)
- Canadian French vs European French
- Gender-neutral language where appropriate
- Emoji usage is culturally appropriate

## Implementation Steps

1. **Prepare Review Environment**
   ```bash
   # Set locale to fr_CA
   export NHL_SCRABBLE_LANG=fr_CA

   # Test all interfaces
   nhl-scrabble analyze
   nhl-scrabble interactive
   # Visit web interface
   ```

2. **Open Translation File**
   ```bash
   # Use Poedit or text editor
   poedit src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
   # Or
   code src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
   ```

3. **Review Each Translation**
   - Read msgid (English source)
   - Evaluate msgstr (French translation)
   - Check context comments (# references)
   - Verify placeholder preservation
   - Validate Rich markup
   - Test string length in UI

4. **Document Issues Found**
   Create spreadsheet or document:
   | Line | msgid | Current msgstr | Issue | Suggested msgstr |
   |------|-------|---------------|-------|-----------------|
   | 42 | "Analysis complete!" | "Analyse terminée!" | Too formal | "Analyse complétée!" |

5. **Update Translations**
   ```bash
   # Edit .po file with corrections
   vim src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po

   # Compile translations
   make i18n-compile
   ```

6. **Test Updated Translations**
   ```bash
   # Test CLI
   NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze

   # Test Web
   # Visit http://localhost:8000?lang=fr_CA

   # Test TUI
   NHL_SCRABBLE_LANG=fr_CA nhl-scrabble interactive
   ```

7. **Update Documentation**
   Update `TRANSLATING.md`:
   ```markdown
   | fr_CA | French (Canada) | ✅ Complete (REVIEWED) | 254/254 | No |
   ```

8. **Create Pull Request**
   ```bash
   git checkout -b enhancement/046-fr-ca-review
   git add src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
   git add TRANSLATING.md
   git commit -m "feat(i18n): Native speaker review of fr_CA translations"
   git push origin enhancement/046-fr-ca-review
   gh pr create
   ```

## Testing Strategy

### Manual Testing

Test all user-facing strings in context:

```bash
# CLI Help
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble --help
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze --help

# CLI Execution
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze --format text

# Web Interface
# Browse all pages with ?lang=fr_CA
# Check: buttons, labels, error messages, tables

# Interactive Mode
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble interactive
# Test all commands: analyze, help, filter, export, quit
```

### Automated Testing

Existing i18n tests should still pass:

```bash
# Run translation tests
pytest tests/unit/test_i18n_translations.py::TestFrenchCanadianTranslations -v

# Run integration tests
pytest tests/integration/test_i18n_integration.py -v
```

### Review Checklist

- [ ] All 254 strings reviewed for natural language
- [ ] Hockey terminology verified against Quebec standards
- [ ] All placeholders preserved: {count}, {name}, %(var)s
- [ ] All Rich markup tags intact: [green], [/green], [bold], etc.
- [ ] UI string lengths tested in all interfaces
- [ ] Formal vs informal usage is consistent
- [ ] Canadian French (not European French) conventions used
- [ ] No broken layouts from overly long strings
- [ ] Tested in CLI, Web, and TUI interfaces
- [ ] Compilation succeeds: make i18n-compile

## Acceptance Criteria

- [ ] Native French Canadian speaker has reviewed all 254 translations
- [ ] Natural, idiomatic French Canadian language used throughout
- [ ] Quebec hockey terminology validated and corrected where needed
- [ ] All format placeholders preserved (no {count} → {nombre} changes)
- [ ] All Rich markup tags remain in English
- [ ] No UI layout issues from overly long translations
- [ ] Consistent use of formal/informal address
- [ ] TRANSLATING.md updated to show "✅ Complete (REVIEWED)"
- [ ] All translation tests pass
- [ ] Translations compile without errors
- [ ] Documentation of review process completed

## Related Files

- `src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po` - Translation source file
- `src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.mo` - Compiled translations
- `TRANSLATING.md` - Translation status documentation
- `tests/unit/test_i18n_translations.py` - Translation unit tests
- `tests/integration/test_i18n_integration.py` - Translation integration tests

## Dependencies

- **Task 024**: Priority language translations (fr_CA) - COMPLETE
- **Reviewer**: Native French Canadian speaker with hockey knowledge
- **Tools**: Poedit (optional), text editor, make, pytest

## Additional Notes

### Finding a Reviewer

Potential sources for native French Canadian reviewers:
1. **Community Contributors**: Post in r/hockey, r/Habs, r/Quebec subreddits
2. **Open Source Communities**: Weblate, Crowdin platforms
3. **University Hockey Clubs**: Contact McGill, Concordia, Université de Montréal
4. **Professional Services**: Upwork, Fiverr (budget: $50-100 for 3-4 hours)

### Review Compensation

Consider:
- Credit in CONTRIBUTORS.md
- GitHub acknowledgment in PR
- Small honorarium ($25-50) for thorough review
- Reciprocal help with their open source projects

### Hockey Terminology Resources

- **RDS (Réseau des sports)**: French Canadian sports network terminology
- **TVA Sports**: Quebec sports broadcasting terms
- **La Presse Sports**: Quebec hockey journalism
- **NHL.com/fr**: Official NHL French translations (European French, use with caution)

### Common Quebec French vs European French

| European French | Quebec French | English |
|----------------|---------------|---------|
| Football | Hockey | Hockey |
| Match | Partie / Match | Game |
| Gardien | Gardien de but | Goalie |
| Tir | Lancer | Shot |
| Arrêt | Arrêt | Save |

### Translation Memory

After review, add corrections to translation memory for future use:
- Document common patterns
- Create terminology glossary
- Note hockey-specific terms
- Save for other French locales (if added later)

## Implementation Notes

*To be filled during implementation:*
- Name of reviewer and credentials
- Number of corrections made
- Categories of issues found (terminology, grammar, length, etc.)
- Time spent on review
- Recommendations for future translations
- Actual effort vs estimated
