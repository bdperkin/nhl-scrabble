"""Team-related routes.

This module contains routes for viewing teams and team details.
"""

from __future__ import annotations

import logging
import operator
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiClient, NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.security.log_filter import sanitize_for_logging
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post, get_analysis_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page with data.

    Args:
        request: FastAPI request object
    Returns:
        Rendered teams.html template with standings data

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
        return templates.TemplateResponse(  # type: ignore[no-any-return]
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


@router.get("/teams/{team_abbrev}", response_class=HTMLResponse)
async def team_detail_page(  # noqa: C901  # Route handler with team roster processing
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
    templates = request.app.state.templates
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

        # Fetch full team roster and calculate Scrabble scores
        # The analyze endpoint only returns top N players per team, but we need ALL players
        scorer = ScrabbleScorer()
        with NHLApiClient() as client:
            try:
                roster_data = client.get_team_roster(team_abbrev_normalized)
            except NHLApiError as e:
                logger.error(
                    "Failed to fetch roster for team %s: %s",
                    sanitize_for_logging(team_abbrev_normalized),
                    sanitize_for_logging(e),
                )
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to fetch team roster: {e!s}",
                ) from e

        # Process roster and calculate scores
        # Roster data has keys: 'forwards', 'defensemen', 'goalies'
        team_players: list[dict[str, Any]] = []
        for position in ("forwards", "defensemen", "goalies"):
            if position not in roster_data:
                continue

            for roster_player in roster_data[position]:
                first_name = roster_player.get("firstName", {}).get("default", "")
                last_name = roster_player.get("lastName", {}).get("default", "")

                if not first_name or not last_name:
                    continue

                first_score = scorer.calculate_score(first_name)
                last_score = scorer.calculate_score(last_name)
                full_score = first_score + last_score

                team_players.append(
                    {
                        "first_name": first_name,
                        "last_name": last_name,
                        "score": full_score,
                        "first_score": first_score,
                        "last_score": last_score,
                    },
                )

        # Sort by score (descending) and add rank
        team_players.sort(key=operator.itemgetter("score"), reverse=True)
        for idx, player_dict in enumerate(team_players, start=1):
            player_dict["rank"] = idx

        # Calculate team-specific stats
        team_stats = {
            "team_abbrev": team_data["abbrev"],
            "team_name": team_data["name"],
            "team_division": team_data["division"],
            "team_conference": team_data["conference"],
            "total_score": team_data["total_score"],
            "avg_score": team_data["avg_score"],
            "total_players": len(team_players),
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
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "team_name": team_data["name"],
                "team_abbrev": team_data["abbrev"],
                "team_division": team_data["division"],
                "team_conference": team_data["conference"],
                "team_stats": team_stats,
                "team_players": team_players,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(  # type: ignore[no-any-return]
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


@router.get("/api/teams/{team_abbrev}")
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
    _analysis_cache = get_analysis_cache()
    for cached in _analysis_cache.values():
        for team in cached["data"]["team_standings"]:
            if team["abbrev"].upper() == team_abbrev.upper():
                return team  # type: ignore[no-any-return]

    raise HTTPException(status_code=404, detail=f"Team {team_abbrev} not found")
