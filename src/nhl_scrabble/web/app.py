"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError
from nhl_scrabble.config import Config
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

logger = logging.getLogger(__name__)

# Get paths relative to this module
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):  # type: ignore[misc]
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
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


@app.get("/favicon.svg")
async def favicon() -> HTMLResponse:
    """Serve favicon as SVG.

    Returns:
        SVG favicon with hockey emoji
    """
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <text y="0.9em" font-size="90">🏒</text>
</svg>"""
    return HTMLResponse(content=svg_content, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Serve home page.

    Args:
        request: FastAPI request object

    Returns:
        Rendered index.html template
    """
    if templates is None:
        # Fallback if templates not available
        return HTMLResponse(
            content="<h1>NHL Scrabble Analyzer</h1><p>Templates not configured. Visit <a href='/docs'>/docs</a> for API documentation.</p>",
            status_code=200,
        )
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/analyze")
async def analyze(
    top_players: Annotated[
        int, Query(ge=1, le=100, description="Number of top players to display")
    ] = 20,
    top_team_players: Annotated[
        int, Query(ge=1, le=30, description="Number of top players per team")
    ] = 5,
    use_cache: Annotated[bool, Query(description="Use cached API responses")] = True,
) -> JSONResponse:
    """Run NHL Scrabble analysis and return results as JSON.

    Args:
        top_players: Number of top-scoring players to include (1-100)
        top_team_players: Number of players per team to include (1-30)
        use_cache: Whether to use cached API responses for faster results

    Returns:
        JSON response containing analysis results including teams, divisions,
        conferences, and playoff standings

    Raises:
        HTTPException: 500 if analysis fails due to NHL API error
        HTTPException: 422 if parameters are out of range
    """
    try:
        # Create config from parameters
        config = Config.from_env()
        config.top_players_count = top_players
        config.top_team_players_count = top_team_players
        config.cache_enabled = use_cache
        config.output_format = "json"

        logger.info(
            f"Starting analysis: top_players={top_players}, "
            f"top_team_players={top_team_players}, use_cache={use_cache}"
        )

        # Initialize components
        api_client = NHLApiClient(
            timeout=config.api_timeout,
            retries=config.api_retries,
            rate_limit_delay=config.rate_limit_delay,
            backoff_factor=config.backoff_factor,
            max_backoff=config.max_backoff,
            cache_enabled=config.cache_enabled,
            cache_expiry=config.cache_expiry,
        )

        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)
        playoff_calculator = PlayoffCalculator()

        # Process all teams
        team_scores, all_players, failed_teams = team_processor.process_all_teams()

        if failed_teams:
            logger.warning(f"Failed to fetch {len(failed_teams)} teams: {failed_teams}")

        # Calculate standings
        division_standings = team_processor.calculate_division_standings(team_scores)
        conference_standings = team_processor.calculate_conference_standings(team_scores)
        playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

        # Convert dataclasses to dictionaries for JSON serialization
        teams_data = {
            abbrev: {
                "total": team.total,
                "players": [asdict(p) for p in team.players[:top_team_players]],
                "division": team.division,
                "conference": team.conference,
                "avg_per_player": team.avg_per_player,
            }
            for abbrev, team in team_scores.items()
        }

        # Sort players and get top N
        sorted_players = sorted(all_players, key=lambda p: p.full_score, reverse=True)
        top_players_data = [asdict(p) for p in sorted_players[:top_players]]

        divisions_data = {name: asdict(standing) for name, standing in division_standings.items()}

        conferences_data = {
            name: asdict(standing) for name, standing in conference_standings.items()
        }

        playoffs_data = {
            conf: [asdict(team) for team in teams_list]
            for conf, teams_list in playoff_standings.items()
        }

        # Build response
        response_data = {
            "metadata": {
                "version": __version__,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "parameters": {
                    "top_players": top_players,
                    "top_team_players": top_team_players,
                    "use_cache": use_cache,
                },
                "stats": {
                    "total_teams": len(team_scores),
                    "failed_teams": len(failed_teams),
                    "total_players": len(all_players),
                },
            },
            "teams": teams_data,
            "top_players": top_players_data,
            "divisions": divisions_data,
            "conferences": conferences_data,
            "playoffs": playoffs_data,
        }

        logger.info(
            f"Analysis complete: {len(team_scores)} teams, "
            f"{len(all_players)} players, {len(failed_teams)} failures"
        )

        return JSONResponse(content=response_data)

    except NHLApiError as e:
        logger.error(f"NHL API error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {e!s}",
        ) from e
