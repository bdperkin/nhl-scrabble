# Comprehensive I18n Test Suite for All Locales

**GitHub Issue**: #512 - https://github.com/bdperkin/nhl-scrabble/issues/512

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Create automated tests to validate translation quality, completeness, and functional correctness across all 12 supported locales. Tests should verify: (1) 100% completion, (2) placeholder preservation, (3) markup not translated, (4) hockey terminology consistency, (5) UI string lengths, (6) locale switching, (7) fallback to English.

## Current State

Limited i18n testing:
- `tests/unit/test_i18n_translations.py` - 25 tests for fr_CA and sv_SE
- `tests/integration/test_i18n_integration.py` - 31 integration tests
- No comprehensive validation across all 12 locales
- No CI checks for translation quality
- No pre-commit hooks for translation changes

## Proposed Solution

Create comprehensive test suite covering all 12 locales:

```python
# tests/unit/test_i18n_comprehensive.py

import pytest
from pathlib import Path
import polib
from nhl_scrabble.i18n import SUPPORTED_LOCALES, get_translator

class TestTranslationCompleteness:
    """Test all locales have complete translations."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_100_percent_translated(self, locale):
        """Verify locale has no untranslated strings."""
        po_file = Path(f"src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po")
        po = polib.pofile(str(po_file))

        untranslated = po.untranslated_entries()
        assert len(untranslated) == 0, \
            f"{locale}: {len(untranslated)} untranslated strings found"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_placeholders_preserved(self, locale):
        """Verify format placeholders are preserved in translations."""
        po_file = Path(f"src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po")
        po = polib.pofile(str(po_file))

        for entry in po.translated_entries():
            # Find placeholders in source
            import re
            src_placeholders = set(re.findall(r'\{[^}]+\}', entry.msgid))
            tgt_placeholders = set(re.findall(r'\{[^}]+\}', entry.msgstr))

            assert src_placeholders == tgt_placeholders, \
                f"{locale}: Placeholder mismatch in '{entry.msgid}'"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_rich_markup_not_translated(self, locale):
        """Verify Rich markup tags remain in English."""
        po_file = Path(f"src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po")
        po = polib.pofile(str(po_file))

        markup_pattern = r'\[(green|red|blue|yellow|bold|italic|/\w+)\]'

        for entry in po.translated_entries():
            if '[' in entry.msgid:
                import re
                src_markup = set(re.findall(markup_pattern, entry.msgid))
                tgt_markup = set(re.findall(markup_pattern, entry.msgstr))

                assert src_markup == tgt_markup, \
                    f"{locale}: Markup changed in '{entry.msgid}'"

class TestLocaleSwitching:
    """Test locale switching works in all interfaces."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_cli_locale_switching(self, cli_runner, locale):
        """Test CLI respects locale setting."""
        result = cli_runner.invoke(["analyze", "--locale", locale, "--help"])
        assert result.exit_code == 0

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_translator_loads_for_locale(self, locale):
        """Test translator loads without errors."""
        translator = get_translator(locale)
        assert callable(translator)

        # Test a known string
        result = translator("Team")
        assert isinstance(result, str)
        assert len(result) > 0

class TestTranslationQuality:
    """Test translation quality metrics."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_no_fuzzy_translations(self, locale):
        """Verify no fuzzy (uncertain) translations."""
        po_file = Path(f"src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po")
        po = polib.pofile(str(po_file))

        fuzzy = [e for e in po if 'fuzzy' in e.flags]
        assert len(fuzzy) == 0, \
            f"{locale}: {len(fuzzy)} fuzzy translations found"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_ui_string_lengths_reasonable(self, locale):
        """Verify translated strings aren't excessively long."""
        po_file = Path(f"src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po")
        po = polib.pofile(str(po_file))

        # Allow translations to be up to 150% of source length
        for entry in po.translated_entries():
            src_len = len(entry.msgid)
            tgt_len = len(entry.msgstr)

            if src_len > 0:
                ratio = tgt_len / src_len
                assert ratio <= 1.5, \
                    f"{locale}: '{entry.msgid}' translation too long ({ratio:.1f}x)"
```

## Implementation Steps

1. Install polib for .po file parsing: `pip install polib`
2. Create comprehensive test file
3. Add tests to CI workflow
4. Add pre-commit hook for translation validation
5. Run tests across all 12 locales
6. Document test coverage

## Acceptance Criteria

- [ ] Tests verify 100% translation completion for all 12 locales
- [ ] Tests verify placeholder preservation
- [ ] Tests verify Rich markup not translated
- [ ] Tests verify no fuzzy translations
- [ ] Tests verify reasonable string lengths
- [ ] Tests verify locale switching works (CLI/Web/TUI)
- [ ] Tests verify fallback to English for missing translations
- [ ] CI runs tests on every PR affecting translations
- [ ] Pre-commit hook validates translation changes

## Related Files

- `tests/unit/test_i18n_comprehensive.py` - New comprehensive test file
- `.github/workflows/ci.yml` - Add i18n test job
- `.pre-commit-config.yaml` - Add translation validation hook
- `pyproject.toml` - Add polib to test dependencies

## Dependencies

- polib library for .po file parsing
- All 12 locale .po files present

## Additional Notes

Add to CI workflow:
```yaml
- name: Run comprehensive i18n tests
  run: pytest tests/unit/test_i18n_comprehensive.py -v
```

Add pre-commit hook:
```yaml
- id: check-i18n-quality
  name: Validate translation quality
  entry: pytest tests/unit/test_i18n_comprehensive.py -v
  language: system
  files: '\.po$'
  pass_filenames: false
```
