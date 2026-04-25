"""NHL Roster Scrabble Score Analyzer.

A tool for fetching NHL roster data and calculating Scrabble scores for player names.
"""

try:
    from nhl_scrabble._version import __version__
except ImportError:
    # Fallback for development without build
    __version__ = "0.0.0+unknown"

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
