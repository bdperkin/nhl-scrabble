"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from nhl_scrabble import __version__
from nhl_scrabble.api import NHLApiClient, NHLApiError
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.processors import PlayoffCalculator, TeamProcessor
from nhl_scrabble.scoring import ScrabbleScorer

logger = logging.getLogger(__name__)

# Get paths relative to this module
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
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
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
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

# Cache storage (in-memory for now)
_analysis_cache: dict[str, dict[str, Any]] = {}


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""

    top_players: int = Field(
        default=20, ge=1, le=100, description="Number of top players to include"
    )
    top_team_players: int = Field(default=5, ge=1, le=30, description="Top players per team")
    use_cache: bool = Field(default=True, description="Use cached results if available")


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""

    timestamp: str
    cache_hit: bool
    top_players: list[dict[str, Any]]
    team_standings: list[dict[str, Any]]
    division_standings: dict[str, list[dict[str, Any]]]
    conference_standings: dict[str, list[dict[str, Any]]]
    playoff_bracket: dict[str, Any]
    stats: dict[str, Any]


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status including version and timestamp
    """
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Serve the main web interface.

    Args:
        request: FastAPI request object

    Returns:
        Rendered index.html template

    Raises:
        HTTPException: If templates not available
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


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


def _convert_players_to_dict(
    players: list[Any],
) -> list[dict[str, Any]]:
    """Convert PlayerScore objects to dict format for response.

    Args:
        players: List of PlayerScore objects

    Returns:
        List of player dictionaries
    """
    return [
        {
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "team": player.team,
            "score": player.full_score,
        }
        for player in players
    ]


def _convert_teams_to_dict(
    team_scores_dict: dict[str, TeamScore],
    top_team_players: int,
) -> list[dict[str, Any]]:
    """Convert TeamScore objects to dict format for response.

    Args:
        team_scores_dict: Dictionary of TeamScore objects
        top_team_players: Number of top players to include per team

    Returns:
        List of team dictionaries
    """
    teams_data = [
        {
            "abbrev": team_score.abbrev,
            "total_score": team_score.total,
            "avg_score": team_score.avg_per_player,
            "player_count": team_score.player_count,
            "division": team_score.division,
            "conference": team_score.conference,
            "top_players": [
                {
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "full_name": player.full_name,
                    "score": player.full_score,
                }
                for player in sorted(
                    team_score.players,
                    key=lambda x: x.full_score,
                    reverse=True,
                )[:top_team_players]
            ],
        }
        for team_score in team_scores_dict.values()
    ]
    teams_data.sort(key=lambda x: x["total_score"], reverse=True)  # type: ignore[arg-type, return-value]
    return teams_data


def _group_teams_by_grouping(
    teams_data: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Group teams by division and conference.

    Args:
        teams_data: List of team dictionaries

    Returns:
        Tuple of (divisions dict, conferences dict)
    """
    divisions: dict[str, list[dict[str, Any]]] = {}
    conferences: dict[str, list[dict[str, Any]]] = {}

    for team in teams_data:
        div = team["division"]
        conf = team["conference"]

        if div not in divisions:
            divisions[div] = []
        divisions[div].append(team)

        if conf not in conferences:
            conferences[conf] = []
        conferences[conf].append(team)

    return divisions, conferences


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_post(request: AnalysisRequest) -> dict[str, Any]:
    """Run NHL Scrabble analysis.

    Fetches current NHL roster data, calculates Scrabble scores for all players,
    generates standings and playoff bracket. Results are cached for 1 hour.

    Args:
        request: Analysis configuration

    Returns:
        Complete analysis results including players, standings, and playoff bracket

    Raises:
        HTTPException: If NHL API is unavailable or analysis fails
    """
    cache_key = f"{request.top_players}_{request.top_team_players}"

    # Check cache
    if request.use_cache and cache_key in _analysis_cache:
        cached = _analysis_cache[cache_key]
        cache_age = datetime.now(UTC) - datetime.fromisoformat(cached["cached_at"])

        if cache_age < timedelta(hours=1):
            return {
                **cached["data"],
                "cache_hit": True,
            }

    # Run analysis
    try:
        with NHLApiClient() as client:
            # Process all teams using TeamProcessor
            scorer = ScrabbleScorer()
            team_processor = TeamProcessor(client, scorer)
            team_scores_dict, all_players_objects, failed_teams = team_processor.process_all_teams()

            # Log failed teams
            if failed_teams:
                logger.warning("Failed to fetch %d teams: %s", len(failed_teams), failed_teams)

            # Convert player objects to dicts and sort by score
            all_players = _convert_players_to_dict(all_players_objects)
            all_players.sort(key=lambda x: x["score"], reverse=True)

            # Calculate playoff standings
            playoff_calc = PlayoffCalculator()
            playoff_standings = playoff_calc.calculate_playoff_standings(team_scores_dict)

            # Convert team scores to dict format for response
            teams_data = _convert_teams_to_dict(team_scores_dict, request.top_team_players)

            # Group by division and conference
            divisions, conferences = _group_teams_by_grouping(teams_data)

            # Calculate stats
            stats = {
                "total_players": len(all_players),
                "total_teams": len(teams_data),
                "highest_score": all_players[0]["score"] if all_players else 0,
                "lowest_score": all_players[-1]["score"] if all_players else 0,
                "avg_score": (
                    sum(p["score"] for p in all_players) / len(all_players) if all_players else 0
                ),
                "highest_team": teams_data[0]["abbrev"] if teams_data else None,
                "lowest_team": teams_data[-1]["abbrev"] if teams_data else None,
            }

            # Convert playoff standings to dict format
            playoff_bracket = {}
            for conference, teams in playoff_standings.items():
                playoff_bracket[conference] = [
                    {
                        "abbrev": team.abbrev,
                        "total": team.total,
                        "players": team.players,
                        "avg": team.avg,
                        "conference": team.conference,
                        "division": team.division,
                        "status_indicator": team.status_indicator,
                        "seed_type": team.seed_type,
                        "in_playoffs": team.in_playoffs,
                        "division_rank": team.division_rank,
                    }
                    for team in teams
                ]

            # Build response
            result = {
                "timestamp": datetime.now(UTC).isoformat(),
                "cache_hit": False,
                "top_players": all_players[: request.top_players],
                "team_standings": teams_data,
                "division_standings": divisions,
                "conference_standings": conferences,
                "playoff_bracket": playoff_bracket,
                "stats": stats,
            }

            # Cache result
            _analysis_cache[cache_key] = {
                "cached_at": datetime.now(UTC).isoformat(),
                "data": result,
            }

            return result

    except NHLApiError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {e!s}",
        ) from e


