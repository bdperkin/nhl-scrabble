"""NHL Roster Scrabble Score Analyzer.

A tool for fetching NHL roster data and calculating Scrabble scores for player names.
"""

__version__ = "2.1.0"
__author__ = "Brandon Perkins"

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.exceptions import ValidationError
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

__all__ = [
    "NHLApiClient",
    "ScrabbleScorer",
    "ValidationError",
    "__version__",
]
