"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from nhl_scrabble import __version__
from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

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

# Cache for analysis results (in-memory cache with expiration)
analysis_cache: dict[str, dict[str, Any]] = {}


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
        int, Query(ge=1, le=30, description="Number of top players per team to display")
    ] = 5,
    use_cache: Annotated[bool, Query(description="Use cached results if available")] = True,
) -> dict[str, Any]:
    """Run NHL Scrabble analysis.

    Fetches current NHL roster data, calculates Scrabble scores for all players,
    and generates comprehensive reports including team standings, playoff brackets,
    and statistics.

    Args:
        top_players: Number of top-scoring players to include (1-100)
        top_team_players: Number of top players per team to include (1-30)
        use_cache: Whether to use cached results (1 hour expiration)

    Returns:
        Analysis results including top players, team standings, conference standings,
        playoff bracket, and statistics

    Raises:
        HTTPException: If analysis fails due to API errors or other issues
    """
    # Generate cache key
    cache_key = f"{top_players}_{top_team_players}"

    # Check cache
    if use_cache and cache_key in analysis_cache:
        cached = analysis_cache[cache_key]
        cache_age = datetime.now(timezone.utc) - cached["timestamp"]
        if cache_age < timedelta(hours=1):  # 1 hour cache expiration
            return cached["data"]  # type: ignore[no-any-return]

    try:
        # Initialize scorer
        scorer = ScrabbleScorer()

        # Fetch NHL data
        with NHLApiClient() as client:
            # Process teams
            processor = TeamProcessor(api_client=client, scorer=scorer)
            teams_dict, _all_players, _failed_teams = processor.process_all_teams()

        # Calculate playoff bracket
        playoff_calc = PlayoffCalculator()
        playoff_standings = playoff_calc.calculate_playoff_standings(teams_dict)

        # Get sorted list of all teams for statistics
        all_teams = list(teams_dict.values())

        # Build response with all analysis data
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache_key": cache_key,
            "top_players": top_players,
            "top_team_players": top_team_players,
            "teams": [
                {
                    "abbreviation": team.abbrev,
                    "division": team.division,
                    "conference": team.conference,
                    "total_score": team.total,
                    "average_score": team.avg_per_player,
                    "roster_size": team.player_count,
                    "top_players": [
                        {
                            "name": player.full_name,
                            "score": player.full_score,
                        }
                        for player in team.players[:top_team_players]
                    ],
                }
                for team in all_teams
            ],
            "playoff_bracket": {
                "eastern_conference": [
                    {
                        "abbreviation": team.abbrev,
                        "total_score": team.total,
                        "in_playoffs": team.in_playoffs,
                        "status": team.status_indicator,
                    }
                    for team in playoff_standings.get("Eastern", [])
                ],
                "western_conference": [
                    {
                        "abbreviation": team.abbrev,
                        "total_score": team.total,
                        "in_playoffs": team.in_playoffs,
                        "status": team.status_indicator,
                    }
                    for team in playoff_standings.get("Western", [])
                ],
            },
            "statistics": {
                "total_teams": len(all_teams),
                "total_players": sum(team.player_count for team in all_teams),
                "highest_team_score": max((team.total for team in all_teams), default=0),
                "lowest_team_score": min((team.total for team in all_teams), default=0),
                "average_team_score": (
                    sum(team.total for team in all_teams) / len(all_teams) if all_teams else 0
                ),
            },
        }

        # Cache result
        analysis_cache[cache_key] = {
            "timestamp": datetime.now(timezone.utc),
            "data": result,
        }

        return result

    except NHLApiError as e:
        raise HTTPException(status_code=503, detail=f"NHL API error: {e!s}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e


@app.get("/api/cache/clear")
async def clear_cache() -> dict[str, Any]:
    """Clear the analysis cache.

    Returns:
        Confirmation message with number of entries cleared
    """
    count = len(analysis_cache)
    analysis_cache.clear()
    return {
        "message": "Cache cleared",
        "entries_cleared": count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/teams/{team_abbrev}")
async def get_team(team_abbrev: str) -> dict[str, Any]:
    """Get details for a specific team.

    Args:
        team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL', 'BOS')

    Returns:
        Team details including roster and Scrabble scores

    Raises:
        HTTPException: If team not found or API error occurs
    """
    try:
        # Initialize scorer
        scorer = ScrabbleScorer()

        # Fetch NHL data and process all teams to find the requested one
        with NHLApiClient() as client:
            processor = TeamProcessor(api_client=client, scorer=scorer)
            teams_dict, _all_players, _failed_teams = processor.process_all_teams()

            # Find the requested team
            team_score = None
            for abbrev, team in teams_dict.items():
                if abbrev.upper() == team_abbrev.upper():
                    team_score = team
                    break

        if not team_score:
            raise HTTPException(status_code=404, detail=f"Team not found: {team_abbrev}")

        return {
            "abbreviation": team_score.abbrev,
            "division": team_score.division,
            "conference": team_score.conference,
            "total_score": team_score.total,
            "average_score": team_score.avg_per_player,
            "roster_size": team_score.player_count,
            "players": [
                {
                    "name": player.full_name,
                    "score": player.full_score,
                }
                for player in team_score.players
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except NHLApiError as e:
        raise HTTPException(status_code=503, detail=f"NHL API error: {e!s}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch team: {e!s}") from e


@app.get("/api/players/{player_id}")
async def get_player(player_id: int) -> dict[str, Any]:  # noqa: ARG001
    """Get details for a specific player.

    Note: This endpoint requires player ID which is not currently exposed
    in the main analysis. This is a placeholder for future enhancement.

    Args:
        player_id: NHL player ID

    Returns:
        Player details including Scrabble score

    Raises:
        HTTPException: Not implemented yet
    """
    # This would require additional NHL API integration to fetch individual player data
    raise HTTPException(
        status_code=501,
        detail="Player lookup by ID not implemented yet. Use /api/teams/{team_abbrev} to see team rosters.",
    )
