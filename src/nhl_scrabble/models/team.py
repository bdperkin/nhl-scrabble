"""Team data models."""

from dataclasses import dataclass, field

from nhl_scrabble.models.player import PlayerScore


@dataclass
class TeamScore:
    """Represents a team with aggregated Scrabble score information.

    Attributes:
        abbrev: Team abbreviation (e.g., 'TOR', 'MTL')
        total: Total Scrabble score for all players on the team
        players: List of all players on the team with their scores
        division: Division name
        conference: Conference name
        avg_per_player: Average score per player (computed)
    """

    abbrev: str
    total: int
    players: list[PlayerScore]
    division: str
    conference: str
    avg_per_player: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate average score per player after initialization."""
        self.avg_per_player = self.total / len(self.players) if self.players else 0.0

    @property
    def player_count(self) -> int:
        """Return the number of players on the team."""
        return len(self.players)

    def __repr__(self) -> str:
        """Return a string representation of the team."""
        return f"TeamScore(abbrev='{self.abbrev}', total={self.total}, players={self.player_count})"
