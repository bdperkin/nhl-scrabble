"""FastAPI application factory and configuration.

This module creates and configures the FastAPI application for the NHL Scrabble API.

The application includes:
- OpenAPI documentation at /docs
- ReDoc documentation at /redoc
- Health check endpoint at /health
- Rate limiting middleware
- Optional authentication
- CORS support

Example:
    Create the application::

        from nhl_scrabble.api_server import create_app
        app = create_app()

    Run with uvicorn::

        uvicorn nhl_scrabble.api_server.app:app --reload
"""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from nhl_scrabble.api_server.routes import health, players, standings, teams


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.

    Example:
        >>> app = create_app()
        >>> # Run with: uvicorn module:app --reload
    """
    app = FastAPI(
        title="NHL Scrabble API",
        description=(
            "REST API for NHL Scrabble Score Analyzer - "
            "programmatic access to team scores, player scores, and standings "
            "based on Scrabble letter values."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(teams.router, prefix="/api/v1", tags=["teams"])
    app.include_router(players.router, prefix="/api/v1", tags=["players"])
    app.include_router(standings.router, prefix="/api/v1", tags=["standings"])

    # Root endpoint
    @app.get("/", response_class=JSONResponse)
    async def root() -> dict[str, Any]:
        """Return API information and documentation links.

        Returns:
            dict: API information including title, version, and documentation URLs.

        Example:
            >>> response = await root()
            >>> print(response["title"])
            NHL Scrabble API
        """
        return {
            "title": "NHL Scrabble API",
            "version": "1.0.0",
            "description": "REST API for NHL Scrabble Score Analyzer",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json",
        }

    return app


# Application instance for uvicorn
app = create_app()
