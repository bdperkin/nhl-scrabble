"""Locale handling utilities for the web application.

This module provides functions for detecting and configuring locales in the FastAPI application.
"""

from __future__ import annotations

import gettext
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nhl_scrabble.i18n import DEFAULT_LOCALE, LOCALES_DIR, SUPPORTED_LOCALES

if TYPE_CHECKING:
    from fastapi import Request
    from fastapi.templating import Jinja2Templates


def get_request_locale(request: Request) -> str:
    """Detect locale from request.

    Priority order:
    1. ?lang= query parameter
    2. Accept-Language header
    3. Default locale (en_US)

    Args:
        request: FastAPI request object

    Returns:
        Locale code (e.g., 'en_US', 'fr_CA')
    """
    # Try URL parameter first
    lang_param = request.query_params.get("lang")
    if lang_param and lang_param in SUPPORTED_LOCALES:
        return str(lang_param)

    # Try Accept-Language header
    accept_language = request.headers.get("Accept-Language", "")
    if accept_language:
        # Parse Accept-Language header (format: "en-US,en;q=0.9,fr-CA;q=0.8")
        for lang in accept_language.split(","):
            # Extract language code before quality value
            lang_code = lang.split(";")[0].strip()

            # Convert from HTTP format (en-US) to our format (en_US)
            normalized = lang_code.replace("-", "_")

            # Check if this locale is supported
            if normalized in SUPPORTED_LOCALES:
                return str(normalized)

            # Try language part only (e.g., "en" from "en-GB")
            if "_" not in normalized and "-" not in lang_code:
                # Find first matching locale with this language
                for locale in SUPPORTED_LOCALES:
                    if locale.startswith(normalized + "_"):
                        return locale

    # Default locale
    return "en_US"


def setup_template_locale(request: Request, templates: Jinja2Templates | None = None) -> dict[str, Any]:
    """Set up template context with locale-specific translator.

    Args:
        request: FastAPI request object
        templates: Jinja2 templates instance (optional)

    Returns:
        Template context with locale and gettext function
    """
    locale = get_request_locale(request)

    # Update Jinja2 environment with locale-specific translator
    if templates:
        try:
            translation = gettext.translation(
                "messages",
                localedir=str(LOCALES_DIR),
                languages=[locale],
            )
            templates.env.install_gettext_translations(translation, newstyle=True)  # type: ignore[attr-defined]
        except FileNotFoundError:
            # Fallback to NullTranslations if locale not found
            null_translation = gettext.NullTranslations()
            templates.env.install_gettext_translations(null_translation, newstyle=True)  # type: ignore[attr-defined]

    return {
        "request": request,
        "locale": locale,
        "get_locale": lambda: locale,
        "SUPPORTED_LOCALES": SUPPORTED_LOCALES,
    }
