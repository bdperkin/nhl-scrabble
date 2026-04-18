"""NHL Scrabble REST API Server.

This module provides a FastAPI-based REST API for programmatic access to NHL Scrabble data.

The API supports:
- Team scores with optional filtering
- Player scores with optional filtering
- Division and conference standings
- Playoff bracket information
- Rate limiting and optional authentication

Example:
    Start the API server::

        $ nhl-scrabble serve --port 8000

    Or with auto-reload for development::

        $ nhl-scrabble serve --reload

    Then access the API::

        $ curl http://localhost:8000/api/v1/teams
        $ curl http://localhost:8000/api/v1/players?min_score=100
"""

from nhl_scrabble.api_server.app import create_app

__all__ = ["create_app"]
