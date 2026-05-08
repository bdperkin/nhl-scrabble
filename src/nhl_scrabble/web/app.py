"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer, allowing users to access analysis
results via browser instead of CLI.
"""

from __future__ import annotations

import gettext
import json
import logging
import operator
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from nhl_scrabble import __version__
from nhl_scrabble.api import NHLApiClient, NHLApiError
from nhl_scrabble.i18n import DEFAULT_LOCALE, LOCALES_DIR, SUPPORTED_LOCALES
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.processors import PlayoffCalculator, TeamProcessor
from nhl_scrabble.scoring import ScrabbleScorer

if TYPE_CHECKING:
    from starlette.responses import Response

logger = logging.getLogger(__name__)

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
                "img-src 'self' data: https://assets.nhle.com; "
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

# Cache storage (in-memory for now)
_analysis_cache: dict[str, dict[str, Any]] = {}


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


def setup_template_locale(request: Request) -> dict[str, Any]:
    """Set up template context with locale-specific translator.

    Args:
        request: FastAPI request object

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


# Test mode: Use mocked data from fixtures instead of live NHL API
TEST_MODE = os.getenv("NHL_SCRABBLE_TEST_MODE", "0") == "1"

# Log TEST_MODE status at module initialization
if TEST_MODE:
    logger.warning(
        "⚠️  TEST_MODE ENABLED - Server will use fixture data instead of live NHL API. "
        "Set NHL_SCRABBLE_TEST_MODE=0 to disable.",
    )
else:
    logger.info("TEST_MODE disabled - Server will use live NHL API")


