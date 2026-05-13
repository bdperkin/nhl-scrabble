"""Unit tests for i18n locale display functionality."""

from nhl_scrabble.i18n import (
    LOCALE_FLAGS,
    LOCALE_NAMES,
    SUPPORTED_LOCALES,
    get_locale_display_name,
)


class TestLocaleFlagsAndNames:
    """Test LOCALE_FLAGS and LOCALE_NAMES constants."""

    def test_locale_flags_count(self):
        """Test that all supported locales have flag mappings."""
        assert len(LOCALE_FLAGS) == len(SUPPORTED_LOCALES)

    def test_locale_names_count(self):
        """Test that all supported locales have display names."""
        assert len(LOCALE_NAMES) == len(SUPPORTED_LOCALES)

    def test_all_supported_locales_have_flags(self):
        """Test every supported locale has a flag emoji."""
        for locale_code in SUPPORTED_LOCALES:
            assert locale_code in LOCALE_FLAGS
            assert LOCALE_FLAGS[locale_code]  # Not empty

    def test_all_supported_locales_have_names(self):
        """Test every supported locale has a display name."""
        for locale_code in SUPPORTED_LOCALES:
            assert locale_code in LOCALE_NAMES
            assert LOCALE_NAMES[locale_code]  # Not empty

    def test_flag_emoji_are_unicode(self):
        """Test flag emoji are proper Unicode regional indicators."""
        for _locale_code, flag in LOCALE_FLAGS.items():
            # Flag emoji are 4 bytes (2 regional indicator symbols)
            assert isinstance(flag, str)
            assert len(flag) == 2  # Two unicode characters (regional indicators)

    def test_locale_names_are_non_empty_strings(self):
        """Test locale display names are non-empty strings."""
        for _locale_code, name in LOCALE_NAMES.items():
            assert isinstance(name, str)
            assert len(name) > 0
            assert name.strip() == name  # No leading/trailing whitespace

    def test_specific_flag_mappings(self):
        """Test specific flag emoji are correct."""
        # Spot check a few important ones
        assert LOCALE_FLAGS["en_US"] == "🇺🇸"
        assert LOCALE_FLAGS["en_CA"] == "🇨🇦"
        assert LOCALE_FLAGS["fr_CA"] == "🇨🇦"
        assert LOCALE_FLAGS["sv_SE"] == "🇸🇪"
        assert LOCALE_FLAGS["de_DE"] == "🇩🇪"
        assert LOCALE_FLAGS["de_CH"] == "🇨🇭"

    def test_specific_name_mappings(self):
        """Test specific display names are correct."""
        # Spot check a few important ones
        assert LOCALE_NAMES["en_US"] == "English (US)"
        assert LOCALE_NAMES["fr_CA"] == "Français (Canada)"
        assert LOCALE_NAMES["sv_SE"] == "Svenska (Sweden)"
        assert LOCALE_NAMES["de_DE"] == "Deutsch (Germany)"
        assert LOCALE_NAMES["de_CH"] == "Deutsch (Switzerland)"

    def test_canada_locales_same_flag(self):
        """Test Canadian locales share the same flag."""
        assert LOCALE_FLAGS["en_CA"] == LOCALE_FLAGS["fr_CA"]
        assert LOCALE_FLAGS["en_CA"] == "🇨🇦"

    def test_switzerland_locales_same_flag(self):
        """Test Swiss locales share the same flag."""
        assert LOCALE_FLAGS["de_CH"] == LOCALE_FLAGS["it_CH"]
        assert LOCALE_FLAGS["de_CH"] == "🇨🇭"


class TestGetLocaleDisplayName:
    """Test get_locale_display_name function."""

    def test_returns_flag_and_name(self):
        """Test function returns flag emoji + name for valid locales."""
        result = get_locale_display_name("en_US")
        assert result == "🇺🇸 English (US)"

        result = get_locale_display_name("fr_CA")
        assert result == "🇨🇦 Français (Canada)"

        result = get_locale_display_name("sv_SE")
        assert result == "🇸🇪 Svenska (Sweden)"

    def test_all_supported_locales(self):
        """Test function works for all supported locales."""
        for locale_code in SUPPORTED_LOCALES:
            result = get_locale_display_name(locale_code)
            # Should contain flag emoji (non-ASCII)
            assert any(ord(c) > 127 for c in result)
            # Should contain display name
            assert LOCALE_NAMES[locale_code] in result
            # Should start with flag emoji
            assert result.startswith(LOCALE_FLAGS[locale_code])

    def test_unknown_locale_fallback(self):
        """Test function returns locale code for unknown locales."""
        result = get_locale_display_name("unknown_XX")
        assert result == "unknown_XX"

        result = get_locale_display_name("invalid")
        assert result == "invalid"

    def test_format_includes_space(self):
        """Test flag and name are separated by space."""
        for locale_code in SUPPORTED_LOCALES:
            result = get_locale_display_name(locale_code)
            # Should be: "flag name" format
            assert result == f"{LOCALE_FLAGS[locale_code]} {LOCALE_NAMES[locale_code]}"

    def test_return_type(self):
        """Test function returns string."""
        for locale_code in SUPPORTED_LOCALES:
            result = get_locale_display_name(locale_code)
            assert isinstance(result, str)

    def test_case_sensitive(self):
        """Test function is case-sensitive for locale codes."""
        # Wrong case should fallback to locale code
        result = get_locale_display_name("EN_US")
        assert result == "EN_US"

        result = get_locale_display_name("en_us")
        assert result == "en_us"

    def test_empty_string(self):
        """Test function handles empty string."""
        result = get_locale_display_name("")
        assert result == ""

    def test_none_value(self):
        """Test function handles None gracefully."""
        # get_locale_display_name expects str, not None
        # Type checker would catch this, but test runtime behavior
        # The function returns None as fallback (from LOCALE_NAMES.get(None, None))
        result = get_locale_display_name(None)  # type: ignore[arg-type]
        assert result is None

    def test_specific_expected_outputs(self):
        """Test specific expected outputs for common locales."""
        expected = {
            "en_US": "🇺🇸 English (US)",
            "en_CA": "🇨🇦 English (Canada)",
            "fr_CA": "🇨🇦 Français (Canada)",
            "sv_SE": "🇸🇪 Svenska (Sweden)",
            "ru_RU": "🇷🇺 Русский (Russia)",
            "fi_FI": "🇫🇮 Suomi (Finland)",
            "cs_CZ": "🇨🇿 Čeština (Czech Republic)",
            "de_DE": "🇩🇪 Deutsch (Germany)",
            "de_CH": "🇨🇭 Deutsch (Switzerland)",
            "it_CH": "🇨🇭 Italiano (Switzerland)",
            "sk_SK": "🇸🇰 Slovenčina (Slovakia)",
            "lv_LV": "🇱🇻 Latviešu (Latvia)",
        }

        for locale_code, expected_output in expected.items():
            result = get_locale_display_name(locale_code)
            assert result == expected_output
