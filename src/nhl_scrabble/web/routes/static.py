"""Static file routes.

This module contains routes for serving static files like favicons and robots.txt.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

router = APIRouter()

# Get static directory path
WEB_DIR = Path(__file__).parent.parent
STATIC_DIR = WEB_DIR / "static"


@router.get("/favicon.svg")
async def favicon() -> HTMLResponse:
    """Serve favicon as SVG.

    Returns:
        SVG favicon with hockey emoji
    """
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text y="0.9em" font-size="90">🏒</text>
</svg>"""
    return HTMLResponse(content=svg_content, media_type="image/svg+xml")


@router.get("/favicon.ico")
async def favicon_ico() -> HTMLResponse:
    """Serve favicon.ico (redirects to SVG).

    Modern browsers support SVG favicons, so we return the same SVG content
    with image/svg+xml media type instead of generating an ICO file.

    Returns:
        SVG favicon with hockey emoji
    """
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text y="0.9em" font-size="90">🏒</text>
</svg>"""
    return HTMLResponse(content=svg_content, media_type="image/svg+xml")


@router.get("/robots.txt")
async def robots_txt() -> FileResponse:
    """Serve robots.txt file.

    Returns:
        robots.txt file for web crawlers
    """
    robots_file = STATIC_DIR / "robots.txt"
    return FileResponse(robots_file, media_type="text/plain")