def _load_fixture_data() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load NHL API fixture data from JSON files for test mode.

    Returns:
        Tuple of (standings_data, rosters_data)

    Raises:
        FileNotFoundError: If fixture files not found
        json.JSONDecodeError: If fixture files are invalid JSON
    """
    # Get current working directory for debugging
    cwd = Path.cwd()
    logger.info("Current working directory: %s", cwd)

    # Look for fixtures in common locations
    fixture_paths = [
        Path("qa/web/tests/visual/fixtures"),  # CI and local (from project root)
        Path(__file__).parent.parent.parent.parent
        / "qa/web/tests/visual/fixtures",  # Relative to this file
        cwd / "qa/web/tests/visual/fixtures",  # Explicit from CWD
    ]

    logger.info("Searching for fixture directory in %d locations:", len(fixture_paths))
    for i, path in enumerate(fixture_paths, 1):
        resolved = path.resolve()
        exists = path.exists()
        logger.info("  %d. %s (resolved: %s, exists: %s)", i, path, resolved, exists)

    fixture_dir = None
    for path in fixture_paths:
        if path.exists():
            fixture_dir = path
            logger.info("✅ Found fixture directory: %s", fixture_dir.resolve())
            break

    if fixture_dir is None:
        error_msg = (
            f"Fixture directory not found. CWD: {cwd}. "
            f"Tried: {[str(p.resolve()) for p in fixture_paths]}"
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    standings_file = fixture_dir / "nhl_standings.json"
    rosters_file = fixture_dir / "nhl_rosters.json"

    logger.info("Looking for fixture files:")
    logger.info("  - Standings: %s (exists: %s)", standings_file, standings_file.exists())
    logger.info("  - Rosters: %s (exists: %s)", rosters_file, rosters_file.exists())

    if not standings_file.exists():
        error_msg = f"Standings fixture not found: {standings_file.resolve()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    if not rosters_file.exists():
        error_msg = f"Rosters fixture not found: {rosters_file.resolve()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with standings_file.open() as f:
            standings_data = json.load(f)
        logger.info("✅ Loaded standings fixture: %d bytes", standings_file.stat().st_size)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in standings fixture {standings_file}: {e}"
        logger.error(error_msg)
        raise

    try:
        with rosters_file.open() as f:
            rosters_data = json.load(f)
        logger.info("✅ Loaded rosters fixture: %d bytes", rosters_file.stat().st_size)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in rosters fixture {rosters_file}: {e}"
        logger.error(error_msg)
        raise

    num_standings = len(standings_data.get("standings", []))
    num_rosters = len(rosters_data)
    logger.info(
        "✅ Fixture data loaded successfully: %d teams in standings, %d team rosters",
        num_standings,
        num_rosters,
    )

    return standings_data, rosters_data


def _process_fixture_data(
    scorer: ScrabbleScorer,
) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
    """Process fixture data the same way as TeamProcessor would process live API data.

    Args:
        scorer: ScrabbleScorer instance

    Returns:
        Tuple of (team_scores_dict, all_players, failed_teams)
    """
    standings_data, rosters_data = _load_fixture_data()

    team_scores: dict[str, TeamScore] = {}
    all_players: list[PlayerScore] = []
    failed_teams: list[str] = []

    # Extract team metadata from standings
    teams_info: dict[str, dict[str, str]] = {}
    for team in standings_data.get("standings", []):
        team_abbrev = team["teamAbbrev"]["default"]
        teams_info[team_abbrev] = {
            "name": team.get("teamName", {}).get("default", team_abbrev),
            "division": team.get("divisionName", "Unknown"),
            "conference": team.get("conferenceName", "Unknown"),
        }

    # Process each team's roster
    for team_abbrev, team_info in teams_info.items():
        if team_abbrev not in rosters_data:
            logger.warning("No roster data for team: %s", team_abbrev)
            failed_teams.append(team_abbrev)
            continue

        roster = rosters_data[team_abbrev]
        team_players: list[PlayerScore] = []

        # Process all positions
        for position_group in ("forwards", "defensemen", "goalies"):
            for player_data in roster.get(position_group, []):
                first_name = player_data.get("firstName", {}).get("default", "")
                last_name = player_data.get("lastName", {}).get("default", "")

                if not first_name or not last_name:
                    continue

                # Calculate scores
                first_score = scorer.calculate_score(first_name)
                last_score = scorer.calculate_score(last_name)
                full_name = f"{first_name} {last_name}"
                full_score = first_score + last_score

                player = PlayerScore(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    first_score=first_score,
                    last_score=last_score,
                    full_score=full_score,
                    team=team_abbrev,
                    division=team_info["division"],
                    conference=team_info["conference"],
                )
                team_players.append(player)
                all_players.append(player)

        # Create TeamScore
        if team_players:
            total_score = sum(p.full_score for p in team_players)
            team_score = TeamScore(
                abbrev=team_abbrev,
                name=team_info["name"],
                total=total_score,
                players=team_players,
                division=team_info["division"],
                conference=team_info["conference"],
            )
            team_scores[team_abbrev] = team_score

    logger.info("Processed %d teams with %d total players", len(team_scores), len(all_players))

    return team_scores, all_players, failed_teams


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""

    top_players: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of top players to include",
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

    context = setup_template_locale(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


def _convert_players_to_dict(
    players: list[PlayerScore],
) -> list[dict[str, str | int | float]]:
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
            "name": team_score.name,
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
    teams_data.sort(key=operator.itemgetter("total_score"), reverse=True)
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
        scorer = ScrabbleScorer()

        # Use fixture data in test mode, otherwise use live API
        if TEST_MODE:
            logger.info("🧪 TEST_MODE enabled - using fixture data instead of live NHL API")
            try:
                team_scores_dict, all_players_objects, failed_teams = _process_fixture_data(scorer)
                logger.info(
                    "✅ Fixture processing complete: %d teams, %d players",
                    len(team_scores_dict),
                    len(all_players_objects),
                )
            except FileNotFoundError as e:
                logger.error("❌ Fixture loading failed: %s", e)
                raise HTTPException(
                    status_code=500,
                    detail=f"TEST_MODE enabled but fixture data not found: {e}",
                ) from e
            except json.JSONDecodeError as e:
                logger.error("❌ Fixture parsing failed: %s", e)
                raise HTTPException(
                    status_code=500,
                    detail=f"TEST_MODE enabled but fixture data is invalid JSON: {e}",
                ) from e
            except Exception as e:
                logger.exception("❌ Unexpected error processing fixture data")
                raise HTTPException(
                    status_code=500,
                    detail=f"TEST_MODE enabled but fixture processing failed: {e}",
                ) from e
        else:
            with NHLApiClient() as client:
                # Process all teams using TeamProcessor
                team_processor = TeamProcessor(client, scorer)
                team_scores_dict, all_players_objects, failed_teams = (
                    team_processor.process_all_teams()
                )

        # Log failed teams
        if failed_teams:
            logger.warning("Failed to fetch %d teams: %s", len(failed_teams), failed_teams)

        # Convert player objects to dicts and sort by score
        all_players = _convert_players_to_dict(all_players_objects)
        all_players.sort(key=operator.itemgetter("score"), reverse=True)

        # Calculate playoff standings
        playoff_calc = PlayoffCalculator()
        playoff_standings = playoff_calc.calculate_playoff_standings(team_scores_dict)

        # Convert team scores to dict format for response
        teams_data = _convert_teams_to_dict(team_scores_dict, request.top_team_players)

        # Group by division and conference
        divisions, conferences = _group_teams_by_grouping(teams_data)

        # Calculate stats
        total_score: int | float = sum(int(p["score"]) for p in all_players) if all_players else 0

        # Get highest player's team name
        highest_player_team_name = None
        if all_players:
            highest_player_abbrev = all_players[0]["team"]
            for team in teams_data:
                if team["abbrev"] == highest_player_abbrev:
                    highest_player_team_name = team["name"]
                    break

        stats = {
            "total_players": len(all_players),
            "total_teams": len(teams_data),
            "highest_score": all_players[0]["score"] if all_players else 0,
            "highest_player_name": all_players[0]["full_name"] if all_players else None,
            "highest_player_team": highest_player_team_name,
            "lowest_score": all_players[-1]["score"] if all_players else 0,
            "avg_score": total_score / len(all_players) if all_players else 0,
            "highest_team": teams_data[0]["abbrev"] if teams_data else None,
            "highest_team_score": teams_data[0]["total_score"] if teams_data else 0,
            "highest_team_name": teams_data[0]["name"] if teams_data else None,
            "lowest_team": teams_data[-1]["abbrev"] if teams_data else None,
            "lowest_team_name": teams_data[-1]["name"] if teams_data else None,
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
        # Use fixed timestamp in TEST_MODE for deterministic visual tests
        timestamp = "2026-01-15T12:00:00+00:00" if TEST_MODE else datetime.now(UTC).isoformat()

        result = {
            "timestamp": timestamp,
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


@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered teams.html template with standings data

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "team_standings": data["team_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="teams.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch teams data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/teams/{team_abbrev}", response_class=HTMLResponse)
async def team_detail_page(
    request: Request,
    team_abbrev: str,
) -> HTMLResponse:
    """Serve a team detail page with player rankings and team logo.

    Args:
        request: FastAPI request object
        team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL', 'BOS')

    Returns:
        Rendered team_detail.html template with team data

    Raises:
        HTTPException: If team not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=100, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize team abbreviation for comparison
        team_abbrev_normalized = team_abbrev.strip().upper()

        # Find the team in team_standings
        team_data = None
        for team in data["team_standings"]:
            if team["abbrev"].upper() == team_abbrev_normalized:
                team_data = team
                break

        if team_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Team '{team_abbrev}' not found",
            )

        # Get all players for this team and sort by score (descending)
        team_players = sorted(
            team_data["players"],
            key=operator.itemgetter("score"),
            reverse=True,
        )

        # Add rank to each player
        for idx, player in enumerate(team_players, start=1):
            player["rank"] = idx

        # Calculate team-specific stats
        team_stats = {
            "team_abbrev": team_data["abbrev"],
            "team_name": team_data["name"],
            "team_division": team_data["division"],
            "team_conference": team_data["conference"],
            "total_score": team_data["total_score"],
            "avg_score": team_data["avg_score"],
            "total_players": team_data["player_count"],
            "highest_player_score": team_players[0]["score"] if team_players else 0,
            "highest_player_name": (
                f"{team_players[0]['first_name']} {team_players[0]['last_name']}"
                if team_players
                else "N/A"
            ),
            "logo_url_light": f"https://assets.nhle.com/logos/nhl/svg/{team_data['abbrev']}_light.svg",
            "logo_url_dark": f"https://assets.nhle.com/logos/nhl/svg/{team_data['abbrev']}_dark.svg",
        }

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "team_stats": team_stats,
                "team_players": team_players,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="team_detail.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch team detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/divisions", response_class=HTMLResponse)
