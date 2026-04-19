# Implement Web API Endpoints for NHL Scrabble Analysis

**GitHub Issue**: #104 - https://github.com/bdperkin/nhl-scrabble/issues/104

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Implement comprehensive API endpoints for the NHL Scrabble web interface that integrate with existing analysis functionality. This includes the main analysis endpoint with caching, player/team detail endpoints, and cache management. The endpoints will serve JSON data to the frontend and provide a programmatic interface to the analyzer.

This is part 2 of 5 subtasks for building the complete web interface (broken down from #50).

## Current State

After completing task 002 (FastAPI Infrastructure), we have:

- FastAPI application at `src/nhl_scrabble/web/app.py`
- Health endpoint (`/health`)
- Root endpoint (`/`)
- Basic server infrastructure
- No analysis endpoints
- No caching mechanism
- No integration with core analysis logic

**Current app.py** (from task 002):

```python
from fastapi import FastAPI

app = FastAPI(
    title="NHL Scrabble Analyzer",
    description="Analyze NHL player names by Scrabble score",
    version=__version__,
)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": __version__, "timestamp": ...}

@app.get("/")
async def root():
    return {"message": "NHL Scrabble Analyzer API", "docs": "/docs", "health": "/health"}
```

**Existing core components** (available to integrate):

- `NHLClient` - Fetches data from NHL API
- `TeamProcessor` - Processes team scores
- `PlayoffCalculator` - Calculates playoff brackets
- `ScrabbleScorer` - Scores player names
- Various report generators

## Proposed Solution

Add API endpoints that leverage existing analysis infrastructure with caching for performance.

### 1. Add Analysis Endpoint with Caching

Extend `src/nhl_scrabble/web/app.py`:

```python
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from nhl_scrabble.api import NHLClient
from nhl_scrabble.config import Config
from nhl_scrabble.processors import TeamProcessor, PlayoffCalculator
from nhl_scrabble.scoring import ScrabbleScorer

# ... existing imports and app setup ...

# Cache storage (in-memory for now)
_analysis_cache: dict[str, dict[str, Any]] = {}


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""

    top_players: int = Field(default=20, ge=1, le=100, description="Number of top players to include")
    top_team_players: int = Field(default=5, ge=1, le=30, description="Top players per team")
    use_cache: bool = Field(default=True, description="Use cached results if available")


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""

    timestamp: str
    cache_hit: bool
    top_players: list[dict[str, Any]]
    team_standings: list[dict[str, Any]]
    division_standings: dict[str, list[dict[str, Any]]]
    conference_standings: dict[str, list[dict[str, Any]]]
    playoff_bracket: dict[str, Any]
    stats: dict[str, Any]


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> dict[str, Any]:
    """Run NHL Scrabble analysis.

    Fetches current NHL roster data, calculates Scrabble scores for all players,
    generates standings and playoff bracket. Results are cached for 1 hour.

    Args:
        request: Analysis configuration

    Returns:
        Complete analysis results including players, standings, and playoff bracket

    Raises:
        HTTPException: If NHL API is unavailable or analysis fails
    """
    cache_key = f"{request.top_players}_{request.top_team_players}"

    # Check cache
    if request.use_cache and cache_key in _analysis_cache:
        cached = _analysis_cache[cache_key]
        cache_age = datetime.now() - datetime.fromisoformat(cached["cached_at"])

        if cache_age < timedelta(hours=1):
            return {
                **cached["data"],
                "cache_hit": True,
            }

    # Run analysis
    try:
        config = Config(
            top_players=request.top_players,
            top_team_players=request.top_team_players,
        )

        with NHLClient() as client:
            # Fetch standings
            standings = client.get_standings()

            # Fetch all team rosters and calculate scores
            scorer = ScrabbleScorer()
            all_players = []
            teams_data = []

            for team in standings:
                try:
                    roster = client.get_team_roster(team.team_abbrev)

                    # Score all players
                    team_scores = []
                    for player in roster:
                        score = scorer.score_player(player)
                        all_players.append({
                            "id": player.id,
                            "first_name": player.first_name,
                            "last_name": player.last_name,
                            "team": team.team_abbrev,
                            "score": score.total,
                        })
                        team_scores.append(score)

                    # Calculate team total
                    team_total = sum(s.total for s in team_scores)
                    teams_data.append({
                        "abbrev": team.team_abbrev,
                        "name": team.team_name,
                        "division": team.division,
                        "conference": team.conference,
                        "total_score": team_total,
                        "avg_score": team_total / len(team_scores) if team_scores else 0,
                        "player_count": len(team_scores),
                        "top_players": sorted(
                            team_scores,
                            key=lambda x: x.total,
                            reverse=True
                        )[:request.top_team_players],
                    })

                except Exception as e:
                    # Log error but continue with other teams
                    continue

            # Sort and rank
            all_players.sort(key=lambda x: x["score"], reverse=True)
            teams_data.sort(key=lambda x: x["total_score"], reverse=True)

            # Calculate playoff bracket
            playoff_calc = PlayoffCalculator(teams_data)
            playoff_bracket = playoff_calc.calculate_bracket()

            # Group by division and conference
            divisions = {}
            conferences = {}
            for team in teams_data:
                div = team["division"]
                conf = team["conference"]

                if div not in divisions:
                    divisions[div] = []
                divisions[div].append(team)

                if conf not in conferences:
                    conferences[conf] = []
                conferences[conf].append(team)

            # Calculate stats
            stats = {
                "total_players": len(all_players),
                "total_teams": len(teams_data),
                "highest_score": all_players[0]["score"] if all_players else 0,
                "lowest_score": all_players[-1]["score"] if all_players else 0,
                "avg_score": sum(p["score"] for p in all_players) / len(all_players) if all_players else 0,
                "highest_team": teams_data[0]["abbrev"] if teams_data else None,
                "lowest_team": teams_data[-1]["abbrev"] if teams_data else None,
            }

            # Build response
            result = {
                "timestamp": datetime.now().isoformat(),
                "cache_hit": False,
                "top_players": all_players[:request.top_players],
                "team_standings": teams_data,
                "division_standings": divisions,
                "conference_standings": conferences,
                "playoff_bracket": playoff_bracket,
                "stats": stats,
            }

            # Cache result
            _analysis_cache[cache_key] = {
                "cached_at": datetime.now().isoformat(),
                "data": result,
            }

            return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/players/{player_id}")
async def get_player(player_id: int) -> dict[str, Any]:
    """Get details for a specific player.

    Args:
        player_id: NHL player ID

    Returns:
        Player details including score and team

    Raises:
        HTTPException: If player not found
    """
    # Search cache for player
    for cached in _analysis_cache.values():
        for player in cached["data"]["top_players"]:
            if player["id"] == player_id:
                return player

    raise HTTPException(status_code=404, detail=f"Player {player_id} not found")


@app.get("/api/teams/{team_abbrev}")
async def get_team(team_abbrev: str) -> dict[str, Any]:
    """Get details for a specific team.

    Args:
        team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')

    Returns:
        Team details including score and roster

    Raises:
        HTTPException: If team not found
    """
    # Search cache for team
    for cached in _analysis_cache.values():
        for team in cached["data"]["team_standings"]:
            if team["abbrev"].upper() == team_abbrev.upper():
                return team

    raise HTTPException(status_code=404, detail=f"Team {team_abbrev} not found")


@app.delete("/api/cache/clear")
async def clear_cache() -> dict[str, str]:
    """Clear the analysis cache.

    Returns:
        Confirmation message
    """
    _analysis_cache.clear()
    return {
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/cache/stats")
async def cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Cache statistics including size and entries
    """
    entries = []
    for key, cached in _analysis_cache.items():
        cache_age = datetime.now() - datetime.fromisoformat(cached["cached_at"])
        entries.append({
            "key": key,
            "cached_at": cached["cached_at"],
            "age_seconds": cache_age.total_seconds(),
            "expires_in_seconds": max(0, 3600 - cache_age.total_seconds()),
        })

    return {
        "size": len(_analysis_cache),
        "entries": entries,
    }
```

## Implementation Steps

1. **Add Pydantic Models**

   - Create `AnalysisRequest` model with validation
   - Create `AnalysisResponse` model for type safety
   - Add field validators and documentation

1. **Implement Analysis Endpoint**

   - Add `/api/analyze` POST endpoint
   - Integrate with `NHLClient`, `ScrabbleScorer`, `TeamProcessor`
   - Implement caching logic with 1-hour expiration
   - Handle errors gracefully
   - Return comprehensive JSON response

1. **Implement Player Endpoint**

   - Add `/api/players/{player_id}` GET endpoint
   - Search cached analysis results
   - Return 404 if not found
   - Include player score and team info

1. **Implement Team Endpoint**

   - Add `/api/teams/{team_abbrev}` GET endpoint
   - Search cached analysis results
   - Return 404 if not found
   - Include team score and top players

1. **Implement Cache Management**

   - Add `/api/cache/clear` DELETE endpoint
   - Add `/api/cache/stats` GET endpoint for monitoring
   - Clear expired entries automatically

1. **Add Tests**

   - Test analysis endpoint with different parameters
   - Test caching behavior
   - Test player/team endpoints
   - Test cache management
   - Test error handling

1. **Update Documentation**

   - Update OpenAPI docs (automatic via FastAPI)
   - Add usage examples to README
   - Update CHANGELOG

## Testing Strategy

### Integration Tests

Create `tests/integration/test_web_api.py`:

```python
"""Integration tests for web API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_analyze_endpoint_success(client: TestClient) -> None:
    """Test analysis endpoint returns valid data."""
    response = client.post(
        "/api/analyze",
        json={"top_players": 10, "top_team_players": 3, "use_cache": False}
    )

    assert response.status_code == 200
    data = response.json()

    assert "timestamp" in data
    assert "cache_hit" in data
    assert data["cache_hit"] is False
    assert "top_players" in data
    assert "team_standings" in data
    assert "playoff_bracket" in data
    assert "stats" in data

    # Verify top players structure
    assert len(data["top_players"]) <= 10
    if data["top_players"]:
        player = data["top_players"][0]
        assert "id" in player
        assert "first_name" in player
        assert "last_name" in player
        assert "score" in player
        assert "team" in player


def test_analyze_endpoint_caching(client: TestClient) -> None:
    """Test analysis endpoint uses cache."""
    # First request (cache miss)
    response1 = client.post(
        "/api/analyze",
        json={"top_players": 20, "top_team_players": 5, "use_cache": True}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["cache_hit"] is False

    # Second request (cache hit)
    response2 = client.post(
        "/api/analyze",
        json={"top_players": 20, "top_team_players": 5, "use_cache": True}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["cache_hit"] is True

    # Same timestamp indicates cached result
    assert data1["timestamp"] == data2["timestamp"]


def test_analyze_endpoint_validation(client: TestClient) -> None:
    """Test analysis endpoint validates parameters."""
    # Invalid top_players (too high)
    response = client.post(
        "/api/analyze",
        json={"top_players": 200}
    )
    assert response.status_code == 422  # Validation error

    # Invalid top_players (negative)
    response = client.post(
        "/api/analyze",
        json={"top_players": -5}
    )
    assert response.status_code == 422


def test_get_player_found(client: TestClient) -> None:
    """Test player endpoint returns player data."""
    # First run analysis to populate cache
    client.post("/api/analyze", json={"top_players": 20, "use_cache": False})

    # Then get a player (use ID from analysis)
    # This is a simplified test - real test would use actual player ID
    response = client.get("/api/players/8478402")

    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "score" in data


def test_get_player_not_found(client: TestClient) -> None:
    """Test player endpoint returns 404 for unknown player."""
    response = client.get("/api/players/99999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_team_found(client: TestClient) -> None:
    """Test team endpoint returns team data."""
    # First run analysis to populate cache
    client.post("/api/analyze", json={"use_cache": False})

    # Then get a team
    response = client.get("/api/teams/TOR")

    if response.status_code == 200:
        data = response.json()
        assert "abbrev" in data
        assert "total_score" in data
        assert "top_players" in data


def test_get_team_not_found(client: TestClient) -> None:
    """Test team endpoint returns 404 for unknown team."""
    response = client.get("/api/teams/XXX")

    assert response.status_code == 404


def test_clear_cache(client: TestClient) -> None:
    """Test cache clear endpoint."""
    # Populate cache
    client.post("/api/analyze", json={"use_cache": False})

    # Clear cache
    response = client.delete("/api/cache/clear")

    assert response.status_code == 200
    assert "cleared" in response.json()["message"].lower()

    # Verify cache is empty
    stats_response = client.get("/api/cache/stats")
    assert stats_response.json()["size"] == 0


def test_cache_stats(client: TestClient) -> None:
    """Test cache stats endpoint."""
    # Clear cache first
    client.delete("/api/cache/clear")

    # Get initial stats
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    assert response.json()["size"] == 0

    # Populate cache
    client.post("/api/analyze", json={"use_cache": False})

    # Get stats again
    response = client.get("/api/cache/stats")
    data = response.json()
    assert data["size"] == 1
    assert len(data["entries"]) == 1
    assert "age_seconds" in data["entries"][0]
    assert "expires_in_seconds" in data["entries"][0]
```

### Manual Testing

```bash
# Start server
nhl-scrabble serve --reload

# Test analysis endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"top_players": 20, "top_team_players": 5, "use_cache": true}'

# Test with different parameters
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"top_players": 10, "top_team_players": 3, "use_cache": false}'

# Test player endpoint
curl http://localhost:8000/api/players/8478402

# Test team endpoint
curl http://localhost:8000/api/teams/TOR
curl http://localhost:8000/api/teams/MTL

# Test cache stats
curl http://localhost:8000/api/cache/stats

# Test cache clear
curl -X DELETE http://localhost:8000/api/cache/clear

# View OpenAPI docs
open http://localhost:8000/docs
```

## Acceptance Criteria

- [ ] `/api/analyze` POST endpoint implemented
- [ ] Analysis endpoint accepts `top_players`, `top_team_players`, `use_cache` parameters
- [ ] Parameter validation works (Pydantic models)
- [ ] Analysis integrates with `NHLClient`, `ScrabbleScorer`, etc.
- [ ] Caching mechanism works with 1-hour expiration
- [ ] Cache hits return same data without re-fetching
- [ ] `/api/players/{player_id}` endpoint implemented
- [ ] `/api/teams/{team_abbrev}` endpoint implemented
- [ ] Both endpoints return 404 for not found
- [ ] `/api/cache/clear` endpoint implemented
- [ ] `/api/cache/stats` endpoint implemented
- [ ] All endpoints have proper error handling
- [ ] OpenAPI docs include all new endpoints
- [ ] Integration tests pass for all endpoints
- [ ] Manual testing confirms functionality
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/web/app.py` - Add endpoints
- `tests/integration/test_web_api.py` - New tests
- `README.md` - Update with API usage
- `CHANGELOG.md` - Document new endpoints

## Dependencies

**Required**: Task new-features/002 (FastAPI Infrastructure) must be completed first

This task builds upon the FastAPI application structure created in task 002.

## Additional Notes

### Caching Strategy

**In-Memory Cache** (current implementation):

- Simple dictionary-based cache
- 1-hour expiration
- Lost on server restart
- Good for development and small-scale deployment

**Future Improvements** (not in this task):

- Redis for distributed caching
- Persistent cache across restarts
- Cache invalidation strategies
- Configurable expiration times

### API Design Decisions

**POST vs GET for /api/analyze**:

- Using POST because it has a request body
- Allows complex parameters without URL encoding
- Follows REST conventions for non-idempotent operations

**Cache Key Strategy**:

- Key: `"{top_players}_{top_team_players}"`
- Simple and effective
- Different parameter combinations get separate cache entries

**Error Handling**:

- 422 for validation errors (Pydantic automatic)
- 404 for not found (players/teams)
- 500 for analysis failures
- Detailed error messages in responses

### Performance Considerations

**First Request** (cache miss):

- Fetches data for all ~32 NHL teams
- Scores ~700 players
- Takes ~30-60 seconds depending on API response time
- This is why caching is critical

**Cached Requests**:

- Instant response (~10ms)
- No NHL API calls
- Excellent user experience

**Optimization Opportunities** (future):

- Background refresh of cache before expiration
- Partial caching (cache team rosters separately)
- Streaming responses for large datasets

### Security Considerations

**No Authentication Yet**:

- Public API (for now)
- No rate limiting (yet)
- No user-specific data

**Input Validation**:

- Pydantic models validate all inputs
- Prevents injection attacks
- Clear error messages

**Future Security** (not this task):

- Rate limiting per IP
- API key authentication
- CORS configuration
- Request size limits

### Testing Notes

**Mock vs Real NHL API**:

- Integration tests use real NHL API (slower but accurate)
- Consider adding unit tests with mocked NHLClient
- Use `pytest-mock` for mocking if needed

**Test Data Freshness**:

- Tests depend on current NHL data
- Player/team IDs may change between seasons
- Tests should be resilient to data changes

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
