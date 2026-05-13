"""Cache management routes.

This module contains routes for cache management operations.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from nhl_scrabble.web.routes.core import get_analysis_cache

router = APIRouter()


@router.delete("/api/cache/clear")
async def clear_cache() -> dict[str, str]:
    """Clear the analysis cache.

    Returns:
        Confirmation message
    """
    _analysis_cache = get_analysis_cache()
    _analysis_cache.clear()
    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/api/cache/stats")
async def cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Cache statistics including size and entries
    """
    _analysis_cache = get_analysis_cache()
    entries = []
    for key, cached in _analysis_cache.items():
        cache_age = datetime.now(UTC) - datetime.fromisoformat(cached["cached_at"])
        entries.append(
            {
                "key": key,
                "cached_at": cached["cached_at"],
                "age_seconds": cache_age.total_seconds(),
                "expires_in_seconds": max(0, 3600 - cache_age.total_seconds()),
            },
        )

    return {
        "size": len(_analysis_cache),
        "entries": entries,
    }
