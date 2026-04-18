"""Health check endpoints.

Provides health check and readiness endpoints for monitoring and load balancers.

Example:
    Check API health::

        $ curl http://localhost:8000/health
        {"status": "healthy", "service": "nhl-scrabble-api", "version": "1.0.0"}
"""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", response_class=JSONResponse)
async def health() -> dict[str, Any]:
    """Health check endpoint.

    Returns basic health status for monitoring and load balancers.

    Returns:
        dict: Health status information.

    Example:
        >>> response = await health()
        >>> assert response["status"] == "healthy"
    """
    return {
        "status": "healthy",
        "service": "nhl-scrabble-api",
        "version": "1.0.0",
    }
