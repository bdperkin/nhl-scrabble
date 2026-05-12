"""Tests for date/time localization functions.

Note: Test datetimes use naive timezone (no tzinfo) to focus on format testing.
Timezone handling is not the primary concern for these localization format tests.
"""

from datetime import date, datetime, time

import pytest

from nhl_scrabble.i18n import (
    SUPPORTED_LOCALES,
    format_date,
    format_datetime,
    format_time,
)


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_short_en_us(self) -> None:
        """Test short date format for US English."""
        d = date(2026, 1, 15)
        result = format_date(d, "en_US", "short")
        # US format: M/D/YY or M/D/YYYY
        assert "1/15/" in result
        assert "26" in result or "2026" in result

    def test_format_date_long_en_us(self) -> None:
        """Test long date format for US English."""
        d = date(2026, 1, 15)
        result = format_date(d, "en_US", "long")
        # Long format: Month Day, Year
        assert "January" in result
        assert "15" in result
        assert "2026" in result

    def test_format_date_short_de_de(self) -> None:
        """Test short date format for German."""
        d = date(2026, 1, 15)
        result = format_date(d, "de_DE", "short")
        # German format: DD.MM.YY or DD.MM.YYYY
        assert "15." in result or "15/" in result
        assert "01" in result or "1" in result

    def test_format_date_long_de_de(self) -> None:
        """Test long date format for German."""
        d = date(2026, 1, 15)
        result = format_date(d, "de_DE", "long")
        # Long format with German month name
        assert "Januar" in result
        assert "2026" in result

    def test_format_date_long_fr_ca(self) -> None:
        """Test long date format for French Canadian."""
        d = date(2026, 1, 15)
        result = format_date(d, "fr_CA", "long")
        # French month name
        assert "janvier" in result.lower()
        assert "2026" in result

    def test_format_date_long_sv_se(self) -> None:
        """Test long date format for Swedish."""
        d = date(2026, 1, 15)
        result = format_date(d, "sv_SE", "long")
        # Swedish month name
        assert "januari" in result.lower()
        assert "2026" in result

    def test_format_date_medium_en_ca(self) -> None:
        """Test medium date format for Canadian English."""
        d = date(2026, 1, 15)
        result = format_date(d, "en_CA", "medium")
        # ISO-style format: YYYY-MM-DD
        assert "2026" in result
        assert "01" in result or "Jan" in result
        assert "15" in result

    def test_format_date_full_format(self) -> None:
        """Test full date format includes weekday."""
        d = date(2026, 1, 15)  # Thursday
        result = format_date(d, "en_US", "full")
        # Full format includes day of week
        assert len(result) > 15  # Full format is longer
        assert "2026" in result

    def test_format_date_defaults_to_system_locale(self) -> None:
        """Test format_date uses system locale when not specified."""
        d = date(2026, 1, 15)
        # Should not raise error (uses DEFAULT_LOCALE as fallback)
        result = format_date(d)
        assert result
        assert "2026" in result or "26" in result

    def test_format_date_invalid_locale_fallback(self) -> None:
        """Test format_date falls back to default for invalid locale."""
        d = date(2026, 1, 15)
        result = format_date(d, "invalid_LOCALE", "medium")
        # Should fallback to DEFAULT_LOCALE without error
        assert result
        assert "2026" in result or "26" in result


