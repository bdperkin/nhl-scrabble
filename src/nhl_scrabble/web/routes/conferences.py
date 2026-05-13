"""Conference-related routes.

This module contains routes for viewing conferences and conference details.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/conferences", response_class=HTMLResponse)
async def conferences_page(request: Request) -> HTMLResponse:
    """Serve the conferences standings page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered conferences.html template with standings data

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

        from nhl_scrabble.web.locale import setup_template_locale

        context = setup_template_locale(request, templates)
        context.update(
            {
                "conference_standings": data["conference_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
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


@router.get("/conferences/{conference_name}", response_class=HTMLResponse)
async def conference_detail_page(
    request: Request,
    conference_name: str) -> HTMLResponse:
    """Serve a conference detail page with teams and top players.

    Args:
        request: FastAPI request object
        conference_name: Conference name (Eastern, Western)
    Returns:
        Rendered conference_detail.html template with filtered data

    Raises:
        HTTPException: If conference not found or analysis fails
    """
    templates = request.app.state.templates
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
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale

        context = setup_template_locale(request, templates)
        context.update(
            {
                "conference_name": conference_normalized,
                "conference_teams": conference_teams,
                "conference_players": conference_players,
                "conference_stats": conference_stats,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
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
