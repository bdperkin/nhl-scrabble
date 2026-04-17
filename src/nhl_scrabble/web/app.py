"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from nhl_scrabble import __version__

# Get paths relative to this module
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

# Create FastAPI application
app = FastAPI(
    title="NHL Scrabble Analyzer",
    description="Analyze NHL player names by Scrabble score",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files (if directory exists)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Jinja2 templates (if directory exists)
templates: Jinja2Templates | None = None
if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status including version and timestamp
    """
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint placeholder.

    Returns:
        Simple message directing to docs
    """
    return {
        "message": "NHL Scrabble Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }
