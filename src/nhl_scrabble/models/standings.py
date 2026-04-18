"""Standings data models."""

from dataclasses import dataclass
from typing import Literal


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

    def __repr__(self) -> str:
        """Return a string representation of the division standings."""
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

    def __repr__(self) -> str:
        """Return a string representation of the conference standings."""
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

    def __repr__(self) -> str:
        """Return a string representation of the playoff team."""
        return (
            f"PlayoffTeam(abbrev='{self.abbrev}', "
            f"seed='{self.seed_type}', status='{self.status_indicator}')"
        )
