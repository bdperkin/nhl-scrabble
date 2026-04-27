"""JSON output formatter.

Converts NHL Scrabble analysis data to JSON format with proper indentation and structure for easy
consumption by other programs.
"""

from __future__ import annotations

import json
from typing import Any


class JSONFormatter:
    """Format analysis data as JSON.

    Produces well-formatted JSON output with 2-space indentation, suitable for
    programmatic consumption or storage.

    Example:
        >>> formatter = JSONFormatter()
        >>> data = {"teams": {}, "summary": {}}
        >>> output = formatter.format(data)
        >>> parsed = json.loads(output)
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to JSON string.

        Args:
            data: Analysis data dictionary with structure:
                {
                    "teams": {...},
                    "divisions": {...},
                    "conferences": {...},
                    "playoffs": {...},
                    "summary": {...}
                }

        Returns:
            Pretty-printed JSON string with 2-space indentation

        Example:
            >>> formatter = JSONFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "TOR" in output
            True
        """
        return json.dumps(data, indent=2)
