# Add Standalone REST API Server

**GitHub Issue**: #150 - https://github.com/bdperkin/nhl-scrabble/issues/150

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Create a standalone REST API server (separate from web interface) for programmatic access to NHL Scrabble data.

Enables third-party integrations, mobile apps, and custom clients.

## Proposed Solution

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="NHL Scrabble API")

@app.get("/api/v1/teams")
async def get_teams(division: Optional[str] = None):
    """Get all team scores."""
    pass

@app.get("/api/v1/teams/{abbrev}")
async def get_team(abbrev: str):
    """Get specific team score."""
    pass

@app.get("/api/v1/players")
async def get_players(min_score: Optional[int] = Query(None)):
    """Get all players with optional filtering."""
    pass

@app.get("/api/v1/standings/{type}")
async def get_standings(type: str):
    """Get standings (division/conference)."""
    pass
```

```bash
# Start API server
nhl-scrabble serve --port 8000

# With auto-reload
nhl-scrabble serve --reload

# Production mode
gunicorn nhl_scrabble.api:app
```

## Implementation Steps

1. Create FastAPI application
1. Implement API endpoints
1. Add OpenAPI documentation
1. Add authentication (optional)
1. Add rate limiting
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] REST API endpoints implemented
- [ ] OpenAPI docs generated
- [ ] Authentication supported
- [ ] Rate limiting added
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/api_server/` - New module
- `src/nhl_scrabble/cli.py` - Add serve command

## Dependencies

- `fastapi` (new dependency)
- `uvicorn` (new dependency)

## Additional Notes

**Benefits**: Programmatic access, third-party integrations, API ecosystem

## Implementation Notes

*To be filled during implementation*
