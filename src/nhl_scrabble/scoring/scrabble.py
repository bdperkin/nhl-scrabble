"""Scrabble scoring logic for player names."""

from __future__ import annotations

from typing import Any, ClassVar

from nhl_scrabble.models.player import PlayerScore


class ScrabbleScorer:
    """Calculate Scrabble scores for player names using standard letter values.

    This class provides methods to calculate Scrabble scores based on the
    standard English Scrabble letter point values.

    Letter values:
        - 1 point: A, E, I, O, U, L, N, S, T, R
        - 2 points: D, G
        - 3 points: B, C, M, P
        - 4 points: F, H, V, W, Y
        - 5 points: K
        - 8 points: J, X
        - 10 points: Q, Z
    """

    LETTER_VALUES: ClassVar[dict[str, int]] = {
        "A": 1,
        "E": 1,
        "I": 1,
        "O": 1,
        "U": 1,
        "L": 1,
        "N": 1,
        "S": 1,
        "T": 1,
        "R": 1,
        "D": 2,
        "G": 2,
        "B": 3,
        "C": 3,
        "M": 3,
        "P": 3,
        "F": 4,
        "H": 4,
        "V": 4,
        "W": 4,
        "Y": 4,
        "K": 5,
        "J": 8,
        "X": 8,
        "Q": 10,
        "Z": 10,
    }

    def calculate_score(self, name: str) -> int:
        """Calculate the Scrabble score for a given name.

        Args:
            name: The name to score (can include spaces and special characters)

        Returns:
            The total Scrabble score (non-letter characters are worth 0 points)

        Examples:
            >>> scorer = ScrabbleScorer()
            >>> scorer.calculate_score("ALEX")
            11
            >>> scorer.calculate_score("Ovechkin")
            22
        """
        return sum(self.LETTER_VALUES.get(char.upper(), 0) for char in name)

    def score_player(
        self, player_data: dict[str, Any], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Score a player and return a PlayerScore object.

        Args:
            player_data: Dictionary with 'firstName' and 'lastName' keys containing 'default' values
            team: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            PlayerScore object with all scoring information

        Examples:
            >>> scorer = ScrabbleScorer()
            >>> player = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}
            >>> result = scorer.score_player(player, "EDM", "Pacific", "Western")
            >>> result.full_score
            32
        """
        first_name = player_data["firstName"]["default"]
        last_name = player_data["lastName"]["default"]
        full_name = f"{first_name} {last_name}"

        first_score = self.calculate_score(first_name)
        last_score = self.calculate_score(last_name)
        full_score = first_score + last_score

        return PlayerScore(
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            first_score=first_score,
            last_score=last_score,
            full_score=full_score,
            team=team,
            division=division,
            conference=conference,
        )
