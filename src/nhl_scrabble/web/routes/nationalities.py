"""Nationality-related routes.

This module contains routes for viewing nationalities and nationality details.
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
from nhl_scrabble.processors import calculate_group_statistics, group_by_nationality
from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/nationalities", response_class=HTMLResponse)
async def nationalities_page(request: Request) -> HTMLResponse:
    """Serve the nationalities page with player nationality statistics.

    Args:
        request: FastAPI request object
    Returns:
        Rendered nationalities.html template with nationality data

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
            )
            for p in data["top_players"]
        ]

        # Group players by nationality
        nationality_groups = group_by_nationality(all_players)

        # Calculate stats for each nationality
        nationality_standings: list[dict[str, str | int | float]] = []
        for nationality, players in sorted(
            nationality_groups.items(),
            key=lambda x: sum(p.full_score for p in x[1]),
            reverse=True,
        ):
            if nationality:  # Skip unknown nationality
                stats = calculate_group_statistics(players)
                nationality_standings.append(
                    {
                        "nationality": nationality,
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
        total_nationalities = len(nationality_standings)
        total_players: int = sum(int(ns["player_count"]) for ns in nationality_standings)
        highest_nationality = (
            nationality_standings[0]["nationality"] if nationality_standings else "—"
        )
        highest_nationality_score = (
            nationality_standings[0]["total_score"] if nationality_standings else 0
        )

        # Find highest scoring player across all nationalities
        highest_player = max(all_players, key=lambda p: p.full_score)
        highest_player_name = highest_player.full_name
        highest_player_score = highest_player.full_score

        # Build entity data with nationalities for auto-linking
        entity_data = _build_entity_data(data)
        entity_data["nationalities"] = [
            {"name": str(ns["nationality"])} for ns in nationality_standings
        ]

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "nationality_standings": nationality_standings,
                "nationality_stats": {
                    "total_nationalities": total_nationalities,
                    "total_players": total_players,
                    "highest_nationality": highest_nationality,
                    "highest_nationality_score": highest_nationality_score,
                    "highest_player_name": highest_player_name,
                    "highest_player_score": highest_player_score,
                },
                "entity_data": entity_data,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="nationalities.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch nationalities data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e


@router.get("/nationalities/{nationality_name}", response_class=HTMLResponse)
async def nationality_detail_page(
    request: Request,
    nationality_name: str,
) -> HTMLResponse:
    """Serve the nationality detail page with all players from that nationality.

    Args:
        request: FastAPI request object
        nationality_name: Name of the nationality (e.g., "Canada", "United States")

    Returns:
        Rendered nationality_detail.html template with nationality data

    Raises:
        HTTPException: If templates not configured, analysis fails, or nationality not found
    """
    templates = request.app.state.templates
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize nationality name
        nationality_normalized = nationality_name.strip()

        # Convert top_players to PlayerScore objects and filter by nationality
        nationality_players = [
            {
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "team": p["team"],
                "score": p["score"],
                "birthplace": p.get("birthplace", ""),
            }
            for p in data["top_players"]
            if p.get("nationality", "") == nationality_normalized
        ]

        if not nationality_players:
            raise HTTPException(
                status_code=404,
                detail=f"No players found for nationality '{nationality_normalized}'",
            )

        # Sort by score descending
        nationality_players.sort(key=operator.itemgetter("score"), reverse=True)

        # Calculate stats
        total_players = len(nationality_players)
        total_score = sum(p["score"] for p in nationality_players)
        avg_score = total_score / total_players if total_players > 0 else 0
        highest_player = nationality_players[0]
        highest_player_name = f"{highest_player['first_name']} {highest_player['last_name']}"
        highest_player_score = highest_player["score"]

        # Calculate team distribution
        team_counts: dict[str, int] = {}
        for player in nationality_players:
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

        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "nationality": nationality_normalized,
                "nationality_players": nationality_players,
                "nationality_stats": {
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
            name="nationality_detail.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch nationality detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
