"""Team score endpoints.

Provides endpoints for fetching team Scrabble scores with optional filtering.

Example:
    Get all teams::

        $ curl http://localhost:8000/api/v1/teams

    Get teams from a specific division::

        $ curl http://localhost:8000/api/v1/teams?division=Atlantic

    Get a specific team::

        $ curl http://localhost:8000/api/v1/teams/TOR
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

router = APIRouter()


@router.get("/teams")
async def get_teams(
    division: str | None = Query(
        None,
        description="Filter teams by division (e.g., Atlantic, Metropolitan, Central, Pacific)",
    ),
    conference: str | None = Query(
        None,
        description="Filter teams by conference (Eastern or Western)",
    ),
) -> dict[str, Any]:
    """Get all team scores with optional filtering.

    Args:
        division: Optional division filter.
        conference: Optional conference filter.

    Returns:
        dict: Team scores data.

    Raises:
        HTTPException: If data fetch fails.

    Example:
        >>> # Get all teams
        >>> response = await get_teams()
        >>> # Filter by division
        >>> response = await get_teams(division="Atlantic")
    """
    try:
        api_client = NHLApiClient()
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer)

        team_scores, _, _ = processor.process_all_teams()

        # Apply filters
        filtered_teams = [
            team
            for team in team_scores.values()
            if (division is None or team.division == division)
            and (conference is None or team.conference == conference)
        ]

        teams_data = [
            {
                "abbrev": team.abbrev,
                "name": team.abbrev,  # We don't have full name in current model
                "division": team.division,
                "conference": team.conference,
                "total_score": team.total,
                "average_score": team.avg_per_player,
                "player_count": len(team.players),
                "top_players": [
                    {
                        "name": f"{p.first_name} {p.last_name}",
                        "score": p.full_score,
                    }
                    for p in sorted(team.players, key=lambda x: x.full_score, reverse=True)[:5]
                ],
            }
            for team in filtered_teams
        ]

        return {
            "teams": teams_data,
            "count": len(teams_data),
            "filters": {
                "division": division,
                "conference": conference,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch teams: {e!s}") from e


@router.get("/teams/{abbrev}")
async def get_team(abbrev: str) -> dict[str, Any]:
    """Get a specific team's score by abbreviation.

    Args:
        abbrev: Team abbreviation (e.g., TOR, MTL, NYR).

    Returns:
        dict: Team score data.

    Raises:
        HTTPException: If team not found or fetch fails.

    Example:
        >>> response = await get_team("TOR")
        >>> assert response["abbrev"] == "TOR"
    """
    try:
        api_client = NHLApiClient()
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer)

        team_scores, _, _ = processor.process_all_teams()

        # Find the team
        team = team_scores.get(abbrev.upper())

        if team is None:
            raise HTTPException(
                status_code=404,
                detail=f"Team '{abbrev}' not found",
            )

        return {
            "abbrev": team.abbrev,
            "name": team.abbrev,
            "division": team.division,
            "conference": team.conference,
            "total_score": team.total,
            "average_score": team.avg_per_player,
            "player_count": len(team.players),
            "players": [
                {
                    "name": f"{p.first_name} {p.last_name}",
                    "score": p.full_score,
                    "first_name_score": p.first_score,
                    "last_name_score": p.last_score,
                }
                for p in sorted(team.players, key=lambda x: x.full_score, reverse=True)
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch team '{abbrev}': {e!s}",
        ) from e
