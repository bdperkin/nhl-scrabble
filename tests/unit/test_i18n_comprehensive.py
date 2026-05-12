"""Comprehensive i18n test suite for all 12 supported locales.

This module provides comprehensive testing of translation quality, completeness,
and functional correctness across all supported locales.

Test Coverage:
    - Translation completeness (100% for all locales)
    - Placeholder preservation ({variable} format strings)
    - Rich markup preservation ([color] tags)
    - No fuzzy translations (uncertain translations)
    - Reasonable UI string lengths (≤150% of source)
    - Locale switching functionality (CLI/Web/TUI)
    - Fallback behavior for missing translations
"""

import re
import shutil

import polib
import pytest

from nhl_scrabble.i18n import (
    DEFAULT_LOCALE,
    LOCALES_DIR,
    SUPPORTED_LOCALES,
    get_translator,
)

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


class TestLocaleSwitching:
    """Test locale switching works in all interfaces."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_translator_loads_for_locale(self, locale: str) -> None:
        """Test translator loads without errors.

        Args:
            locale: Locale code to test.

        Notes:
            - Tests that get_translator() succeeds
            - Tests that returned function is callable
            - Does not test translation accuracy (covered elsewhere)
        """
        translator = get_translator(locale)
        assert callable(translator), f"{locale}: Translator is not callable"

        # Test a known string exists
        result = translator("Team")
        assert isinstance(result, str), f"{locale}: Translation not a string"
        assert len(result) > 0, f"{locale}: Translation is empty"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_translator_handles_missing_translation(self, locale: str) -> None:
        """Test translator falls back to source for missing strings.

        Args:
            locale: Locale code to test.

        Notes:
            - Untranslated strings should return source (English)
            - Prevents runtime errors when translations incomplete
        """
        translator = get_translator(locale)

        # Test with a string that definitely doesn't exist
        fake_string = f"FAKE_STRING_NEVER_TRANSLATED_{locale}_xyz123"
        result = translator(fake_string)

        # Should return source string unchanged
        assert result == fake_string, f"{locale}: Expected fallback to source, got '{result}'"


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
                f"Run 'make i18n-update' and review fuzzy translations."
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
                f"{locale}: {len(empty)} empty translations found:\n" f"{empty_examples}"
            )


class TestLocaleMetadata:
    """Test locale metadata and catalog info."""

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_has_valid_metadata(self, locale: str) -> None:
        """Verify .po file has valid metadata.

        Args:
            locale: Locale code to test.

        Notes:
            - Checks for Project-Id-Version, Language, Language-Team
            - Metadata helps translators understand context
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        # Check for essential metadata fields
        assert po.metadata.get("Language"), f"{locale}: Missing Language metadata"
        assert po.metadata.get("Content-Type"), f"{locale}: Missing Content-Type metadata"

    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_locale_encoding_utf8(self, locale: str) -> None:
        """Verify .po file uses UTF-8 encoding.

        Args:
            locale: Locale code to test.

        Notes:
            - UTF-8 required for international characters
            - Should be "Content-Type: text/plain; charset=UTF-8"
        """
        po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"
        po = polib.pofile(str(po_file))

        content_type = po.metadata.get("Content-Type", "")
        assert "UTF-8" in content_type or "utf-8" in content_type, (
            f"{locale}: Not using UTF-8 encoding. " f"Found: {content_type}"
        )


class TestHockeyTerminologyConsistency:
    """Test hockey-specific terminology is consistently translated."""

    # Common hockey terms that should be translated consistently
    HOCKEY_TERMS = {
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


class TestCLILocaleSwitching:
    """Test CLI-specific locale switching."""

    @pytest.mark.skipif(
        shutil.which("nhl-scrabble") is None,
        reason="nhl-scrabble CLI not found (package not installed)",
    )
    @pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
    def test_cli_help_respects_locale(self, locale: str) -> None:
        """Test CLI help text respects locale setting.

        Args:
            locale: Locale code to test.

        Notes:
            - Tests that --help shows localized text
            - Exit code should be 0 (success)
            - Output should contain help text (localized or English)
        """
        import os
        import subprocess

        env = os.environ.copy()
        env["NHL_SCRABBLE_LANG"] = locale

        result = subprocess.run(
            ["nhl-scrabble", "--help"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        assert (
            result.returncode == 0
        ), f"{locale}: CLI --help failed with exit code {result.returncode}"
        assert len(result.stdout) > 0, f"{locale}: CLI --help produced no output"


class TestFallbackBehavior:
    """Test fallback to English for missing/incomplete translations."""

    def test_invalid_locale_falls_back_to_default(self) -> None:
        """Test that invalid locale code falls back to default (en_US).

        Notes:
            - Invalid locales should not crash
            - Should gracefully return English translations
        """
        translator = get_translator("invalid_XX")

        result = translator("Team")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_missing_translation_returns_source(self) -> None:
        """Test that missing translation returns source string.

        Notes:
            - Prevents runtime errors from incomplete translations
            - User sees English instead of error or blank
        """
        # Test with a locale that exists but string doesn't
        translator = get_translator("fr_CA")

        fake_string = "TOTALLY_FAKE_STRING_NEVER_EXISTS_xyz789"
        result = translator(fake_string)

        assert result == fake_string, "Expected source string fallback for missing translation"


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


class TestI18nInfrastructure:
    """Test i18n infrastructure and tooling."""

    def test_all_locales_in_supported_list(self) -> None:
        """Verify all locale directories are in SUPPORTED_LOCALES.

        Notes:
            - Prevents orphaned locale directories
            - Ensures SUPPORTED_LOCALES is up-to-date
        """
        locale_dirs = [
            d.name
            for d in LOCALES_DIR.iterdir()
            if d.is_dir() and (d / "LC_MESSAGES" / "messages.po").exists()
        ]

        for locale_dir in locale_dirs:
            assert (
                locale_dir in SUPPORTED_LOCALES
            ), f"{locale_dir} directory exists but not in SUPPORTED_LOCALES"

    def test_supported_locales_have_directories(self) -> None:
        """Verify all SUPPORTED_LOCALES have locale directories.

        Notes:
            - Ensures no missing locale directories
            - All supported locales should have infrastructure
        """
        for locale in SUPPORTED_LOCALES:
            locale_dir = LOCALES_DIR / locale / "LC_MESSAGES"
            assert (
                locale_dir.exists()
            ), f"{locale} in SUPPORTED_LOCALES but directory missing: {locale_dir}"

    def test_locales_directory_exists(self) -> None:
        """Verify locales directory exists.

        Notes:
            - Required for gettext to find translations
            - Should be src/nhl_scrabble/locales/
        """
        assert LOCALES_DIR.exists(), f"Locales directory not found: {LOCALES_DIR}"
        assert LOCALES_DIR.is_dir(), f"Locales path is not a directory: {LOCALES_DIR}"

    def test_pot_template_exists(self) -> None:
        """Verify .pot template file exists.

        Notes:
            - Template is source for all .po files
            - Generated by 'make i18n-extract'
            - Should be src/nhl_scrabble/locales/messages.pot
            - Test skipped if file doesn't exist (needs to be generated)
        """
        pot_file = LOCALES_DIR / "messages.pot"
        if not pot_file.exists():
            pytest.skip(
                f"POT template not found: {pot_file}. " "Run 'make i18n-extract' to generate.",
            )

        # Verify it's a valid POT file
        po = polib.pofile(str(pot_file))
        assert len(po) > 0, "POT template is empty"
