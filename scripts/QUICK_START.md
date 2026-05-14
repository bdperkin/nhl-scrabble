# Translation Quick Start

## Status: ✅ ALL 12 LOCALES COMPLETE (as of 2026-05-14)

All 12 supported locales now have complete translations!

## Supported Locales (12 total)

| Region             | Locales                                          | Status   |
| ------------------ | ------------------------------------------------ | -------- |
| **North America**  | en_US (source), en_CA ✅, fr_CA ✅               | Complete |
| **Nordic**         | sv_SE ✅, fi_FI ✅                               | Complete |
| **Central Europe** | cs_CZ ✅, de_DE ✅, de_CH ✅, it_CH ✅, sk_SK ✅ | Complete |
| **Eastern Europe** | ru_RU ✅, lv_LV ✅                               | Complete |

**Native Speaker Reviews**:

- fr_CA (French Canada): ✅ REVIEWED
- sv_SE (Swedish): ✅ REVIEWED
- All others: ⏳ DRAFT (require native speaker review)

## Translation Methods Used

### Automated (7 locales via scripts)

```bash
# These locales were translated using this automation:
# ru_RU, fi_FI, cs_CZ, de_DE, it_CH, sk_SK, lv_LV

./scripts/translate-all-remaining.sh  # Translates all at once
# OR
./scripts/translate-locale.py ru_RU   # Translate single locale
```

### Manual/Earlier (5 locales)

- `en_US`: Source language
- `en_CA`: Manual translation (Canadian spelling variants)
- `fr_CA`: AI-assisted + native speaker review ✅
- `sv_SE`: AI-assisted + native speaker review ✅
- `de_CH`: Manual translation (Swiss German conventions)

## Adding New Locales

To translate a new locale (e.g., `pt_PT` for Portuguese):

### 1. Initialize Locale

```bash
make i18n-init LOCALE=pt_PT
```

### 2. Add Translation Database

Edit `scripts/translate-locale.py` and add translation database:

```python
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ... existing locales ...
    "pt_PT": {
        "Analysis complete!": "Análise completa!",
        "Analyze": "Analisar",
        # ... add ~30-50 core terms
    },
}
```

### 3. Run Translation Script

```bash
./scripts/translate-locale.py pt_PT
```

### 4. What Happens Automatically

1. ✅ Translates 254 strings using AI database
1. ✅ Compiles .mo files
1. ✅ Updates test config
1. ✅ Updates TRANSLATING.md
1. ✅ Runs i18n tests
1. ✅ Creates git branch
1. ✅ Commits changes
1. ✅ Pushes to remote
1. ✅ Creates PR

### 5. After Translation - Wait for CI

```bash
# Check PR status
gh pr checks <PR_NUMBER>

# Watch CI
gh pr view <PR_NUMBER> --web
```

### 6. Merge When CI Passes

```bash
# Auto-merge
gh pr merge <PR_NUMBER> --squash --delete-branch

# Or review first
gh pr view <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
```

## ⚠️ Important

All AI-generated translations are **DRAFTS**. They:

- Require native speaker review
- May have unnatural phrasing
- May use wrong terminology
- Should be reviewed before production release

**Best practice**: Follow the fr_CA and sv_SE examples - get native speaker review!

## Completed Translations Reference

| Locale | Language               | Status           | Issue | PR   |
| ------ | ---------------------- | ---------------- | ----- | ---- |
| en_US  | English (US)           | Source           | -     | -    |
| en_CA  | English (Canada)       | Complete         | #513  | #622 |
| fr_CA  | French (Canada)        | REVIEWED ✅      | #508  | #508 |
| sv_SE  | Swedish (Sweden)       | REVIEWED ✅      | #508  | #508 |
| ru_RU  | Russian (Russia)       | Complete (DRAFT) | #514  | #624 |
| fi_FI  | Finnish (Finland)      | Complete (DRAFT) | #515  | #625 |
| cs_CZ  | Czech (Czech Republic) | Complete (DRAFT) | #516  | #626 |
| de_DE  | German (Germany)       | Complete (DRAFT) | #517  | #627 |
| de_CH  | German (Switzerland)   | Complete (DRAFT) | #518  | #623 |
| it_CH  | Italian (Switzerland)  | Complete (DRAFT) | #519  | #628 |
| sk_SK  | Slovak (Slovakia)      | Complete (DRAFT) | #520  | #629 |
| lv_LV  | Latvian (Latvia)       | Complete (DRAFT) | #521  | #630 |

## Full Documentation

See `scripts/TRANSLATION_AUTOMATION.md` for complete details.
