"""API route modules.

This package contains FastAPI route handlers for different API endpoints:

- health: Health check endpoints
- teams: Team score endpoints
- players: Player score endpoints
- standings: Division and conference standings endpoints
"""

from nhl_scrabble.api_server.routes import health, players, standings, teams

__all__ = ["health", "players", "standings", "teams"]
