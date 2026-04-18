"""Player score endpoints.

Provides endpoints for fetching player Scrabble scores with optional filtering.

Example:
    Get all players::

        $ curl http://localhost:8000/api/v1/players

    Get players with minimum score::

        $ curl http://localhost:8000/api/v1/players?min_score=100

    Get top N players::

        $ curl http://localhost:8000/api/v1/players?limit=10
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

router = APIRouter()


@router.get("/players")
async def get_players(
    min_score: int | None = Query(None, description="Minimum Scrabble score filter", ge=0),
    max_score: int | None = Query(None, description="Maximum Scrabble score filter", ge=0),
    team: str | None = Query(None, description="Filter by team abbreviation"),
    limit: int | None = Query(None, description="Limit number of results", ge=1, le=1000),
    sort_by: str = Query("score", description="Sort field (score or name)"),
    order: str = Query("desc", description="Sort order (asc or desc)"),
) -> dict[str, Any]:
    """Get all player scores with optional filtering.

    Args:
        min_score: Minimum score filter (inclusive).
        max_score: Maximum score filter (inclusive).
        team: Team abbreviation filter.
        limit: Maximum number of players to return.
        sort_by: Field to sort by (score or name).
        order: Sort order (asc or desc).

    Returns:
        dict: Player scores data.

    Raises:
        HTTPException: If data fetch fails.

    Example:
        >>> # Get all players
        >>> response = await get_players()
        >>> # Filter by minimum score
        >>> response = await get_players(min_score=100, limit=10)
    """
    try:
        api_client = NHLApiClient()
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer)

        team_scores, all_players, _ = processor.process_all_teams()

        # Apply team filter
        if team:
            team_upper = team.upper()
            if team_upper not in team_scores:
                raise HTTPException(status_code=404, detail=f"Team '{team}' not found")
            all_players = team_scores[team_upper].players

        # Build player data
        players_data = [
            {
                "name": f"{p.first_name} {p.last_name}",
                "first_name": p.first_name,
                "last_name": p.last_name,
                "score": p.full_score,
                "first_name_score": p.first_score,
                "last_name_score": p.last_score,
                "team": getattr(p, "team", team.upper() if team else ""),
            }
            for p in all_players
        ]

        # Apply score filters
        if min_score is not None:
            players_data = [p for p in players_data if p["score"] >= min_score]  # type: ignore[operator]
        if max_score is not None:
            players_data = [p for p in players_data if p["score"] <= max_score]  # type: ignore[operator]

        # Sort
        reverse = order.lower() == "desc"
        if sort_by == "score":
            players_data.sort(key=lambda p: p["score"], reverse=reverse)
        elif sort_by == "name":
            players_data.sort(
                key=lambda p: (p["last_name"], p["first_name"]),
                reverse=reverse,
            )

        # Apply limit
        if limit is not None:
            players_data = players_data[:limit]

        return {
            "players": players_data,
            "count": len(players_data),
            "filters": {
                "min_score": min_score,
                "max_score": max_score,
                "team": team,
                "limit": limit,
                "sort_by": sort_by,
                "order": order,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch players: {e!s}") from e
