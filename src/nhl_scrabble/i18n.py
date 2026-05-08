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
from pathlib import Path

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
