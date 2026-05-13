"""Position-related routes.

This module contains routes for viewing positions and position details.
"""

from __future__ import annotations

import logging
import operator
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from nhl_scrabble.api import NHLApiError
from nhl_scrabble.i18n import format_date, format_time
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.processors import calculate_group_statistics, group_by_position
from nhl_scrabble.utils.positions import get_position_name, get_position_type
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/positions", response_class=HTMLResponse)
async def positions_page(request: Request) -> HTMLResponse:
    """Serve the positions page with player position statistics.

    Args:
        request: FastAPI request object
    Returns:
        Rendered positions.html template with position data

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

        # Convert top_players to PlayerScore objects
        all_players = [
            PlayerScore(
                player_id=p["player_id"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                full_name=p["full_name"],
                first_score=p["first_score"],
                last_score=p["last_score"],
                full_score=p["score"],
                team=p["team"],
                division=p.get("division", ""),
                conference=p.get("conference", ""),
                birthplace=p.get("birthplace", ""),
                birth_country=p.get("birth_country", ""),
                nationality=p.get("nationality", ""),
                position_code=p.get("position_code", ""),
                position=p.get("position", ""),
                position_type=p.get("position_type", ""),
            )
            for p in data["top_players"]
        ]

        # Group players by position
        position_groups = group_by_position(all_players)

        # Calculate stats for each position
        position_standings: list[dict[str, str | int | float]] = []
        for position, players in sorted(
            position_groups.items(),
            key=lambda x: sum(p.full_score for p in x[1]),
            reverse=True,
        ):
            if position:  # Skip unknown position
                stats = calculate_group_statistics(players)
                position_standings.append(
                    {
                        "position": position,
                        "position_code": players[0].position_code,
                        "position_type": players[0].position_type,
                        "player_count": stats["player_count"],
                        "total_score": stats["total_score"],
                        "avg_score": stats["average_score"],
                        "top_player_name": (
                            stats["top_player"]["full_name"] if stats["top_player"] else "—"
                        ),
                        "top_player_score": (
                            stats["top_player"]["full_score"] if stats["top_player"] else 0
                        ),
                    },
                )

        # Calculate overall stats
        total_positions = len(position_standings)
        total_players: int = sum(int(ps["player_count"]) for ps in position_standings)
        highest_position = position_standings[0]["position"] if position_standings else "—"
        highest_position_code = position_standings[0]["position_code"] if position_standings else ""
        highest_position_score = position_standings[0]["total_score"] if position_standings else 0

        # Find highest scoring player across all positions
        highest_player = max(all_players, key=lambda p: p.full_score)
        highest_player_name = highest_player.full_name
        highest_player_score = highest_player.full_score

        # Build entity data with positions for auto-linking
        entity_data = _build_entity_data(data)

        from nhl_scrabble.web.locale import setup_template_locale

        context = setup_template_locale(request, templates)
        context.update(
            {
                "position_standings": position_standings,
                "position_stats": {
                    "total_positions": total_positions,
                    "total_players": total_players,
                    "highest_position": highest_position,
                    "highest_position_code": highest_position_code,
                    "highest_position_score": highest_position_score,
                    "highest_player_name": highest_player_name,
                    "highest_player_score": highest_player_score,
                },
                "entity_data": entity_data,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="positions.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch positions data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@router.get("/positions/{position_type}", response_class=HTMLResponse)
async def position_type_page(
    request: Request,
    position_type: str) -> HTMLResponse:
    """Serve the position type page with all players from that position type.

    Args:
        request: FastAPI request object
        position_type: Position type (e.g., "Forward", "Defense", "Goalie")
    Returns:
        Rendered position_type.html template with position type data

    Raises:
        HTTPException: If templates not configured, analysis fails, or position type not found
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    # Validate position type
    valid_position_types = ["Forward", "Defense", "Goalie"]
    if position_type not in valid_position_types:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid position type '{position_type}'. Valid types: {', '.join(valid_position_types)}",
        )

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Convert top_players to PlayerScore objects and filter by position type
        position_type_players = [
            {
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "team": p["team"],
                "score": p["score"],
                "position": p.get("position", ""),
                "position_code": p.get("position_code", ""),
            }
            for p in data["top_players"]
            if p.get("position_type", "") == position_type
        ]

        if not position_type_players:
            raise HTTPException(
                status_code=404,
                detail=f"No players found for position type '{position_type}'",
            )

        # Sort by score descending
        position_type_players.sort(key=operator.itemgetter("score"), reverse=True)

        # Calculate stats
        total_players = len(position_type_players)
        total_score = sum(p["score"] for p in position_type_players)
        avg_score = total_score / total_players if total_players > 0 else 0
        highest_player = position_type_players[0]
        highest_player_name = f"{highest_player['first_name']} {highest_player['last_name']}"
        highest_player_score = highest_player["score"]

        # Calculate team distribution
        team_counts: dict[str, int] = {}
        for player in position_type_players:
            team = player["team"]
            team_counts[team] = team_counts.get(team, 0) + 1

        team_distribution = [
            {"team": team, "count": count}
            for team, count in sorted(team_counts.items(), key=operator.itemgetter(1), reverse=True)
        ]
        team_count = len(team_distribution)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale

        context = setup_template_locale(request, templates)
        context.update(
            {
                "position_type": position_type,
                "position_type_players": position_type_players,
                "position_stats": {
                    "total_players": total_players,
                    "total_score": total_score,
                    "avg_score": avg_score,
                    "highest_player_name": highest_player_name,
                    "highest_player_score": highest_player_score,
                },
                "team_distribution": team_distribution,
                "team_count": team_count,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="position_type.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch position type data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@router.get("/positions/detail/{position_code}", response_class=HTMLResponse)
async def position_detail_page(
    request: Request,
    position_code: str) -> HTMLResponse:
    """Serve the position detail page with all players at that specific position.

    Args:
        request: FastAPI request object
        position_code: Position code (e.g., "C", "L", "R", "D", "G")
    Returns:
        Rendered position_detail.html template with position data

    Raises:
        HTTPException: If templates not configured, analysis fails, or position code not found
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    # Validate and normalize position code
    valid_position_codes = ["C", "L", "R", "D", "G"]
    position_code_upper = position_code.upper()
    if position_code_upper not in valid_position_codes:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid position code '{position_code}'. Valid codes: {', '.join(valid_position_codes)}",
        )

    # Get position name and type
    position_name = get_position_name(position_code_upper)
    position_type = get_position_type(position_code_upper)

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Convert top_players to PlayerScore objects and filter by position code
        position_players = [
            {
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "team": p["team"],
                "score": p["score"],
                "nationality": p.get("nationality", ""),
            }
            for p in data["top_players"]
            if p.get("position_code", "").upper() == position_code_upper
        ]

        if not position_players:
            raise HTTPException(
                status_code=404,
                detail=f"No players found for position code '{position_code_upper}'",
            )

        # Sort by score descending
        position_players.sort(key=operator.itemgetter("score"), reverse=True)

        # Calculate stats
        total_players = len(position_players)
        total_score = sum(p["score"] for p in position_players)
        avg_score = total_score / total_players if total_players > 0 else 0
        highest_player = position_players[0]
        highest_player_name = f"{highest_player['first_name']} {highest_player['last_name']}"
        highest_player_score = highest_player["score"]

        # Calculate team distribution
        team_counts: dict[str, int] = {}
        for player in position_players:
            team = player["team"]
            team_counts[team] = team_counts.get(team, 0) + 1

        team_distribution = [
            {"team": team, "count": count}
            for team, count in sorted(team_counts.items(), key=operator.itemgetter(1), reverse=True)
        ]
        team_count = len(team_distribution)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = format_date(timestamp_dt.date(), format="long")
        timestamp_time = format_time(timestamp_dt, format="short") + " UTC"

        from nhl_scrabble.web.locale import setup_template_locale

        context = setup_template_locale(request, templates)
        context.update(
            {
                "position": position_name,
                "position_code": position_code_upper,
                "position_type": position_type,
                "position_players": position_players,
                "position_stats": {
                    "total_players": total_players,
                    "total_score": total_score,
                    "avg_score": avg_score,
                    "highest_player_name": highest_player_name,
                    "highest_player_score": highest_player_score,
                },
                "team_distribution": team_distribution,
                "team_count": team_count,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="position_detail.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch position detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
