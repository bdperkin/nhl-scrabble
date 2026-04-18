"""Player data models."""

from dataclasses import dataclass


@dataclass(slots=True)
class PlayerScore:
    """Represents a player with their Scrabble score information.

    Attributes:
        first_name: Player's first name
        last_name: Player's last name
        full_name: Player's full name (first + last)
        first_score: Scrabble score for first name
        last_score: Scrabble score for last name
        full_score: Total Scrabble score (first + last)
        team: Team abbreviation (e.g., 'TOR', 'MTL')
        division: Division name
        conference: Conference name
    """

    first_name: str
    last_name: str
    full_name: str
    first_score: int
    last_score: int
    full_score: int
    team: str
    division: str
    conference: str

    def __repr__(self) -> str:
        """Return a string representation of the player."""
        return f"PlayerScore(name='{self.full_name}', score={self.full_score}, team='{self.team}')"
