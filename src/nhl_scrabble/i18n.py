"""Internationalization utilities for NHL Scrabble.

This module provides utilities for translation and localization support across
all user-facing components (CLI, Web, TUI). Uses gettext for translations and
locale-specific formatting for numbers and dates.

Supported Locales:
    12 locales covering major hockey markets:
    - en_US: English (United States) - Default
    - en_CA: English (Canada)
    - fr_CA: French (Canada)
    - sv_SE: Swedish (Sweden)
    - ru_RU: Russian (Russia)
    - fi_FI: Finnish (Finland)
    - cs_CZ: Czech (Czechia)
    - de_DE: German (Germany)
    - de_CH: German (Switzerland)
    - it_CH: Italian (Switzerland)
    - sk_SK: Slovak (Slovakia)
    - lv_LV: Latvian (Latvia)

Usage:
    Basic translation::

        from nhl_scrabble.i18n import get_translator
        _ = get_translator("fr_CA")
        print(_("Hello, World!"))
        # Output: Bonjour, le monde! (once translations are compiled)

    Environment variable override::

        import os
        os.environ["NHL_SCRABBLE_LANG"] = "sv_SE"
        _ = get_translator()
        print(_("Team"))
        # Output: Lag (once translations are compiled)

    Number formatting:
        >>> from nhl_scrabble.i18n import format_number
        >>> format_number(1234.56, "en_US")
        '1,234.56'
        >>> format_number(1234.56, "de_DE")
        '1.234,56'

Environment Variables:
    NHL_SCRABBLE_LANG: Override system locale (e.g., "fr_CA", "sv_SE")
"""

import contextlib
import gettext
import locale
import os
import sys
from collections.abc import Callable
from datetime import date, datetime, time
from pathlib import Path

from babel.dates import format_date as babel_format_date
from babel.dates import format_datetime as babel_format_datetime
from babel.dates import format_time as babel_format_time

# Supported locales (12 total covering major hockey markets)
SUPPORTED_LOCALES = [
    "en_US",  # English - United States (default)
    "en_CA",  # English - Canada
    "fr_CA",  # French - Canada
    "sv_SE",  # Swedish - Sweden
    "ru_RU",  # Russian - Russia
    "fi_FI",  # Finnish - Finland
    "cs_CZ",  # Czech - Czechia
    "de_DE",  # German - Germany
    "de_CH",  # German - Switzerland
    "it_CH",  # Italian - Switzerland
    "sk_SK",  # Slovak - Slovakia
    "lv_LV",  # Latvian - Latvia
]

# Default locale
DEFAULT_LOCALE = "en_US"

# Locales directory
LOCALES_DIR = Path(__file__).parent / "locales"


def get_system_locale() -> str:
    """Detect system locale.

    Attempts to detect the system's default locale and returns it if supported.
    Falls back to DEFAULT_LOCALE (en_US) if detection fails or locale is unsupported.

    Returns:
        Locale code (e.g., "en_US") or DEFAULT_LOCALE if detection fails.

    Examples:
        >>> get_system_locale()  # doctest: +SKIP
        'en_US'

    Notes:
        - Reads from environment variables (LANG, LC_ALL, LC_CTYPE, LANGUAGE)
        - Only returns locales in SUPPORTED_LOCALES list
        - Safe to call multiple times (no side effects)
        - On Windows, avoids setlocale() which can fail or behave unexpectedly
    """
    with contextlib.suppress(ValueError, TypeError, locale.Error):
        # Try environment variables in order of precedence
        # This replaces the deprecated locale.getdefaultlocale()
        for env_var in ("LC_ALL", "LC_CTYPE", "LANG", "LANGUAGE"):
            if localename := os.environ.get(env_var):
                # Parse locale name (e.g., "en_US.UTF-8" -> "en_US")
                system_locale = localename.split(".")[0].split("@")[0]
                if system_locale and system_locale in SUPPORTED_LOCALES:
                    return system_locale

        # Windows: Skip setlocale("") which can fail or behave unexpectedly
        # Just return DEFAULT_LOCALE if env vars not set
        if sys.platform == "win32":
            return DEFAULT_LOCALE

        # Unix/macOS: Fallback to locale.getlocale() (requires setlocale first)
        saved_locale = locale.setlocale(locale.LC_CTYPE)
        try:
            locale.setlocale(locale.LC_CTYPE, "")
            loc_tuple = locale.getlocale()
            if loc_tuple[0] and loc_tuple[0] in SUPPORTED_LOCALES:
                return loc_tuple[0]
        finally:
            locale.setlocale(locale.LC_CTYPE, saved_locale)

    return DEFAULT_LOCALE


