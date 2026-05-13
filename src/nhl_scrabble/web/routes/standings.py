"""League standings and playoff routes.

This module contains routes for league-wide standings, playoffs, and statistics.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/league", response_class=HTMLResponse)
async def league_page(request: Request) -> HTMLResponse:
    """Serve the league standings page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered league.html template with league-wide standings

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
                "team_standings": data["team_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
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


@router.get("/playoffs", response_class=HTMLResponse)
async def playoffs_page(request: Request) -> HTMLResponse:
    """Serve the playoff bracket page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered playoffs.html template with bracket data

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

        # Calculate total playoff teams (only teams that made playoffs, not eliminated)
        playoff_teams_count = sum(
            sum(1 for team in teams if team.get("in_playoffs", False))
            for teams in data["playoff_bracket"].values()
        )

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "playoff_bracket": data["playoff_bracket"],
                "playoff_teams_count": playoff_teams_count,
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
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


@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request) -> HTMLResponse:
    """Serve the statistics page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered stats.html template with statistics and visualizations

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
                "stats": data["stats"],
                "top_players": data["top_players"],
                "team_standings": data["team_standings"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
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
