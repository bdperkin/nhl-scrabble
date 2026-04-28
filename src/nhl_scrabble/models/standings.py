"""Standings data models."""

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(slots=True)
class DivisionStandings:
    """Represents division-level standings based on Scrabble scores.

    Attributes:
        name: Division name
        total: Total Scrabble score for all teams in the division
        teams: List of team abbreviations in this division
        player_count: Total number of players in the division
        avg_per_team: Average score per team
    """

    name: str
    total: int
    teams: list[str]
    player_count: int
    avg_per_team: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Examples:
            >>> standings = DivisionStandings(
            ...     name="Atlantic",
            ...     total=5000,
            ...     teams=["TOR", "MTL", "BOS"],
            ...     player_count=75,
            ...     avg_per_team=1666.67
            ... )
            >>> result = standings.to_dict()
            >>> result['name']
            'Atlantic'
            >>> len(result['teams'])
            3
        """
        return {
            "name": self.name,
            "total": self.total,
            "teams": self.teams,
            "player_count": self.player_count,
            "avg_per_team": self.avg_per_team,
        }

    def __repr__(self) -> str:
        """Return a string representation of the division standings.

        Examples:
            >>> standings = DivisionStandings(
            ...     name="Atlantic",
            ...     total=5000,
            ...     teams=["TOR", "MTL", "BOS"],
            ...     player_count=75,
            ...     avg_per_team=1666.67
            ... )
            >>> repr(standings)
            "DivisionStandings(name='Atlantic', total=5000, teams=3)"
        """
        return f"DivisionStandings(name='{self.name}', total={self.total}, teams={len(self.teams)})"


@dataclass(slots=True)
class ConferenceStandings:
    """Represents conference-level standings based on Scrabble scores.

    Attributes:
        name: Conference name
        total: Total Scrabble score for all teams in the conference
        teams: List of team abbreviations in this conference
        player_count: Total number of players in the conference
        avg_per_team: Average score per team
    """

    name: str
    total: int
    teams: list[str]
    player_count: int
    avg_per_team: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Examples:
            >>> standings = ConferenceStandings(
            ...     name="Eastern",
            ...     total=10000,
            ...     teams=["TOR", "MTL", "BOS", "NYR"],
            ...     player_count=100,
            ...     avg_per_team=2500.0
            ... )
            >>> result = standings.to_dict()
            >>> result['name']
            'Eastern'
            >>> len(result['teams'])
            4
        """
        return {
            "name": self.name,
            "total": self.total,
            "teams": self.teams,
            "player_count": self.player_count,
            "avg_per_team": self.avg_per_team,
        }

    def __repr__(self) -> str:
        """Return a string representation of the conference standings.

        Examples:
            >>> standings = ConferenceStandings(
            ...     name="Eastern",
            ...     total=10000,
            ...     teams=["TOR", "MTL", "BOS", "NYR"],
            ...     player_count=100,
            ...     avg_per_team=2500.0
            ... )
            >>> repr(standings)
            "ConferenceStandings(name='Eastern', total=10000, teams=4)"
        """
        return (
            f"ConferenceStandings(name='{self.name}', total={self.total}, teams={len(self.teams)})"
        )


StatusIndicator = Literal["p", "z", "y", "x", "e", ""]


@dataclass(slots=True)
class PlayoffTeam:
    """Represents a team in playoff standings context.

    Attributes:
        abbrev: Team abbreviation
        total: Total Scrabble score
        players: Number of players on the team
        avg: Average score per player
        conference: Conference name
        division: Division name
        seed_type: Playoff seed description (e.g., "Atlantic #1", "Eastern WC1")
        in_playoffs: Whether team has clinched a playoff spot
        division_rank: Rank within the division (1-based)
        status_indicator: Playoff status (p=Presidents', z=Conference, y=Division, x=Playoff, e=Eliminated)
    """

    abbrev: str
    total: int
    players: int
    avg: float
    conference: str
    division: str
    seed_type: str = ""
    in_playoffs: bool = False
    division_rank: int = 0
    status_indicator: StatusIndicator = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Examples:
            >>> team = PlayoffTeam(
            ...     abbrev="TOR",
            ...     total=500,
            ...     players=25,
            ...     avg=20.0,
            ...     conference="Eastern",
            ...     division="Atlantic",
            ...     seed_type="Atlantic #1",
            ...     in_playoffs=True,
            ...     division_rank=1,
            ...     status_indicator="y"
            ... )
            >>> result = team.to_dict()
            >>> result['abbrev']
            'TOR'
            >>> result['in_playoffs']
            True
        """
        return {
            "abbrev": self.abbrev,
            "total": self.total,
            "players": self.players,
            "avg": self.avg,
            "conference": self.conference,
            "division": self.division,
            "seed_type": self.seed_type,
            "in_playoffs": self.in_playoffs,
            "division_rank": self.division_rank,
            "status_indicator": self.status_indicator,
        }

    def __repr__(self) -> str:
        """Return a string representation of the playoff team.

        Examples:
            >>> team = PlayoffTeam(
            ...     abbrev="TOR",
            ...     total=500,
            ...     players=25,
            ...     avg=20.0,
            ...     conference="Eastern",
            ...     division="Atlantic",
            ...     seed_type="Atlantic #1",
            ...     in_playoffs=True,
            ...     division_rank=1,
            ...     status_indicator="y"
            ... )
            >>> repr(team)
            "PlayoffTeam(abbrev='TOR', seed='Atlantic #1', status='y')"
        """
        return (
            f"PlayoffTeam(abbrev='{self.abbrev}', "
            f"seed='{self.seed_type}', status='{self.status_indicator}')"
        )
