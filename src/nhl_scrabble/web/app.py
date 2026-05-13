"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

import gettext
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from nhl_scrabble import __version__
from nhl_scrabble.i18n import DEFAULT_LOCALE, LOCALES_DIR

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.responses import Response

# Get paths relative to this module
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Skip CSP for API documentation endpoints (Swagger UI/ReDoc need external resources)
        is_api_docs = request.url.path in ("/docs", "/redoc", "/openapi.json")

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Only apply strict CSP to non-documentation pages
        if not is_api_docs:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://assets.nhle.com https://flagcdn.com; "
                "font-src 'self'; "
                "connect-src 'self'"
            )

        return response


# Create FastAPI application
app = FastAPI(
    title="NHL Scrabble Analyzer",
    description="Analyze NHL player names by Scrabble score",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware (for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files (if directory exists)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Jinja2 templates (if directory exists)
templates: Jinja2Templates | None = None
if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # Enable Jinja2 i18n extension for template translations
    templates.env.add_extension("jinja2.ext.i18n")

    # Configure i18n with gettext using default locale
    try:
        default_translation = gettext.translation(
            "messages",
            localedir=str(LOCALES_DIR),
            languages=[DEFAULT_LOCALE],
        )
        templates.env.install_gettext_translations(default_translation, newstyle=True)  # type: ignore[attr-defined]
    except FileNotFoundError:
        # Fallback to NullTranslations if .mo files not found
        null_translation = gettext.NullTranslations()
        templates.env.install_gettext_translations(null_translation, newstyle=True)  # type: ignore[attr-defined]

    # Register custom filters
    from nhl_scrabble.web.utils.auto_link import auto_link

    templates.env.filters["auto_link"] = auto_link

# Store templates in app state for access by route handlers
app.state.templates = templates

# Register all routes
from nhl_scrabble.web.routes import register_routes

register_routes(app, templates)

__all__ = ["app"]
# Re-export routes for backward compatibility
from nhl_scrabble.web.routes.core import health  # noqa: F401
