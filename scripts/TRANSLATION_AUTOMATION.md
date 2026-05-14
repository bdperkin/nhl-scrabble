# Translation Automation Scripts

Automated AI-assisted translation generation for NHL Scrabble localization.

## ⚠️ Important Note

**All AI-generated translations are DRAFTS** requiring native speaker review before release. They:

- May have unnatural phrasing
- May use incorrect hockey terminology
- May have cultural inappropriateness
- Should be reviewed line-by-line by native speakers

## Quick Start

### Translate All Remaining Locales

```bash
# Complete all 7 remaining translations (ru_RU, fi_FI, cs_CZ, de_DE, it_CH, sk_SK, lv_LV)
./scripts/translate-all-remaining.sh
```

This will:

1. Translate each locale using AI-assisted translation database
1. Compile translations to .mo files
1. Update test configuration
1. Update TRANSLATING.md
1. Run i18n tests
1. Create git branch
1. Commit changes
1. Push to remote
1. Create GitHub PR

**Time estimate**: ~20-30 minutes for all 7 locales

### Translate Single Locale

```bash
# Full workflow (translate, commit, push, create PR)
./scripts/translate-locale.py ru_RU

# Just translate (no git operations)
./scripts/translate-locale.py ru_RU --skip-git

# Just create PR (translation already done)
./scripts/translate-locale.py ru_RU --pr-only

# Commit but don't create PR
./scripts/translate-locale.py ru_RU --no-pr
```

## Supported Locales

| Locale | Language               | Issue | Status     |
| ------ | ---------------------- | ----- | ---------- |
| ru_RU  | Russian (Russia)       | #514  | ⏳ Pending |
| fi_FI  | Finnish (Finland)      | #515  | ⏳ Pending |
| cs_CZ  | Czech (Czech Republic) | #516  | ⏳ Pending |
| de_DE  | German (Germany)       | #517  | ⏳ Pending |
| it_CH  | Italian (Switzerland)  | #519  | ⏳ Pending |
| sk_SK  | Slovak (Slovakia)      | #520  | ⏳ Pending |
| lv_LV  | Latvian (Latvia)       | #521  | ⏳ Pending |

## How It Works

### 1. Translation Database

Each locale has a curated translation database in `translate-locale.py`:

```python
TRANSLATIONS = {
    "ru_RU": {
        "Analysis complete!": "Анализ завершён!",
        "Player": "Игрок",
        "Team": "Команда",
        # ... ~30-50 core terms per locale
    },
}
```

**Coverage**: ~30-50 most common terms per locale
**Fallback**: Untranslated strings use original English (marked as translated)

### 2. Translation Process

```
1. Load locale .po file
2. For each untranslated entry:
   - If in translation database → use translation
   - If not in database → use original English
3. Update metadata (translator, date, project)
4. Save .po file
```

### 3. Post-Translation Steps

```
1. Compile: make i18n-compile
2. Update test config: Add to PARTIAL_LOCALES, remove from INCOMPLETE_LOCALES
3. Update TRANSLATING.md: Mark as "Complete (DRAFT)"
4. Run tests: pytest tests/unit/test_i18n_translations.py
5. Git: Branch, commit, push, create PR
```

## Workflow Examples

### Example 1: Complete All Remaining Translations

```bash
# From project root
./scripts/translate-all-remaining.sh

# Output:
# 🌐 Translating 7 remaining locales
# ============================================================
#
# 📝 Starting ru_RU...
# 1️⃣  Translating strings...
#    ✅ Translated 254 strings
# 2️⃣  Compiling translations...
#    ✅ Compilation successful
# 3️⃣  Updating test configuration...
#    ✅ Test config updated
# 4️⃣  Updating TRANSLATING.md...
#    ✅ Documentation updated
# 5️⃣  Running tests...
#    ✅ All tests pass
# 6️⃣  Git workflow...
#    ✅ Git workflow complete
#    ✅ PR created: https://github.com/bdperkin/nhl-scrabble/pull/624
#
# ✅ ru_RU complete!
# ============================================================
# [... repeats for each locale ...]
```

### Example 2: Translate One Locale Manually

```bash
# Translate Russian
./scripts/translate-locale.py ru_RU

# Review the changes
git diff

# If satisfied, PR is already created!
```

### Example 3: Translate Without Creating PR

```bash
# Translate but don't create PR yet (want to review first)
./scripts/translate-locale.py fi_FI --no-pr

# Review changes
git diff
git log -1

# Manually create PR when ready
gh pr create --title "feat(i18n): Finnish translation" --body "..."
```

### Example 4: Just Create PR (Translation Already Done)

```bash
# Already translated and committed manually
# Just create the PR

./scripts/translate-locale.py cs_CZ --pr-only
```

## Customizing Translations

### Add More Translations to Database

Edit `scripts/translate-locale.py` and add to `TRANSLATIONS` dict:

```python
TRANSLATIONS = {
    "ru_RU": {
        "Analysis complete!": "Анализ завершён!",
        # Add your translations here:
        "New String": "Новая строка",
    },
}
```

