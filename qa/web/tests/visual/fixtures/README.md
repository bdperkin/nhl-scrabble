# NHL API Test Fixtures

Mocked NHL API data for visual regression tests.

## Overview

These fixtures contain snapshots of NHL API data captured at a specific point in time.
They are used by visual regression tests to ensure deterministic test results regardless
of current NHL standings, rosters, or game outcomes.

## Files

- **nhl_standings.json**: Team standings data from `/standings/now` endpoint
- **nhl_rosters.json**: Player roster data for all teams from `/roster/{team}/current` endpoints

## Data Snapshot

- **Captured**: 2026-05-01 09:58:52
- **Teams**: 32 teams
- **Total Players**: 862 players
- **Season**: 2024-2025 (current)

## Structure

### nhl_standings.json

Contains standings data with the following structure:

```json
{
  "standings": [
    {
      "teamAbbrev": {"default": "TOR"},
      "teamName": {"default": "Maple Leafs"},
      "divisionName": "Atlantic",
      "conferenceName": "Eastern",
      "wins": 50,
      "losses": 20,
      "points": 110,
      ...
    }
  ]
}
```

### nhl_rosters.json

Contains roster data for each team with the following structure:

```json
{
  "TOR": {
    "forwards": [
      {
        "id": 12345,
        "firstName": {"default": "Auston"},
        "lastName": {"default": "Matthews"},
        ...
      }
    ],
    "defensemen": [...],
    "goalies": [...]
  },
  "MTL": {...}
}
```

## Updating Fixtures

Fixtures should be updated when:

1. **NHL season changes** (rosters and standings reset)
1. **Major UI changes** affect data display format
1. **API schema changes** (new fields, structure changes)
1. **Annually at minimum** to keep data realistic

### How to Update

Run the capture script:

```bash
./scripts/capture-nhl-fixtures
```

This will:

1. Fetch current standings from NHL API
1. Fetch current rosters for all teams
1. Save data to this directory
1. Regenerate baselines if needed

After updating fixtures, regenerate visual test baselines:

```bash
./scripts/pytest-playwright qa/web/tests/visual/ --update-snapshots \
  --browser chromium --browser firefox --browser webkit
```

## Testing with Fixtures

Visual tests automatically use these fixtures via mocking in `conftest.py`.
The mocking is transparent to test code - tests don't need to know they're
using mocked data.

## Maintenance

- **Review Period**: Annually
- **Last Updated**: 2026-05-01
- **Next Review**: 2027-01-01
