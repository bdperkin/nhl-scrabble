"""Route registration for the web application.

This module imports all route modules and provides a function to register them with the FastAPI app.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates


def register_routes(app: FastAPI, templates: Jinja2Templates | None) -> None:
    """Register all route modules with the FastAPI app.

    Args:
        app: FastAPI application instance
        templates: Jinja2 templates instance (optional)
    """
    # Import route modules
    from nhl_scrabble.web.routes import (  # noqa: PLC0415 - Avoid circular imports
        api,
        cache,
        conferences,
        core,
        divisions,
        nationalities,
        players,
        positions,
        standings,
        static,
        teams,
    )

    # Register core routes (/, /health, /api/analyze POST)
    app.include_router(core.router, tags=["core"])

    # Register player routes
    # Note: These routes need templates parameter, so we need to wrap them
    # We'll use dependency injection in each route to get templates

    # For routes that need templates, we need to modify the signature
    # to accept templates as a dependency. Since we can't easily do that
    # with the current structure, we'll pass templates via dependency override

    # Store templates in app state for access in route handlers
    app.state.templates = templates

    # Include all routers
    app.include_router(players.router, tags=["players"])
    app.include_router(teams.router, tags=["teams"])
    app.include_router(divisions.router, tags=["divisions"])
    app.include_router(conferences.router, tags=["conferences"])
    app.include_router(positions.router, tags=["positions"])
    app.include_router(nationalities.router, tags=["nationalities"])
    app.include_router(standings.router, tags=["standings"])
    app.include_router(static.router, tags=["static"])
    app.include_router(cache.router, tags=["cache"])
    app.include_router(api.router, tags=["api"])


__all__ = ["register_routes"]