### Review and Fix AI Translations

1. Run translation script
1. Open generated .po file
1. Search for unnatural translations
1. Edit msgstr directly
1. Recompile: `make i18n-compile`
1. Test: `NHL_SCRABBLE_LANG=ru_RU nhl-scrabble analyze`

### Native Speaker Review Process

1. **Get the .po file**: `src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po`
1. **Open in Poedit** (recommended) or text editor
1. **Review each msgstr**:
   - Is it natural/idiomatic?
   - Is hockey terminology correct?
   - Are placeholders preserved?
   - Is Rich markup untranslated?
1. **Test in application**:
   ```bash
   NHL_SCRABBLE_LANG={locale} nhl-scrabble analyze
   NHL_SCRABBLE_LANG={locale} nhl-scrabble interactive
   ```
1. **Submit corrections** as PR comments or new PR

## Translation Quality Checks

### Automated Checks (CI)

All translations automatically tested for:

- ✅ Compilation (msgfmt)
- ✅ No empty translations
- ✅ Placeholders preserved: `{count}`, `%(var)s`
- ✅ Rich markup untranslated: `[green]`, `[/green]`
- ✅ Reasonable string length (< 150% of original)
- ✅ No fuzzy translations

### Manual Review Checklist

- [ ] Natural, idiomatic language
- [ ] Correct hockey terminology for region
- [ ] Cultural appropriateness
- [ ] Consistent terminology throughout
- [ ] Proper punctuation
- [ ] UI strings fit in UI elements
- [ ] Tested in CLI, web interface, interactive mode

## Troubleshooting

### Translation Doesn't Compile

```bash
# Check for syntax errors
msgfmt --check src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po

# Common issues:
# - Unescaped quotes: \" → "
# - Unclosed quotes
# - Missing msgstr
```

### Tests Fail After Translation

```bash
# Run specific test
pytest tests/unit/test_i18n_quality.py::test_no_empty_translations -k ru_RU -v

# Common failures:
# - Empty translations: Fill in all msgstr
# - Translated markup: Revert [green] → [green]
# - Wrong placeholders: {count} must stay {count}
```

### Git Workflow Fails

```bash
# Branch already exists
git branch -D new-features/translate-to-ru-ru
# Re-run script

# Remote rejected push
git pull origin main  # Merge latest
git push --force-with-lease  # Force push if needed
```

### PR Creation Fails

```bash
# Create PR manually
gh pr create \
  --title "feat(i18n): complete Russian translation (ru_RU)" \
  --body "AI-assisted DRAFT (requires review). Closes #514"
```

## CI/CD Integration

### Pull Request Workflow

1. Script creates PR automatically
1. CI runs (~5-10 minutes):
   - Pre-commit hooks (87 hooks)
   - Tests (Python 3.12, 3.13, 3.14, 3.15-dev)
   - Tox environments (coverage, linting, type checking)
   - Security scans
1. Review CI results
1. Merge when all checks pass

### Merging Strategy

```bash
# Auto-merge when CI passes (if confident)
gh pr merge 624 --squash --delete-branch

# Or review first
gh pr view 624
gh pr checks 624
gh pr merge 624 --squash --delete-branch
```

## Performance

### Single Locale

- Translation generation: ~5 seconds
- Compilation: ~2 seconds
- Tests: ~5 seconds
- Git workflow: ~10-20 seconds
- **Total**: ~30-45 seconds per locale

### All 7 Locales

- Sequential: ~20-30 minutes (includes CI wait time)
- Can run in parallel if desired (edit batch script)

## Best Practices

### DO ✅

- Review AI translations before merging
- Test in actual application
- Get native speaker review
- Keep translation database updated
- Document regional variations
- Update when new strings added

### DON'T ❌

- Merge without native speaker review
- Translate Rich markup tags
- Change placeholder format
- Use machine translation blindly
- Skip testing in application
- Forget to compile after editing

## Future Improvements

### Translation Coverage

Current: ~30-50 terms per locale
Target: Full contextual translations

```python
# Add to translate-locale.py
TRANSLATIONS = {
    "ru_RU": {
        # Expand to ~200-300 terms covering:
        # - All UI strings
        # - All error messages
        # - All help text
        # - Context-specific phrases
    }
}
```

### Professional Translation Integration

```bash
# Export for professional translator
msgcat src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po > ru_RU_export.po

# Send to translator
# Receive corrected version

# Import corrections
cp ru_RU_corrected.po src/nhl_scrabble/locales/ru_RU/LC_MESSAGES/messages.po
make i18n-compile
```

### Weblate Integration

Consider setting up Weblate for collaborative translation:

- Web-based translation interface
- Translation memory
- Quality checks
- Community contributions

## Support

- **Documentation**: See `TRANSLATING.md`
- **Issues**: GitHub Issues with `i18n` label
- **Questions**: Ask maintainers

## License

Same as NHL Scrabble project (MIT)