@app.get("/api/analyze", response_model=None)
async def analyze_get(
    request: Request,
    top_players: int = 20,
    top_team_players: int = 5,
    use_cache: bool = True,
) -> HTMLResponse | dict[str, Any]:
    """Run NHL Scrabble analysis (GET endpoint for HTMX).

    Args:
        request: FastAPI request object
        top_players: Number of top players to include
        top_team_players: Top players per team
        use_cache: Use cached results if available

    Returns:
        Analysis results as HTML or JSON

    Raises:
        HTTPException: If NHL API is unavailable or analysis fails
    """
    # Create request object
    analysis_request = AnalysisRequest(
        top_players=top_players,
        top_team_players=top_team_players,
        use_cache=use_cache,
    )

    # Get analysis data
    data = await analyze_post(analysis_request)

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx and templates is not None:
        # Return HTML fragment for HTMX
        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context={
                "request": request,
                "top_players": data["top_players"],
                "team_standings": data["team_standings"],
                "division_standings": data["division_standings"],
                "conference_standings": data["conference_standings"],
                "playoff_bracket": data["playoff_bracket"],
                "stats": data["stats"],
            },
        )

    # Return JSON for regular API calls
    return data


@app.get("/api/players/{player_id}")
async def get_player(player_id: int) -> dict[str, Any]:
    """Get details for a specific player.

    Args:
        player_id: NHL player ID

    Returns:
        Player details including score and team

    Raises:
        HTTPException: If player not found
    """
    # Note: PlayerScore model doesn't currently include player ID,
    # so this endpoint always returns 404. This needs to be enhanced
    # in a future task to include player IDs in the data model.
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found")


@app.get("/api/teams/{team_abbrev}")
async def get_team(team_abbrev: str) -> dict[str, Any]:
    """Get details for a specific team.

    Args:
        team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')

    Returns:
        Team details including score and roster

    Raises:
        HTTPException: If team not found
    """
    # Search cache for team
    for cached in _analysis_cache.values():
        for team in cached["data"]["team_standings"]:
            if team["abbrev"].upper() == team_abbrev.upper():
                return team  # type: ignore[no-any-return]

    raise HTTPException(status_code=404, detail=f"Team {team_abbrev} not found")


@app.delete("/api/cache/clear")
async def clear_cache() -> dict[str, str]:
    """Clear the analysis cache.

    Returns:
        Confirmation message
    """
    _analysis_cache.clear()
    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/cache/stats")
async def cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Cache statistics including size and entries
    """
    entries = []
    for key, cached in _analysis_cache.items():
        cache_age = datetime.now(UTC) - datetime.fromisoformat(cached["cached_at"])
        entries.append(
            {
                "key": key,
                "cached_at": cached["cached_at"],
                "age_seconds": cache_age.total_seconds(),
                "expires_in_seconds": max(0, 3600 - cache_age.total_seconds()),
            }
        )

    return {
        "size": len(_analysis_cache),
        "entries": entries,
    }