async def divisions_page(request: Request) -> HTMLResponse:
    """Serve the divisions standings page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered divisions.html template with standings data

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "division_standings": data["division_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="divisions.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch divisions data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/divisions/{division_name}", response_class=HTMLResponse)
async def division_detail_page(request: Request, division_name: str) -> HTMLResponse:
    """Serve the division detail page with team standings and top players.

    Args:
        request: FastAPI request object
        division_name: Name of the division (e.g., "Atlantic", "Metropolitan")

    Returns:
        Rendered division_detail.html template with division data

    Raises:
        HTTPException: If templates not configured, analysis fails, or division not found
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize division name for comparison
        division_normalized = division_name.strip().title()

        # Validate division exists
        valid_divisions = {"Atlantic", "Metropolitan", "Central", "Pacific"}
        if division_normalized not in valid_divisions:
            raise HTTPException(
                status_code=404,
                detail=f"Division '{division_name}' not found. Valid divisions: {', '.join(sorted(valid_divisions))}",
            )

        # Filter teams by division
        division_teams = [
            team for team in data["team_standings"] if team["division"] == division_normalized
        ]

        if not division_teams:
            raise HTTPException(
                status_code=404,
                detail=f"No teams found for division '{division_normalized}'",
            )

        # Get parent conference from first team
        parent_conference = division_teams[0]["conference"]

        # Filter players by division (via team lookup)
        division_team_abbrevs = {team["abbrev"] for team in division_teams}
        division_players = [
            player for player in data["top_players"] if player["team"] in division_team_abbrevs
        ][:20]

        # Calculate division statistics
        total_teams = len(division_teams)
        total_players = sum(team["player_count"] for team in division_teams)

        # Find highest scoring team
        highest_team = max(division_teams, key=operator.itemgetter("total_score"))
        highest_team_score = highest_team["total_score"]
        highest_team_abbrev = highest_team["abbrev"]
        highest_team_name = highest_team["name"]

        # Find highest scoring player
        if division_players:
            highest_player = division_players[0]
            highest_player_score = highest_player["score"]
            highest_player_name = f"{highest_player['first_name']} {highest_player['last_name']}"
        else:
            highest_player_score = 0
            highest_player_name = "N/A"

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "division_name": division_normalized,
                "parent_conference": parent_conference,
                "division_teams": division_teams,
                "division_players": division_players,
                "division_stats": {
                    "total_teams": total_teams,
                    "total_players": total_players,
                    "highest_team_score": highest_team_score,
                    "highest_team": highest_team_abbrev,
                    "highest_team_name": highest_team_name,
                    "highest_player_score": highest_player_score,
                    "highest_player_name": highest_player_name,
                },
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="division_detail.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch division detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/conferences", response_class=HTMLResponse)
async def conferences_page(request: Request) -> HTMLResponse:
    """Serve the conferences standings page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered conferences.html template with standings data

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "conference_standings": data["conference_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="conferences.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch conferences data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/conferences/{conference_name}", response_class=HTMLResponse)
async def conference_detail_page(
    request: Request,
    conference_name: str,
) -> HTMLResponse:
    """Serve a conference detail page with teams and top players.

    Args:
        request: FastAPI request object
        conference_name: Conference name (Eastern, Western)

    Returns:
        Rendered conference_detail.html template with filtered data

    Raises:
        HTTPException: If conference not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        # Increase top_players to ensure we get 20+ per conference
        analysis_request = AnalysisRequest(top_players=100, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize conference name for comparison
        conference_normalized = conference_name.strip().title()

        # Validate conference exists
        if conference_normalized not in data["conference_standings"]:
            raise HTTPException(
                status_code=404,
                detail=f"Conference '{conference_name}' not found",
            )

        # Filter teams for this conference
        conference_teams = [
            team for team in data["team_standings"] if team["conference"] == conference_normalized
        ]

        # Filter top players for this conference (lookup via team for accuracy)
        conference_team_abbrevs = {team["abbrev"] for team in conference_teams}
        conference_players = [
            player for player in data["top_players"] if player["team"] in conference_team_abbrevs
        ][
            :20
        ]  # Top 20 players from this conference

        # Calculate conference-specific stats
        conference_stats = {
            "total_teams": len(conference_teams),
            "total_players": sum(t["player_count"] for t in conference_teams),
            "highest_team_score": conference_teams[0]["total_score"] if conference_teams else 0,
            "highest_team": conference_teams[0]["abbrev"] if conference_teams else None,
            "highest_team_name": conference_teams[0]["name"] if conference_teams else None,
            "highest_player_score": conference_players[0]["score"] if conference_players else 0,
            "highest_player_name": (
                conference_players[0]["full_name"] if conference_players else None
            ),
        }

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "conference_name": conference_normalized,
                "conference_teams": conference_teams,
                "conference_players": conference_players,
                "conference_stats": conference_stats,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="conference_detail.html",
            context=context,
        )

    except NHLApiError as e:
        logger.error("Failed to fetch conference detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/league", response_class=HTMLResponse)