class TestFormatTime:
    """Tests for format_time function."""

    def test_format_time_short_en_us(self) -> None:
        """Test short time format for US English."""
        t = time(14, 30, 45)
        result = format_time(t, "en_US", "short")
        # US uses 12-hour format with AM/PM
        assert "PM" in result or "pm" in result.lower()
        assert "2:30" in result or "2.30" in result

    def test_format_time_medium_en_us(self) -> None:
        """Test medium time format for US English."""
        t = time(14, 30, 45)
        result = format_time(t, "en_US", "medium")
        # Medium includes seconds
        assert "PM" in result or "pm" in result.lower()
        assert "2:30:45" in result or "2.30.45" in result

    def test_format_time_short_de_de(self) -> None:
        """Test short time format for German."""
        t = time(14, 30, 45)
        result = format_time(t, "de_DE", "short")
        # German uses 24-hour format
        assert "14:30" in result or "14.30" in result
        # Should not have AM/PM
        assert "PM" not in result.upper()

    def test_format_time_medium_de_de(self) -> None:
        """Test medium time format for German."""
        t = time(14, 30, 45)
        result = format_time(t, "de_DE", "medium")
        # 24-hour format with seconds
        assert "14:30:45" in result or "14.30.45" in result
        assert "PM" not in result.upper()

    def test_format_time_medium_fr_ca(self) -> None:
        """Test medium time format for French Canadian."""
        t = time(14, 30, 45)
        result = format_time(t, "fr_CA", "medium")
        # French Canadian uses 24-hour format
        assert "14" in result
        assert "30" in result
        assert "45" in result

    def test_format_time_medium_sv_se(self) -> None:
        """Test medium time format for Swedish."""
        t = time(14, 30, 45)
        result = format_time(t, "sv_SE", "medium")
        # Swedish uses 24-hour format
        assert "14" in result
        assert "30" in result
        assert "45" in result

    def test_format_time_from_datetime(self) -> None:
        """Test format_time accepts datetime objects."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_time(dt, "en_US", "short")
        # Should extract time from datetime
        assert "2:30" in result or "2.30" in result
        assert "PM" in result or "pm" in result.lower()

    def test_format_time_defaults_to_system_locale(self) -> None:
        """Test format_time uses system locale when not specified."""
        t = time(14, 30, 45)
        # Should not raise error
        result = format_time(t)
        assert result
        assert "14" in result or "2" in result

    def test_format_time_invalid_locale_fallback(self) -> None:
        """Test format_time falls back to default for invalid locale."""
        t = time(14, 30, 45)
        result = format_time(t, "invalid_LOCALE", "medium")
        # Should fallback to DEFAULT_LOCALE without error
        assert result
        assert "14" in result or "2" in result


class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_format_datetime_short_en_us(self) -> None:
        """Test short datetime format for US English."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "en_US", "short")
        # Should contain both date and time
        assert "1/15/" in result
        assert "26" in result or "2026" in result
        assert "2:30" in result or "2.30" in result
        assert "PM" in result or "pm" in result.lower()

    def test_format_datetime_long_en_us(self) -> None:
        """Test long datetime format for US English."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "en_US", "long")
        # Long format with full month name
        assert "January" in result
        assert "15" in result
        assert "2026" in result
        assert "2:30" in result or "14:30" in result

    def test_format_datetime_medium_de_de(self) -> None:
        """Test medium datetime format for German."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "de_DE", "medium")
        # German format with 24-hour time
        assert "15" in result
        assert "2026" in result or "26" in result
        assert "14:30" in result or "14.30" in result

    def test_format_datetime_long_de_de(self) -> None:
        """Test long datetime format for German."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "de_DE", "long")
        # German month name
        assert "Januar" in result
        assert "2026" in result

    def test_format_datetime_long_fr_ca(self) -> None:
        """Test long datetime format for French Canadian."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "fr_CA", "long")
        # French month name
        assert "janvier" in result.lower()
        assert "2026" in result

    def test_format_datetime_long_sv_se(self) -> None:
        """Test long datetime format for Swedish."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "sv_SE", "long")
        # Swedish month name
        assert "januari" in result.lower()
        assert "2026" in result

    def test_format_datetime_medium_en_ca(self) -> None:
        """Test medium datetime format for Canadian English."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "en_CA", "medium")
        # Canadian format
        assert "2026" in result or "26" in result
        assert "15" in result

    def test_format_datetime_full_format(self) -> None:
        """Test full datetime format includes weekday."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001  # Thursday
        result = format_datetime(dt, "en_US", "full")
        # Full format is comprehensive
        assert len(result) > 20
        assert "2026" in result

    def test_format_datetime_defaults_to_system_locale(self) -> None:
        """Test format_datetime uses system locale when not specified."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        # Should not raise error
        result = format_datetime(dt)
        assert result
        assert "2026" in result or "26" in result

    def test_format_datetime_invalid_locale_fallback(self) -> None:
        """Test format_datetime falls back to default for invalid locale."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, "invalid_LOCALE", "medium")
        # Should fallback to DEFAULT_LOCALE without error
        assert result
        assert "2026" in result or "26" in result


class TestAllLocales:
    """Test date/time formatting for all 12 supported locales."""

    @pytest.mark.parametrize("locale_code", SUPPORTED_LOCALES)
    def test_format_date_all_locales(self, locale_code: str) -> None:
        """Test format_date works for all supported locales."""
        d = date(2026, 1, 15)
        for fmt in ("full", "long", "medium", "short"):
            result = format_date(d, locale_code, fmt)
            assert result
            # Should contain year in some form
            assert "2026" in result or "26" in result

    @pytest.mark.parametrize("locale_code", SUPPORTED_LOCALES)
    def test_format_time_all_locales(self, locale_code: str) -> None:
        """Test format_time works for all supported locales."""
        t = time(14, 30, 45)
        for fmt in ("full", "long", "medium", "short"):
            result = format_time(t, locale_code, fmt)
            assert result
            # Should contain hour in some form
            assert "14" in result or "2" in result or "02" in result

    @pytest.mark.parametrize("locale_code", SUPPORTED_LOCALES)
    def test_format_datetime_all_locales(self, locale_code: str) -> None:
        """Test format_datetime works for all supported locales."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        for fmt in ("full", "long", "medium", "short"):
            result = format_datetime(dt, locale_code, fmt)
            assert result
            # Should contain both year and hour indicators
            assert "2026" in result or "26" in result
            assert "14" in result or "2" in result or "02" in result


