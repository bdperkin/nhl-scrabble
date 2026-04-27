"""Team data models."""

from dataclasses import dataclass, field
from typing import Any

from nhl_scrabble.models.player import PlayerScore


@dataclass(slots=True)
class TeamScore:
    """Represents a team with aggregated Scrabble score information.

    Attributes:
        abbrev: Team abbreviation (e.g., 'TOR', 'MTL')
        name: Team full name (e.g., 'Maple Leafs', 'Canadiens')
        total: Total Scrabble score for all players on the team
        players: List of all players on the team with their scores
        division: Division name
        conference: Conference name
        avg_per_player: Average score per player (computed)
    """

    abbrev: str
    name: str
    total: int
    players: list[PlayerScore]
    division: str
    conference: str
    avg_per_player: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate average score per player after initialization."""
        self.avg_per_player = self.total / len(self.players) if self.players else 0.0

    def to_dict(self, include_players: bool = True) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Args:
            include_players: Whether to include full player list (default: True)

        Returns:
            Dictionary representation of team
        """
        result = {
            "abbrev": self.abbrev,
            "name": self.name,
            "total": self.total,
            "division": self.division,
            "conference": self.conference,
            "avg_per_player": self.avg_per_player,
            "player_count": len(self.players),
        }

        if include_players:
            result["players"] = [p.to_dict() for p in self.players]

        return result

    @property
    def player_count(self) -> int:
        """Return the number of players on the team."""
        return len(self.players)

    def __repr__(self) -> str:
        """Return a string representation of the team."""
        return f"TeamScore(abbrev='{self.abbrev}', total={self.total}, players={self.player_count})"
