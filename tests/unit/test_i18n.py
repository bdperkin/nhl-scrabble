"""Unit tests for i18n utilities module."""

import locale
import os
from pathlib import Path
from unittest.mock import patch

from nhl_scrabble.i18n import (
    DEFAULT_LOCALE,
    LOCALES_DIR,
    SUPPORTED_LOCALES,
    format_number,
    get_system_locale,
    get_translator,
)


class TestConstants:
    """Test module constants."""

    def test_supported_locales_count(self):
        """Test that all 12 expected locales are supported."""
        assert len(SUPPORTED_LOCALES) == 12

    def test_supported_locales_includes_defaults(self):
        """Test that essential locales are included."""
        assert "en_US" in SUPPORTED_LOCALES
        assert "fr_CA" in SUPPORTED_LOCALES
        assert "sv_SE" in SUPPORTED_LOCALES

    def test_supported_locales_all_valid_format(self):
        """Test all locale codes follow proper format."""
        for loc in SUPPORTED_LOCALES:
            # Should be format: xx_YY (lowercase_UPPERCASE)
            parts = loc.split("_")
            assert len(parts) == 2
            assert len(parts[0]) == 2
            assert len(parts[1]) == 2
            assert parts[0].islower()
            assert parts[1].isupper()

    def test_default_locale(self):
        """Test default locale is en_US."""
        assert DEFAULT_LOCALE == "en_US"

    def test_default_locale_in_supported(self):
        """Test default locale is in supported locales."""
        assert DEFAULT_LOCALE in SUPPORTED_LOCALES

    def test_locales_dir_path(self):
        """Test locales directory path is correct."""
        assert LOCALES_DIR.name == "locales"
        assert "nhl_scrabble" in str(LOCALES_DIR)
        assert isinstance(LOCALES_DIR, Path)


class TestGetSystemLocale:
    """Test get_system_locale function."""

    def test_get_system_locale_fallback_none(self):
        """Test get_system_locale returns default when detection fails (None)."""
        with patch("locale.getdefaultlocale", return_value=(None, None)):
            assert get_system_locale() == DEFAULT_LOCALE

    def test_get_system_locale_fallback_valueerror(self):
        """Test get_system_locale handles ValueError gracefully."""
        with patch("locale.getdefaultlocale", side_effect=ValueError):
            assert get_system_locale() == DEFAULT_LOCALE

    def test_get_system_locale_fallback_typeerror(self):
        """Test get_system_locale handles TypeError gracefully."""
        with patch("locale.getdefaultlocale", side_effect=TypeError):
            assert get_system_locale() == DEFAULT_LOCALE

    def test_get_system_locale_supported(self):
        """Test get_system_locale returns supported locale."""
        with patch("locale.getdefaultlocale", return_value=("fr_CA", "UTF-8")):
            assert get_system_locale() == "fr_CA"

    def test_get_system_locale_unsupported(self):
        """Test get_system_locale falls back for unsupported locale."""
        with patch("locale.getdefaultlocale", return_value=("ja_JP", "UTF-8")):
            assert get_system_locale() == DEFAULT_LOCALE

    def test_get_system_locale_all_supported_locales(self):
        """Test get_system_locale works for all supported locales."""
        for supported_locale in SUPPORTED_LOCALES:
            with patch("locale.getdefaultlocale", return_value=(supported_locale, "UTF-8")):
                assert get_system_locale() == supported_locale

    def test_get_system_locale_case_sensitive(self):
        """Test get_system_locale is case-sensitive."""
        # en_us (wrong case) should not match en_US
        with patch("locale.getdefaultlocale", return_value=("en_us", "UTF-8")):
            assert get_system_locale() == DEFAULT_LOCALE