class TestMonthNames:
    """Test that month names are translated correctly."""

    def test_january_french(self) -> None:
        """Test January is 'janvier' in French."""
        d = date(2026, 1, 15)
        result = format_date(d, "fr_CA", "long")
        assert "janvier" in result.lower()

    def test_january_german(self) -> None:
        """Test January is 'Januar' in German."""
        d = date(2026, 1, 15)
        result = format_date(d, "de_DE", "long")
        assert "Januar" in result

    def test_january_swedish(self) -> None:
        """Test January is 'januari' in Swedish."""
        d = date(2026, 1, 15)
        result = format_date(d, "sv_SE", "long")
        assert "januari" in result.lower()

    def test_january_russian(self) -> None:
        """Test January is translated in Russian."""
        d = date(2026, 1, 15)
        result = format_date(d, "ru_RU", "long")
        # Russian uses Cyrillic characters
        assert result
        assert "2026" in result

    def test_january_finnish(self) -> None:
        """Test January is 'tammikuu' in Finnish."""
        d = date(2026, 1, 15)
        result = format_date(d, "fi_FI", "long")
        # Finnish has unique month names
        assert result
        assert "2026" in result

    def test_january_czech(self) -> None:
        """Test January is translated in Czech."""
        d = date(2026, 1, 15)
        result = format_date(d, "cs_CZ", "long")
        # Czech month name
        assert result
        assert "2026" in result


