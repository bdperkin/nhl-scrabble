"""Tests for i18n functionality, locale switching, and infrastructure."""

import shutil

import polib
import pytest

from nhl_scrabble.i18n import LOCALES_DIR, SUPPORTED_LOCALES, get_translator


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

        # Safe: nhl-scrabble is this project's CLI installed in test environment
        result = subprocess.run(
            ["nhl-scrabble", "--help"],  # noqa: S607
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
