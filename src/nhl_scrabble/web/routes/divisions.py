"""Division-related routes.

This module contains routes for viewing divisions and division details.
"""

from __future__ import annotations

import logging
import operator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/divisions", response_class=HTMLResponse)
async def divisions_page(request: Request) -> HTMLResponse:
    """Serve the divisions standings page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered divisions.html template with standings data

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "division_standings": data["division_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(  # type: ignore[no-any-return]
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


@router.get("/divisions/{division_name}", response_class=HTMLResponse)
async def division_detail_page(
    request: Request,
    division_name: str,
) -> HTMLResponse:
    """Serve the division detail page with team standings and top players.

    Args:
        request: FastAPI request object
        division_name: Name of the division (e.g., "Atlantic", "Metropolitan")

    Returns:
        Rendered division_detail.html template with division data

    Raises:
        HTTPException: If templates not configured, analysis fails, or division not found
    """
    templates = request.app.state.templates
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
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
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
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(  # type: ignore[no-any-return]
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
