"""API routes for HTMX requests.

This module contains API routes for dynamic content loading via HTMX.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastapi import APIRouter, Query, Request

from nhl_scrabble.web.converters import _build_entity_data
from nhl_scrabble.web.routes.core import AnalysisRequest, analyze_post

if TYPE_CHECKING:
    from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/api/analyze", response_model=None)
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
    templates = request.app.state.templates
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
        from nhl_scrabble.web.locale import setup_template_locale  # noqa: PLC0415

        context = setup_template_locale(request, templates)
        context.update(
            {
                "top_players": data["top_players"],
                "team_standings": data["team_standings"],
                "division_standings": data["division_standings"],
                "conference_standings": data["conference_standings"],
                "playoff_bracket": data["playoff_bracket"],
                "stats": data["stats"],
                "entity_data": _build_entity_data(data),
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context=context,
        )

    # Return JSON for regular API calls
    return data
