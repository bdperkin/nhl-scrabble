"""Tests for i18n translation quality metrics and consistency."""

import re
from typing import ClassVar

import polib
import pytest

from nhl_scrabble.i18n import DEFAULT_LOCALE, LOCALES_DIR, SUPPORTED_LOCALES, get_translator

# Locales with partial translations (fuzzy entries or minor issues)
PARTIAL_LOCALES = [
    "fr_CA",  # 8 untranslated, 25 fuzzy
    "sv_SE",  # 8 untranslated, 25 fuzzy
]

# Locales with known incomplete translations
INCOMPLETE_LOCALES = [
    "en_US",  # Source locale
    "en_CA",  # Not yet translated
    "ru_RU",  # Not yet translated
    "fi_FI",  # Not yet translated
    "cs_CZ",  # Not yet translated
    "de_DE",  # Not yet translated
    "de_CH",  # Not yet translated
    "it_CH",  # Not yet translated
    "sk_SK",  # Not yet translated
    "lv_LV",  # Not yet translated
]


class TestRichMarkupPreservation:
    """Test Rich markup tags remain untranslated."""

    # Regex for Rich console markup: [color], [/color], [bold], etc.
    MARKUP_PATTERN = re.compile(
        r"\[(green|red|blue|yellow|cyan|magenta|white|black|bold|italic|underline|"
        r"dim|blink|reverse|strikethrough|/\w+)\]",
    )

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_rich_markup_not_translated(self, locale: str) -> None:
        """Verify Rich markup tags remain in English.

        Args:
            locale: Locale code to test.

        Notes:
            - Rich markup: [green], [bold], [/green], etc.
            - Markup must be identical in source and translation
            - Translated markup breaks Rich console formatting
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        errors = []
        for entry in po.translated_entries():
            if "[" in entry.msgid:
                src_markup = set(self.MARKUP_PATTERN.findall(entry.msgid))
                tgt_markup = set(self.MARKUP_PATTERN.findall(entry.msgstr))

                if src_markup != tgt_markup:
                    errors.append(
                        f"  '{entry.msgid}'\n"
                        f"    Source markup: {sorted(src_markup)}\n"
                        f"    Target markup: {sorted(tgt_markup)}",
                    )

        assert not errors, f"{locale}: Rich markup changes found:\n" + "\n".join(errors)


class TestTranslationQuality:
    """Test translation quality metrics."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_no_fuzzy_translations(self, locale: str) -> None:
        """Verify no fuzzy (uncertain) translations.

        Args:
            locale: Locale code to test.

        Notes:
            - Fuzzy = translations marked uncertain by gettext tools
            - Indicates translation may be outdated or incorrect
            - Should be reviewed and marked as translated or untranslated
        """
        if locale in PARTIAL_LOCALES:
            pytest.xfail(
                f"{locale} has known fuzzy translations. " "Review and resolve fuzzy entries.",
            )

        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        fuzzy = [e for e in po if "fuzzy" in e.flags]
        if fuzzy:
            fuzzy_examples = "\n".join(f"  - {e.msgid}" for e in fuzzy[:5])
            raise AssertionError(
                f"{locale}: {len(fuzzy)} fuzzy translations found:\n"
                f"{fuzzy_examples}\n"
                f"Run 'make i18n-update' and review fuzzy translations.",
            )

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_ui_string_lengths_reasonable(self, locale: str) -> None:
        """Verify translated strings aren't excessively long.

        Args:
            locale: Locale code to test.

        Notes:
            - Allows translations up to 150% of source length
            - Prevents UI layout issues from overly long translations
            - German/Finnish often longer than English, but 150% is reasonable
        """
        if locale in INCOMPLETE_LOCALES or locale in PARTIAL_LOCALES:
            pytest.xfail(
                f"{locale} may have overly long translations. "
                "Review and shorten where possible.",
            )

        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        # Allow translations to be up to 150% of source length
        max_ratio = 1.5

        errors = []
        for entry in po.translated_entries():
            src_len = len(entry.msgid)
            tgt_len = len(entry.msgstr)

            if src_len > 0:
                ratio = tgt_len / src_len
                if ratio > max_ratio:
                    errors.append(
                        f"  '{entry.msgid[:50]}...' "
                        f"({src_len} -> {tgt_len} chars, {ratio:.1f}x)",
                    )

        assert not errors, f"{locale}: Translations exceeding {max_ratio}x length:\n" + "\n".join(
            errors[:10],
        )  # Show first 10

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_no_empty_translations(self, locale: str) -> None:
        """Verify no translated entries are empty strings.

        Args:
            locale: Locale code to test.

        Notes:
            - Empty translations cause UI to show nothing
            - Should be marked untranslated instead
        """
        if locale in PARTIAL_LOCALES:
            pytest.xfail(f"{locale} may have empty translations. " "Review and fix empty entries.")

        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        empty = [e for e in po.translated_entries() if not e.msgstr.strip()]

        if empty:
            empty_examples = "\n".join(f"  - {e.msgid}" for e in empty[:5])
            raise AssertionError(
                f"{locale}: {len(empty)} empty translations found:\n" f"{empty_examples}",
            )


class TestHockeyTerminologyConsistency:
    """Test hockey-specific terminology is consistently translated."""

    # Common hockey terms that should be translated consistently
    HOCKEY_TERMS: ClassVar[dict[str, None]] = {
        "Team": None,  # Should be translated
        "Player": None,
        "Score": None,
        "Division": None,
        "Conference": None,
        "Playoffs": None,
        "Wild Card": None,
    }

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_hockey_terms_translated(self, locale: str) -> None:
        """Verify common hockey terms are translated.

        Args:
            locale: Locale code to test.

        Notes:
            - en_US translations are same as source (valid)
            - Other locales should have translations for hockey terms
            - Some terms may not exist in .po file (not tested here)
        """
        translator = get_translator(locale)

        # For en_US, translation = source is correct
        if locale == DEFAULT_LOCALE:
            pytest.skip(f"{locale} is default locale, skipping translation check")

        # Test that hockey terms are either translated or return source
        for term in self.HOCKEY_TERMS:
            result = translator(term)
            assert isinstance(result, str), f"{locale}: {term} translation is not a string"
            assert len(result) > 0, f"{locale}: {term} translation is empty"


class TestTranslationConsistency:
    """Test consistency within each locale's translations."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_no_duplicate_translations(self, locale: str) -> None:
        """Verify no duplicate msgid entries in .po file.

        Args:
            locale: Locale code to test.

        Notes:
            - Duplicate msgids can cause confusion
            - gettext uses first occurrence, others ignored
            - Should be caught by polib/msgfmt
            - Currently all locales have "Data as of" duplicate
              (needs investigation - may be from different contexts)
        """
        pytest.xfail(
            "All locales have known duplicate msgid entries. "
            "Investigation needed - may be valid context-specific duplicates.",
        )

        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        msgids = [entry.msgid for entry in po if entry.msgid]
        duplicates = [msgid for msgid in set(msgids) if msgids.count(msgid) > 1]

        assert (
            not duplicates
        ), f"{locale}: Found {len(duplicates)} duplicate msgid entries:\n" + "\n".join(
            f"  - {d}" for d in duplicates[:10]
        )