def get_translator(locale_code: str | None = None) -> Callable[[str], str]:
    """Get translator function for a locale.

    Returns a translation function (gettext) configured for the specified locale.
    If translations are not found, returns an identity function (no translation)
    to allow the application to work gracefully without compiled translations.

    Args:
        locale_code: Locale code (e.g., "fr_CA"). If None, uses NHL_SCRABBLE_LANG
            environment variable or system locale (in that order).

    Returns:
        Translation function that takes a string and returns its translation.
        Returns identity function (lambda s: s) if translations not found.

    Examples:
        >>> _ = get_translator("fr_CA")  # doctest: +SKIP
        >>> _("Hello, World!")  # doctest: +SKIP
        'Bonjour, le monde!'

        >>> _ = get_translator()  # Uses system locale  # doctest: +SKIP
        >>> _("Analyzing NHL rosters...")  # doctest: +SKIP
        'Analyse des effectifs de la LNH...'

        >>> import os  # doctest: +SKIP
        >>> os.environ["NHL_SCRABBLE_LANG"] = "sv_SE"  # doctest: +SKIP
        >>> _ = get_translator()  # Uses env var  # doctest: +SKIP
        >>> _("Team")  # doctest: +SKIP
        'Lag'

        >>> _ = get_translator("invalid_LOCALE")  # doctest: +SKIP
        >>> _("Test")  # Falls back to identity  # doctest: +SKIP
        'Test'

    Notes:
        - Priority: explicit parameter > NHL_SCRABBLE_LANG > system locale
        - Validates locale against SUPPORTED_LOCALES
        - Graceful fallback if translations missing (returns original string)
        - No exceptions raised for missing translations
    """
    # Priority: explicit parameter > env var > system locale
    if locale_code is None:
        locale_code = os.getenv("NHL_SCRABBLE_LANG")
    if locale_code is None:
        locale_code = get_system_locale()

    # Validate locale
    if locale_code not in SUPPORTED_LOCALES:
        locale_code = DEFAULT_LOCALE

    try:
        translation = gettext.translation(
            "messages",
            localedir=str(LOCALES_DIR),
            languages=[locale_code],
        )
        return translation.gettext
    except FileNotFoundError:
        # Fallback to identity function (no translation)
        # This allows the app to work even without compiled translations
        return lambda s: s


def format_number(number: float, locale_code: str | None = None) -> str:
    """Format number according to locale conventions.

    Formats a number using locale-specific separators and decimal points.
    Falls back to standard formatting if locale is unavailable.

    Args:
        number: Number to format.
        locale_code: Locale code for formatting. If None, uses system locale.

    Returns:
        Formatted number string with locale-appropriate separators.

    Examples:
        >>> format_number(1234.56, "en_US")  # doctest: +SKIP
        '1,234.56'

        >>> format_number(1234.56, "de_DE")  # doctest: +SKIP
        '1.234,56'

        >>> format_number(1234.56, "fr_CA")  # doctest: +SKIP
        '1 234,56'

        >>> format_number(1234.56, "invalid")  # Fallback
        '1234.56'

    Notes:
        - Uses locale.format_string() for formatting
        - Falls back to f"{number:.2f}" if locale unavailable
        - Always formats to 2 decimal places
        - Thread-safe (sets locale only for this operation)
        - On Windows, falls back to standard formatting if locale unavailable

    Warning:
        May not work correctly in multi-threaded environments due to
        locale.setlocale() being process-wide. Consider using babel.numbers
        for production multi-threaded applications.
    """
    if locale_code is None:
        locale_code = get_system_locale()

    # Windows: setlocale() can fail with locale names, use fallback
    if sys.platform == "win32":
        return f"{number:.2f}"

    try:
        # Save current locale
        current = locale.setlocale(locale.LC_NUMERIC)
        try:
            locale.setlocale(locale.LC_NUMERIC, locale_code)
            return locale.format_string("%.2f", number, grouping=True)
        finally:
            # Restore previous locale
            locale.setlocale(locale.LC_NUMERIC, current)
    except (locale.Error, ValueError, OSError):
        # Fallback to standard formatting
        return f"{number:.2f}"


def format_date(
    date_obj: date,
    locale_code: str | None = None,
    format: str = "medium",  # noqa: A002
) -> str:
    """Format date according to locale conventions.

    Formats a date using locale-specific conventions for date order, separators,
    and month names. Uses babel.dates for reliable cross-platform formatting.

    Args:
        date_obj: Date object to format.
        locale_code: Locale code for formatting. If None, uses system locale.
        format: Format length - 'full', 'long', 'medium', or 'short'.

    Returns:
        Formatted date string with locale-appropriate conventions.

    Examples:
        >>> from datetime import date
        >>> d = date(2026, 1, 15)
        >>> format_date(d, "en_US", "short")  # doctest: +SKIP
        '1/15/26'

        >>> format_date(d, "de_DE", "long")  # doctest: +SKIP
        '15. Januar 2026'

        >>> format_date(d, "fr_CA", "medium")  # doctest: +SKIP
        '15 janv. 2026'

    Notes:
        - 'full': Wednesday, January 15, 2026
        - 'long': January 15, 2026
        - 'medium': Jan 15, 2026
        - 'short': 1/15/26
        - Month names are translated according to locale
        - Date order (MM/DD vs DD/MM) follows locale conventions
        - Thread-safe (babel.dates is thread-safe)
    """
    if locale_code is None:
        locale_code = get_system_locale()

    # Validate locale, fallback to default if invalid
    if locale_code not in SUPPORTED_LOCALES:
        locale_code = DEFAULT_LOCALE

    return babel_format_date(date_obj, format=format, locale=locale_code)  # type: ignore[no-any-return]