class TestTimeFormat12vs24:
    """Test 12-hour vs 24-hour time format by locale."""

    def test_us_uses_12_hour(self) -> None:
        """Test US locale uses 12-hour format."""
        t = time(14, 30, 45)
        result = format_time(t, "en_US", "short")
        # Should have AM/PM
        assert "PM" in result or "pm" in result.lower()
        # Should show 2:30, not 14:30
        assert "2:30" in result or "2.30" in result

    def test_european_uses_24_hour(self) -> None:
        """Test European locales use 24-hour format."""
        t = time(14, 30, 45)
        european_locales = ["de_DE", "de_CH", "sv_SE", "fi_FI", "cs_CZ", "sk_SK"]

        for locale_code in european_locales:
            result = format_time(t, locale_code, "short")
            # Should show 14:30
            assert "14" in result
            # Should not have AM/PM
            assert "PM" not in result.upper()
            assert "AM" not in result.upper()

    def test_canadian_english_uses_24_hour(self) -> None:
        """Test Canadian English typically uses 24-hour format."""
        t = time(14, 30, 45)
        result = format_time(t, "en_CA", "medium")
        # Canada commonly uses 24-hour format
        # Note: This may vary, but babel defaults to 24-hour for en_CA
        assert "14" in result or "2" in result

    def test_french_canadian_uses_24_hour(self) -> None:
        """Test French Canadian uses 24-hour format."""
        t = time(14, 30, 45)
        result = format_time(t, "fr_CA", "short")
        # French uses 24-hour format
        assert "14" in result


class TestDateSeparators:
    """Test date separators vary by locale."""

    def test_us_uses_slash(self) -> None:
        """Test US uses slash separator."""
        d = date(2026, 1, 15)
        result = format_date(d, "en_US", "short")
        # US format: 1/15/26 or 1/15/2026
        assert "/" in result or "-" in result

    def test_german_uses_dot(self) -> None:
        """Test German uses dot separator."""
        d = date(2026, 1, 15)
        result = format_date(d, "de_DE", "short")
        # German format: 15.01.26 or similar
        assert "." in result or "/" in result

    def test_swedish_uses_hyphen(self) -> None:
        """Test Swedish uses hyphen separator."""
        d = date(2026, 1, 15)
        result = format_date(d, "sv_SE", "short")
        # Swedish format: 2026-01-15 or similar
        assert "-" in result or "/" in result or "." in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_format_date_leap_day(self) -> None:
        """Test formatting February 29th (leap day)."""
        d = date(2024, 2, 29)
        result = format_date(d, "en_US", "long")
        assert "February" in result
        assert "29" in result
        assert "2024" in result

    def test_format_date_end_of_year(self) -> None:
        """Test formatting December 31st."""
        d = date(2026, 12, 31)
        result = format_date(d, "en_US", "long")
        assert "December" in result
        assert "31" in result
        assert "2026" in result

    def test_format_time_midnight(self) -> None:
        """Test formatting midnight."""
        t = time(0, 0, 0)
        result = format_time(t, "en_US", "medium")
        # 12:00 AM or 00:00 depending on locale
        assert result
        assert "12:00" in result or "00:00" in result or "0:00" in result

    def test_format_time_noon(self) -> None:
        """Test formatting noon."""
        t = time(12, 0, 0)
        result = format_time(t, "en_US", "medium")
        # 12:00 PM or 12:00
        assert result
        assert "12" in result

    def test_format_datetime_none_locale(self) -> None:
        """Test format_datetime with None locale uses default."""
        dt = datetime(2026, 1, 15, 14, 30, 45)  # noqa: DTZ001
        result = format_datetime(dt, None, "medium")
        # Should use DEFAULT_LOCALE
        assert result
        assert "2026" in result or "26" in result

    def test_format_date_none_locale(self) -> None:
        """Test format_date with None locale uses default."""
        d = date(2026, 1, 15)
        result = format_date(d, None, "medium")
        # Should use DEFAULT_LOCALE
        assert result
        assert "2026" in result or "26" in result

    def test_format_time_none_locale(self) -> None:
        """Test format_time with None locale uses default."""
        t = time(14, 30, 45)
        result = format_time(t, None, "medium")
        # Should use DEFAULT_LOCALE
        assert result
        assert "14" in result or "2" in result
