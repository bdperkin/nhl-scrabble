"""Standings endpoints.

Provides endpoints for division, conference, and playoff standings.

Example:
    Get division standings::

        $ curl http://localhost:8000/api/v1/standings/division

    Get conference standings::

        $ curl http://localhost:8000/api/v1/standings/conference

    Get playoff bracket::

        $ curl http://localhost:8000/api/v1/standings/playoffs
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Path

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

router = APIRouter()


@router.get("/standings/{standings_type}")
async def get_standings(
    standings_type: str = Path(
        ...,
        description="Type of standings (division, conference, or playoffs)",
    ),
) -> dict[str, Any]:
    """Get standings by type.

    Args:
        standings_type: Type of standings to retrieve (division, conference, or playoffs).

    Returns:
        dict: Standings data.

    Raises:
        HTTPException: If invalid type or fetch fails.

    Example:
        >>> response = await get_standings("division")
        >>> assert "divisions" in response
    """
    if standings_type not in {"division", "conference", "playoffs"}:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid standings type '{standings_type}'. "
                "Must be one of: division, conference, playoffs"
            ),
        )

    try:
        with NHLApiClient() as api_client:
            scorer = ScrabbleScorer()
            processor = TeamProcessor(api_client, scorer)

            team_scores, _, _ = processor.process_all_teams()

            if standings_type == "division":
                return _get_division_standings(processor, team_scores)
            if standings_type == "conference":
                return _get_conference_standings(processor, team_scores)
            # standings_type == "playoffs"
            return _get_playoff_standings(team_scores)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch {standings_type} standings: {e!s}",
        ) from e


def _get_division_standings(
    processor: TeamProcessor,
    team_scores: dict[str, Any],
) -> dict[str, Any]:
    """Get division standings.

    Args:
        processor: Team processor instance.
        team_scores: Team scores dictionary.

    Returns:
        dict: Division standings data.
    """
    division_standings = processor.calculate_division_standings(team_scores)

    division_data = []
    for division_name, standing in division_standings.items():
        # Get team details from team_scores dict using team abbreviations
        teams_in_division = [
            team_scores[abbrev] for abbrev in standing.teams if abbrev in team_scores
        ]
        # Sort by total score descending
        teams_in_division.sort(key=lambda t: t.total, reverse=True)

        division_data.append(
            {
                "division": division_name,
                "teams": [
                    {
                        "rank": i + 1,
                        "abbrev": team.abbrev,
                        "name": team.abbrev,
                        "total_score": team.total,
                        "average_score": team.avg_per_player,
                    }
                    for i, team in enumerate(teams_in_division)
                ],
            },
        )

    return {
        "type": "division",
        "divisions": division_data,
    }


def _get_conference_standings(
    processor: TeamProcessor,
    team_scores: dict[str, Any],
) -> dict[str, Any]:
    """Get conference standings.

    Args:
        processor: Team processor instance.
        team_scores: Team scores dictionary.

    Returns:
        dict: Conference standings data.
    """
    conference_standings = processor.calculate_conference_standings(team_scores)

    conference_data = []
    for conference_name, standing in conference_standings.items():
        # Get team details from team_scores dict using team abbreviations
        teams_in_conference = [
            team_scores[abbrev] for abbrev in standing.teams if abbrev in team_scores
        ]
        # Sort by total score descending
        teams_in_conference.sort(key=lambda t: t.total, reverse=True)

        conference_data.append(
            {
                "conference": conference_name,
                "teams": [
                    {
                        "rank": i + 1,
                        "abbrev": team.abbrev,
                        "name": team.abbrev,
                        "division": team.division,
                        "total_score": team.total,
                        "average_score": team.avg_per_player,
                    }
                    for i, team in enumerate(teams_in_conference)
                ],
            },
        )

    return {
        "type": "conference",
        "conferences": conference_data,
    }


def _get_playoff_standings(team_scores: dict[str, Any]) -> dict[str, Any]:
    """Get playoff standings and bracket.

    Args:
        team_scores: Team scores dictionary.

    Returns:
        dict: Playoff bracket data.
    """
    calculator = PlayoffCalculator()
    playoff_standings = calculator.calculate_playoff_standings(team_scores)

    # Format eastern conference
    eastern_teams = playoff_standings.get("Eastern", [])
    eastern_data = [
        {
            "seed": i + 1,
            "abbrev": team.abbrev,
            "name": team.abbrev,
            "division": team.division,
            "total_score": team.total,
            "status": team.status_indicator,
        }
        for i, team in enumerate(eastern_teams[:8])
    ]

    # Format western conference
    western_teams = playoff_standings.get("Western", [])
    western_data = [
        {
            "seed": i + 1,
            "abbrev": team.abbrev,
            "name": team.abbrev,
            "division": team.division,
            "total_score": team.total,
            "status": team.status_indicator,
        }
        for i, team in enumerate(western_teams[:8])
    ]

    return {
        "type": "playoffs",
        "eastern_conference": eastern_data,
        "western_conference": western_data,
    }