def format_time(
    time_obj: datetime | time,
    locale_code: str | None = None,
    format: str = "medium",  # noqa: A002
) -> str:
    """Format time according to locale conventions.

    Formats a time using locale-specific conventions for 12/24-hour format
    and time separators. Uses babel.dates for reliable cross-platform formatting.

    Args:
        time_obj: Time or datetime object to format.
        locale_code: Locale code for formatting. If None, uses system locale.
        format: Format length - 'full', 'long', 'medium', or 'short'.

    Returns:
        Formatted time string with locale-appropriate conventions.

    Examples:
        >>> from datetime import time
        >>> t = time(14, 30, 45)
        >>> format_time(t, "en_US", "short")  # doctest: +SKIP
        '2:30 PM'

        >>> format_time(t, "de_DE", "medium")  # doctest: +SKIP
        '14:30:45'

        >>> format_time(t, "fr_CA", "long")  # doctest: +SKIP
        '14:30:45 UTC'

    Notes:
        - 'full': 2:30:45 PM Eastern Standard Time
        - 'long': 2:30:45 PM EST
        - 'medium': 2:30:45 PM
        - 'short': 2:30 PM
        - US locales typically use 12-hour format with AM/PM
        - European locales typically use 24-hour format
        - Thread-safe (babel.dates is thread-safe)
    """
    if locale_code is None:
        locale_code = get_system_locale()

    # Validate locale, fallback to default if invalid
    if locale_code not in SUPPORTED_LOCALES:
        locale_code = DEFAULT_LOCALE

    return babel_format_time(time_obj, format=format, locale=locale_code)  # type: ignore[no-any-return]


def format_datetime(
    dt: datetime,
    locale_code: str | None = None,
    format: str = "medium",  # noqa: A002
) -> str:
    """Format datetime according to locale conventions.

    Formats a datetime using locale-specific conventions for date order,
    time format, separators, and month names. Uses babel.dates for reliable
    cross-platform formatting.

    Args:
        dt: Datetime object to format.
        locale_code: Locale code for formatting. If None, uses system locale.
        format: Format length - 'full', 'long', 'medium', or 'short'.

    Returns:
        Formatted datetime string with locale-appropriate conventions.

    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2026, 1, 15, 14, 30, 45)
        >>> format_datetime(dt, "en_US", "short")  # doctest: +SKIP
        '1/15/26, 2:30 PM'

        >>> format_datetime(dt, "de_DE", "long")  # doctest: +SKIP
        '15. Januar 2026 um 14:30:45 MEZ'

        >>> format_datetime(dt, "fr_CA", "medium")  # doctest: +SKIP
        '15 janv. 2026, 14:30:45'

    Notes:
        - 'full': Wednesday, January 15, 2026 at 2:30:45 PM Eastern Standard Time
        - 'long': January 15, 2026 at 2:30:45 PM EST
        - 'medium': Jan 15, 2026, 2:30:45 PM
        - 'short': 1/15/26, 2:30 PM
        - Combines date and time formatting per locale
        - Month names and weekday names are translated
        - Thread-safe (babel.dates is thread-safe)
        - Timezone handling depends on datetime object's tzinfo
    """
    if locale_code is None:
        locale_code = get_system_locale()

    # Validate locale, fallback to default if invalid
    if locale_code not in SUPPORTED_LOCALES:
        locale_code = DEFAULT_LOCALE

    return babel_format_datetime(dt, format=format, locale=locale_code)  # type: ignore[no-any-return]


def _(message: str) -> str:
    """Translate a message using the current locale.

    This is a convenience function that uses the system locale for translation.
    It's a simpler alternative to calling get_translator() when you don't need
    explicit locale control.

    Args:
        message: String to translate.

    Returns:
        Translated string, or original if translation not available.

    Examples:
        >>> from nhl_scrabble.i18n import _
        >>> _("Hello, World!")  # doctest: +SKIP
        'Bonjour, le monde!'  # If locale is fr_CA and translation exists

        >>> _("Team")  # doctest: +SKIP
        'Lag'  # If locale is sv_SE and translation exists

    Notes:
        - Uses NHL_SCRABBLE_LANG environment variable if set
        - Falls back to system locale if env var not set
        - Returns original string if translation not found
        - For explicit locale control, use get_translator(locale_code) instead
    """
    translator = get_translator()
    return translator(message)
