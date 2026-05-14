# Translation Quick Start

## Complete All 7 Remaining Translations

```bash
./scripts/translate-all-remaining.sh
```

**Time**: ~20-30 minutes
**Output**: 7 PRs (one per locale)
**Status**: All marked as DRAFT requiring review

## Translate Single Locale

```bash
./scripts/translate-locale.py ru_RU
```

## What Happens

1. ✅ Translates 254 strings using AI database
1. ✅ Compiles .mo files
1. ✅ Updates test config
1. ✅ Updates TRANSLATING.md
1. ✅ Runs i18n tests
1. ✅ Creates git branch
1. ✅ Commits changes
1. ✅ Pushes to remote
1. ✅ Creates PR

## After Translation

### Wait for CI (~5-10 min per PR)

```bash
# Check PR status
gh pr checks 624

# Watch CI
gh pr view 624 --web
```

### Merge When CI Passes

```bash
# Auto-merge
gh pr merge 624 --squash --delete-branch

# Or review first
gh pr view 624
gh pr merge 624 --squash --delete-branch
```

## ⚠️ Important

All translations are **AI-assisted DRAFTS**. They:

- Require native speaker review
- May have unnatural phrasing
- May use wrong terminology
- Should be reviewed before production release

## Remaining Locales

| Locale | Language               | Issue |
| ------ | ---------------------- | ----- |
| ru_RU  | Russian (Russia)       | #514  |
| fi_FI  | Finnish (Finland)      | #515  |
| cs_CZ  | Czech (Czech Republic) | #516  |
| de_DE  | German (Germany)       | #517  |
| it_CH  | Italian (Switzerland)  | #519  |
| sk_SK  | Slovak (Slovakia)      | #520  |
| lv_LV  | Latvian (Latvia)       | #521  |

## Full Documentation

See `scripts/TRANSLATION_AUTOMATION.md` for complete details.