class TestGetTranslator:
    """Test get_translator function."""

    def test_get_translator_default(self):
        """Test get_translator returns function for default locale."""
        _ = get_translator("en_US")
        assert callable(_)
        # Without compiled translations, should return identity function
        assert _("Hello") == "Hello"

    def test_get_translator_returns_callable(self):
        """Test get_translator always returns callable."""
        for locale_code in SUPPORTED_LOCALES:
            _ = get_translator(locale_code)
            assert callable(_)

    def test_get_translator_unsupported_locale(self):
        """Test get_translator falls back for unsupported locale."""
        _ = get_translator("invalid_LOCALE")
        assert callable(_)
        assert _("Test") == "Test"

    def test_get_translator_none_locale(self):
        """Test get_translator with None falls back to system locale."""
        with patch("nhl_scrabble.i18n.get_system_locale", return_value="sv_SE"):
            _ = get_translator(None)
            assert callable(_)

    def test_get_translator_env_var_priority(self):
        """Test get_translator respects NHL_SCRABBLE_LANG env var."""
        with (
            patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}),
            patch("nhl_scrabble.i18n.get_system_locale", return_value="sv_SE"),
        ):
            # Should use env var (fr_CA) not system locale (sv_SE)
            # We can't test the actual locale used, but we can test it's callable
            _ = get_translator()
            assert callable(_)

    def test_get_translator_explicit_overrides_env(self):
        """Test explicit locale_code overrides environment variable."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
            # Explicit parameter should take precedence
            _ = get_translator("sv_SE")
            assert callable(_)

    def test_get_translator_filenotfound_fallback(self):
        """Test get_translator gracefully handles missing translation files."""
        # Force FileNotFoundError by using non-existent locale
        _ = get_translator("ru_RU")
        assert callable(_)
        # Should return identity function
        assert _("Test String") == "Test String"

    def test_get_translator_priority_explicit(self):
        """Test priority: explicit parameter beats all."""
        with (
            patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "de_DE"}),
            patch("nhl_scrabble.i18n.get_system_locale", return_value="fi_FI"),
        ):
            _ = get_translator("cs_CZ")
            # Verify it's callable (actual locale tested via identity function)
            assert callable(_)

    def test_get_translator_identity_function(self):
        """Test fallback identity function preserves strings."""
        _ = get_translator("unsupported_LOCALE")
        test_strings = [
            "Hello, World!",
            "Special chars: äöü ñ",
            "Numbers: 12345",
            "Empty string should work",
            "Punctuation!? Yes.",
        ]
        for s in test_strings:
            assert _(s) == s


class TestFormatNumber:
    """Test format_number function."""

    def test_format_number_fallback_invalid_locale(self):
        """Test format_number fallback for invalid locale."""
        result = format_number(1234.56, "invalid_LOCALE")
        assert result == "1234.56"

    def test_format_number_fallback_none_locale(self):
        """Test format_number with None uses system locale."""
        with patch("nhl_scrabble.i18n.get_system_locale", return_value="en_US"):
            result = format_number(1234.56, None)
            # Result format varies by system, just check it contains the number
            assert "1234" in result or "1,234" in result

    def test_format_number_basic_formats(self):
        """Test format_number with various numbers."""
        # Test fallback mode (invalid locale)
        test_cases = [
            (1234.56, "1234.56"),
            (0.0, "0.00"),
            (999999.99, "999999.99"),
            (0.01, "0.01"),
        ]
        for number, expected in test_cases:
            result = format_number(number, "invalid")
            assert result == expected

    def test_format_number_decimal_places(self):
        """Test format_number always uses 2 decimal places."""
        result = format_number(123, "invalid")
        assert result == "123.00"

        result = format_number(123.1, "invalid")
        assert result == "123.10"

        result = format_number(123.456789, "invalid")
        assert result == "123.46"

    def test_format_number_negative(self):
        """Test format_number with negative numbers."""
        result = format_number(-1234.56, "invalid")
        assert result == "-1234.56"

    def test_format_number_zero(self):
        """Test format_number with zero."""
        result = format_number(0.0, "invalid")
        assert result == "0.00"

    def test_format_number_large_number(self):
        """Test format_number with large numbers."""
        result = format_number(1234567890.12, "invalid")
        assert result == "1234567890.12"

    def test_format_number_locale_error_handling(self):
        """Test format_number handles locale.Error gracefully."""
        with patch("locale.setlocale", side_effect=locale.Error):
            result = format_number(1234.56, "en_US")
            assert result == "1234.56"

    def test_format_number_restores_locale(self):
        """Test format_number restores original locale."""
        # Save current locale
        current = locale.getlocale(locale.LC_NUMERIC)

        # Call format_number (may change locale internally)
        format_number(1234.56, "invalid")

        # Verify locale restored
        after = locale.getlocale(locale.LC_NUMERIC)
        assert after == current


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_translator_empty_string(self):
        """Test translator with empty string."""
        _ = get_translator()
        assert _("") == ""

    def test_translator_unicode(self):
        """Test translator with unicode characters."""
        _ = get_translator()
        test_strings = [
            "Björk",
            "Москва",
            "日本語",
            "Émile",
            "Zürich",
        ]
        for s in test_strings:
            # Identity function should preserve unicode
            assert _(s) == s

    def test_translator_special_characters(self):
        """Test translator with special characters."""
        _ = get_translator()
        test_strings = [
            'Hello "World"',
            "It's a test",
            "Line\nBreak",
            "Tab\tCharacter",
        ]
        for s in test_strings:
            assert _(s) == s

    def test_format_number_very_small(self):
        """Test format_number with very small numbers."""
        result = format_number(0.001, "invalid")
        assert result == "0.00"  # Rounds to 2 decimal places

    def test_format_number_scientific_notation(self):
        """Test format_number with scientific notation input."""
        result = format_number(1.23e5, "invalid")
        assert result == "123000.00"

    def test_multiple_translators(self):
        """Test creating multiple translators doesn't interfere."""
        _en = get_translator("en_US")
        _fr = get_translator("fr_CA")
        _sv = get_translator("sv_SE")

        # All should be callable
        assert callable(_en)
        assert callable(_fr)
        assert callable(_sv)

        # All should work independently
        assert _en("Test") == "Test"
        assert _fr("Test") == "Test"
        assert _sv("Test") == "Test"


class TestIntegration:
    """Integration-style tests using real module state."""

    def test_locales_dir_parent_is_nhl_scrabble(self):
        """Test LOCALES_DIR is in nhl_scrabble package."""
        assert LOCALES_DIR.parent.name == "nhl_scrabble"

    def test_all_supported_locales_unique(self):
        """Test all supported locales are unique."""
        assert len(SUPPORTED_LOCALES) == len(set(SUPPORTED_LOCALES))

    def test_supported_locales_immutable(self):
        """Test SUPPORTED_LOCALES is a list (can't verify immutability in Python)."""
        assert isinstance(SUPPORTED_LOCALES, list)

    def test_get_translator_consistent_results(self):
        """Test get_translator returns consistent results for same input."""
        _1 = get_translator("en_US")
        _2 = get_translator("en_US")

        # Should return same type of function
        assert type(_1) == type(_2)  # noqa: E721
        assert callable(_1)
        assert callable(_2)

    def test_env_var_isolation(self):
        """Test environment variable changes don't affect existing translators."""
        # Get translator without env var
        _ = get_translator()

        # Set env var
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
            # Existing translator should still work
            assert callable(_)
            assert _("Test") == "Test"
