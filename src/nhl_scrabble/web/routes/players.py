"""Player-related routes.

This module contains routes for viewing players and player details.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiClient, NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.security.log_filter import sanitize_for_logging
from nhl_scrabble.utils.countries import get_country_name
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/players", response_class=HTMLResponse)
async def players_page(request: Request) -> HTMLResponse:
    """Serve the players ranking page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered players.html template with player rankings

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        # Use higher top_players count for dedicated players page
        analysis_request = AnalysisRequest(top_players=50, top_team_players=5, use_cache=True)
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
                "top_players": data["top_players"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="players.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch players data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@router.get("/players/{player_id}", response_class=HTMLResponse)
async def player_detail_page(  # Route handler with player data processing
    request: Request,
    player_id: int,
) -> HTMLResponse:
    """Serve a player detail page with comprehensive information.

    Args:
        request: FastAPI request object
        player_id: NHL player ID (numeric)

    Returns:
        Rendered player_detail.html template with player data

    Raises:
        HTTPException: If player not found or analysis fails
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data to get all players with scores
        # Request high number to ensure we can find any player (including lowest scorer)
        # Typical NHL season has 700-800 active players
        analysis_request = AnalysisRequest(top_players=2000, use_cache=True)
        data = await analyze_post(analysis_request)

        # Find the player in top_players list by matching player_id
        player_data = None
        for player in data["top_players"]:
            if player.get("player_id") == player_id:
                player_data = player
                break

        if player_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Player {player_id} not found",
            )

        # Get team name from team_standings
        team_name = player_data["team"]  # Default to abbreviation
        for team in data.get("team_standings", []):
            if team["abbrev"] == player_data["team"]:
                team_name = team["name"]
                break

        # Fetch extended player details from NHL API
        with NHLApiClient() as nhl_client:
            try:
                nhl_data = nhl_client.get_player_details(player_id)
            except NHLApiError as e:
                logger.error(
                    "Failed to fetch player %s details: %s",
                    sanitize_for_logging(player_id),
                    sanitize_for_logging(e),
                )
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to fetch player details: {e!s}",
                ) from e

        # Extract birth location components with defaults
        birth_city = nhl_data.get("birthCity", {})
        birth_city_str = (
            birth_city.get("default", "")
            if isinstance(birth_city, dict)
            else str(birth_city) if birth_city else ""
        )

        birth_state_prov = nhl_data.get("birthStateProvince", {})
        birth_state_str = (
            birth_state_prov.get("default", "")
            if isinstance(birth_state_prov, dict)
            else str(birth_state_prov) if birth_state_prov else ""
        )

        birth_country = nhl_data.get("birthCountry", "")

        # Construct birthplace string
        birthplace_parts = [p for p in (birth_city_str, birth_state_str, birth_country) if p]
        birthplace = ", ".join(birthplace_parts) if birthplace_parts else "Unknown"

        # Extract headshot URL
        headshot = nhl_data.get("headshot", "")

        # Extract position
        position = nhl_data.get("position", "")

        # Extract jersey number
        sweater_number = nhl_data.get("sweaterNumber", 0)

        # Get nationality from birth country code
        nationality = get_country_name(birth_country) if birth_country else ""

        # Extract player information
        player_info = {
            "player_id": player_id,
            "full_name": player_data["full_name"],
            "first_name": player_data["first_name"],
            "last_name": player_data["last_name"],
            "photo_url": headshot,
            "birthplace": birthplace,
            "birth_country": birth_country.lower() if birth_country else "",
            "nationality": nationality,
            "team_abbrev": player_data["team"],
            "team_name": team_name,
            "division": player_data["division"],
            "conference": player_data["conference"],
            "position": position,
            "jersey_number": sweater_number,
            "scrabble_score": player_data["score"],
            "first_score": player_data["first_score"],
            "last_score": player_data["last_score"],
            "team_logo_url": f"https://assets.nhle.com/logos/nhl/svg/{player_data['team']}_light.svg",
            "country_flag_url": (
                f"https://flagcdn.com/w320/{birth_country.lower()}.png" if birth_country else ""
            ),
        }

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "player": player_info,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="player_detail.html",
            context=context,
        )

    except NHLApiError as e:
        logger.error("NHL API error during player detail page generation: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.get("/api/players/{player_id}")
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
