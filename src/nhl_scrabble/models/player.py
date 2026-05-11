"""Player data models."""

from dataclasses import dataclass
from typing import Any


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
        player_id: NHL player ID (unique identifier, 0 if unknown)
        birthplace: Birthplace city and state/province (e.g., 'Richmond Hill, ON')
        birth_country: ISO country code (e.g., 'CAN', 'USA', 'SWE')
        nationality: Full country name (e.g., 'Canada', 'United States', 'Sweden')
        position_code: Single-letter position code (e.g., 'C', 'L', 'R', 'D', 'G')
        position: Full position name (e.g., 'Center', 'Left Wing', 'Defense', 'Goalie')
        position_type: Position category (e.g., 'Forward', 'Defense', 'Goalie')
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
    player_id: int = 0
    birthplace: str = ""
    birth_country: str = ""
    nationality: str = ""
    position_code: str = ""
    position: str = ""
    position_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of player

        Note:
            This is 2-3x faster than dataclasses.asdict()
            because it uses direct attribute access instead of reflection.

        Examples:
            Convert player to dictionary:

            >>> player = PlayerScore(
            ...     player_id=8478402,
            ...     first_name="Connor",
            ...     last_name="McDavid",
            ...     full_name="Connor McDavid",
            ...     first_score=20,
            ...     last_score=15,
            ...     full_score=35,
            ...     team="EDM",
            ...     division="Pacific",
            ...     conference="Western",
            ...     birthplace="Richmond Hill, ON",
            ...     birth_country="CAN",
            ...     nationality="Canada"
            ... )
            >>> result = player.to_dict()
            >>> result['full_name']
            'Connor McDavid'
            >>> result['full_score']
            35
            >>> result['player_id']
            8478402
        """
        return {
            "player_id": self.player_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "first_score": self.first_score,
            "last_score": self.last_score,
            "full_score": self.full_score,
            "team": self.team,
            "division": self.division,
            "conference": self.conference,
            "birthplace": self.birthplace,
            "birth_country": self.birth_country,
            "nationality": self.nationality,
            "position_code": self.position_code,
            "position": self.position,
            "position_type": self.position_type,
        }

    def __repr__(self) -> str:
        """Return a string representation of the player.

        Examples:
            String representation:

            >>> player = PlayerScore(
            ...     player_id=8478402,
            ...     first_name="Connor",
            ...     last_name="McDavid",
            ...     full_name="Connor McDavid",
            ...     first_score=20,
            ...     last_score=15,
            ...     full_score=35,
            ...     team="EDM",
            ...     division="Pacific",
            ...     conference="Western",
            ...     birthplace="Richmond Hill, ON",
            ...     birth_country="CAN",
            ...     nationality="Canada"
            ... )
            >>> repr(player)
            "PlayerScore(id=8478402, name='Connor McDavid', score=35, team='EDM')"
        """
        return f"PlayerScore(id={self.player_id}, name='{self.full_name}', score={self.full_score}, team='{self.team}')"
