"""Core routes for the web application.

This module contains the main routes: /, /health, and /api/analyze POST.
"""

from __future__ import annotations

import json
import logging
import operator
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from nhl_scrabble import __version__
from nhl_scrabble.api import NHLApiClient, NHLApiError
from nhl_scrabble.processors import PlayoffCalculator, TeamProcessor
from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.web.converters import (
    _convert_players_to_dict,
    _convert_teams_to_dict,
    _group_teams_by_grouping,
)
from nhl_scrabble.web.fixtures import _process_fixture_data

logger = logging.getLogger(__name__)

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

# Cache storage (in-memory for now)
_analysis_cache: dict[str, dict[str, Any]] = {}

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""

    top_players: int = Field(
        default=20,
        ge=1,
        le=2000,
        description="Number of top players to include (max 2000 to cover all NHL players)",
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


@router.get("/health")
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


@router.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Serve the main web interface.

    Args:
        request: FastAPI request object

    Returns:
        Rendered index.html template

    Raises:
        HTTPException: If templates not available
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

    context = setup_template_locale(request, templates)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@router.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_post(request: AnalysisRequest) -> dict[str, Any]:  # noqa: C901, PLR0912, PLR0915
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

        # Add team names to players for display (lookup from team_scores_dict)
        for player in all_players:
            team_abbrev = player["team"]
            if team_abbrev in team_scores_dict:
                player["team_name"] = team_scores_dict[team_abbrev].name
            else:
                player["team_name"] = team_abbrev  # Fallback to abbreviation

        # Calculate playoff standings
        playoff_calc = PlayoffCalculator()
        playoff_standings = playoff_calc.calculate_playoff_standings(team_scores_dict)

        # Convert team scores to dict format for response
        teams_data = _convert_teams_to_dict(team_scores_dict, request.top_team_players)

        # Group by division and conference
        divisions, conferences = _group_teams_by_grouping(teams_data)

        # Calculate stats
        total_score: int | float = sum(int(p["score"]) for p in all_players) if all_players else 0

        # Get highest and lowest player team names
        highest_player_team_name = None
        lowest_player_team_name = None
        if all_players:
            highest_player_abbrev = all_players[0]["team"]
            lowest_player_abbrev = all_players[-1]["team"]
            for team in teams_data:
                if team["abbrev"] == highest_player_abbrev:
                    highest_player_team_name = team["name"]
                if team["abbrev"] == lowest_player_abbrev:
                    lowest_player_team_name = team["name"]
                if highest_player_team_name and lowest_player_team_name:
                    break

        stats = {
            "total_players": len(all_players),
            "total_teams": len(teams_data),
            "highest_score": all_players[0]["score"] if all_players else 0,
            "highest_player_name": all_players[0]["full_name"] if all_players else None,
            "highest_player_id": all_players[0].get("player_id") if all_players else None,
            "highest_player_team": highest_player_team_name,
            "lowest_score": all_players[-1]["score"] if all_players else 0,
            "lowest_player_name": all_players[-1]["full_name"] if all_players else None,
            "lowest_player_id": all_players[-1].get("player_id") if all_players else None,
            "lowest_player_team": lowest_player_team_name,
            "avg_score": total_score / len(all_players) if all_players else 0,
            "highest_team": teams_data[0]["abbrev"] if teams_data else None,
            "highest_team_score": teams_data[0]["total_score"] if teams_data else 0,
            "highest_team_name": teams_data[0]["name"] if teams_data else None,
            "lowest_team": teams_data[-1]["abbrev"] if teams_data else None,
            "lowest_team_score": teams_data[-1]["total_score"] if teams_data else 0,
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


def get_analysis_cache() -> dict[str, dict[str, Any]]:
    """Get reference to the analysis cache.

    Returns:
        Analysis cache dictionary
    """
    return _analysis_cache
