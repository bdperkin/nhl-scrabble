"""Tests for i18n translation completeness and placeholder preservation."""

import re

import polib
import pytest

from nhl_scrabble.i18n import LOCALES_DIR, SUPPORTED_LOCALES

# Locales with known incomplete translations (expected to fail strict tests)
# Remove from this list as translations are completed
INCOMPLETE_LOCALES = [
    "en_US",  # Source locale, translations not required in .po
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

# Locales with partial translations (fuzzy entries or minor issues)
PARTIAL_LOCALES = [
    "fr_CA",  # 8 untranslated, 25 fuzzy
    "sv_SE",  # 8 untranslated, 25 fuzzy
]


class TestTranslationCompleteness:
    """Test all locales have complete translations."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_100_percent_translated(self, locale: str) -> None:
        """Verify locale has no untranslated strings.

        Args:
            locale: Locale code to test (e.g., "fr_CA").

        Notes:
            - en_US is the source locale (all strings "translated" = source)
            - All other locales must have 100% translations
            - Untranslated entries cause assertion failure with count
        """
        if locale in INCOMPLETE_LOCALES:
            pytest.xfail(
                f"{locale} has known incomplete translations. "
                "Remove from INCOMPLETE_LOCALES when 100% translated.",
            )

        if locale in PARTIAL_LOCALES:
            pytest.xfail(
                f"{locale} has known translation issues. "
                "Remove from PARTIAL_LOCALES when fully complete.",
            )

        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        untranslated = po.untranslated_entries()
        assert len(untranslated) == 0, (
            f"{locale}: {len(untranslated)} untranslated strings found. "
            f"Run 'make i18n-update' and translate missing strings."
        )

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_po_file_exists(self, locale: str) -> None:
        """Verify .po file exists for locale.

        Args:
            locale: Locale code to test.

        Notes:
            - All locales in SUPPORTED_LOCALES must have .po files
            - Files must be in src/nhl_scrabble/locales/{locale}/LC_MESSAGES/
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        assert po_file.exists(), f"{locale}: .po file not found at {po_file}"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_mo_file_exists(self, locale: str) -> None:
        """Verify .mo compiled file exists for locale.

        Args:
            locale: Locale code to test.

        Notes:
            - .mo files are compiled from .po files
            - Required for gettext to load translations
            - Run 'make i18n-compile' if missing
        """
        mo_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.mo"
        assert (
            mo_file.exists()
        ), f"{locale}: .mo file not found. Run 'make i18n-compile' to generate."


class TestPlaceholderPreservation:
    """Test placeholders are preserved in translations."""

    # Regex pattern for format placeholders: {variable}, {count}, etc.
    PLACEHOLDER_PATTERN = re.compile(r"\{[^}]+\}")

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_placeholders_preserved(self, locale: str) -> None:
        """Verify format placeholders are preserved in translations.

        Args:
            locale: Locale code to test.

        Notes:
            - Placeholders like {team}, {count}, {name} must be identical
            - Order can differ between source and translation
            - Missing/extra placeholders cause formatting errors at runtime
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        errors = []
        for entry in po.translated_entries():
            # Find placeholders in source and translation
            src_placeholders = set(self.PLACEHOLDER_PATTERN.findall(entry.msgid))
            tgt_placeholders = set(self.PLACEHOLDER_PATTERN.findall(entry.msgstr))

            if src_placeholders != tgt_placeholders:
                errors.append(
                    f"  '{entry.msgid}'\n"
                    f"    Source: {sorted(src_placeholders)}\n"
                    f"    Target: {sorted(tgt_placeholders)}",
                )

        assert not errors, f"{locale}: Placeholder mismatches found:\n" + "\n".join(errors)

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_percentage_placeholders_preserved(self, locale: str) -> None:
        """Verify % format placeholders are preserved.

        Args:
            locale: Locale code to test.

        Notes:
            - Legacy % formatting: %(name)s, %d, %s, etc.
            - Must preserve both positional (%s) and named (%(var)s)
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        percent_pattern = re.compile(r"%\([^)]+\)[sd]|%[sd]")

        errors = []
        for entry in po.translated_entries():
            src_placeholders = set(percent_pattern.findall(entry.msgid))
            tgt_placeholders = set(percent_pattern.findall(entry.msgstr))

            if src_placeholders != tgt_placeholders:
                errors.append(
                    f"  '{entry.msgid}'\n"
                    f"    Source: {sorted(src_placeholders)}\n"
                    f"    Target: {sorted(tgt_placeholders)}",
                )

        assert not errors, f"{locale}: % placeholder mismatches found:\n" + "\n".join(errors)