async def league_page(request: Request) -> HTMLResponse:
    """Serve the league standings page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered league.html template with league-wide standings

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "team_standings": data["team_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="league.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch league data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/playoffs", response_class=HTMLResponse)
async def playoffs_page(request: Request) -> HTMLResponse:
    """Serve the playoff bracket page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered playoffs.html template with bracket data

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Calculate total playoff teams
        playoff_teams_count = sum(len(teams) for teams in data["playoff_bracket"].values())

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "playoff_bracket": data["playoff_bracket"],
                "playoff_teams_count": playoff_teams_count,
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="playoffs.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch playoffs data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request) -> HTMLResponse:
    """Serve the statistics page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered stats.html template with statistics and visualizations

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "stats": data["stats"],
                "top_players": data["top_players"],
                "team_standings": data["team_standings"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="stats.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch stats data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


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


@app.get("/robots.txt")
async def robots_txt() -> FileResponse:
    """Serve robots.txt file.

    Returns:
        robots.txt file for web crawlers
    """
    robots_file = STATIC_DIR / "robots.txt"
    return FileResponse(robots_file, media_type="text/plain")


@app.get("/api/analyze", response_model=None)
async def analyze_get(
    request: Request,
    top_players: Annotated[
        int,
        Query(ge=1, le=100, description="Number of top players to include"),
    ] = 20,
    top_team_players: Annotated[
        int,
        Query(ge=1, le=30, description="Top players per team"),
    ] = 5,
    use_cache: Annotated[
        bool,
        Query(description="Use cached results if available"),
    ] = True,
) -> HTMLResponse | dict[str, Any]:
    """Run NHL Scrabble analysis (GET endpoint for HTMX).

    Validates input parameters and returns 422 on invalid values.

    Args:
        request: FastAPI request object
        top_players: Number of top players to include (1-100)
        top_team_players: Top players per team (1-30)
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
        context = setup_template_locale(request)
        context.update(
            {
                "top_players": data["top_players"],
                "team_standings": data["team_standings"],
                "division_standings": data["division_standings"],
                "conference_standings": data["conference_standings"],
                "playoff_bracket": data["playoff_bracket"],
                "stats": data["stats"],
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context=context,
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
            },
        )

    return {
        "size": len(_analysis_cache),
        "entries": entries,
    }
