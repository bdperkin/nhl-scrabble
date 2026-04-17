# Add Historical Data Support

**GitHub Issue**: #143 - https://github.com/bdperkin/nhl-scrabble/issues/143

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Add support for analyzing historical NHL seasons to track Scrabble score trends over time, compare past seasons, and identify patterns.

Currently only supports current season data. Users cannot:

- View historical Scrabble scores
- Compare seasons (e.g., 2022-23 vs 2023-24)
- Track score trends
- Analyze roster changes impact

## Proposed Solution

### 1. Historical Data API

```python
class NHLApiClient:
    def get_standings_for_season(self, season: str) -> Standings:
        """Fetch standings for specific season (e.g., '20232024')."""
        url = f"https://api-web.nhle.com/v1/standings/{season}"
        return self._fetch(url)

    def get_roster_for_season(self, team_abbrev: str, season: str) -> TeamRoster:
        """Fetch team roster for specific season."""
        url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/{season}"
        return self._fetch(url)
```

### 2. CLI Support

```bash
# Analyze specific season
nhl-scrabble analyze --season 20222023

# Compare seasons
nhl-scrabble compare --seasons 20222023,20232024

# Show trends
nhl-scrabble trends --start 20202021 --end 20232024
```

### 3. Data Storage

```python
# Store historical data locally
import json
from pathlib import Path

class HistoricalDataStore:
    def __init__(self, data_dir: Path = Path("data/historical")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_season(self, season: str, data: dict):
        file_path = self.data_dir / f"{season}.json"
        with file_path.open("w") as f:
            json.dump(data, f, indent=2)

    def load_season(self, season: str) -> dict | None:
        file_path = self.data_dir / f"{season}.json"
        if not file_path.exists():
            return None

        with file_path.open() as f:
            return json.load(f)
```

## Implementation Steps

1. Research NHL API historical endpoints
1. Add season parameter to API client
1. Create historical data storage
1. Add CLI options for seasons
1. Implement season comparison reports
1. Add trend analysis
1. Add tests
1. Update documentation

## Acceptance Criteria

- [ ] Can analyze historical seasons
- [ ] Can compare multiple seasons
- [ ] Historical data cached locally
- [ ] Trend analysis implemented
- [ ] CLI options added
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Add historical endpoints
- `src/nhl_scrabble/storage/historical.py` - New storage module
- `src/nhl_scrabble/reports/comparison.py` - Season comparison
- `src/nhl_scrabble/cli.py` - Add season options

## Dependencies

None (uses existing NHL API)

## Additional Notes

**Challenges**:

- NHL API historical data availability
- Data format changes between seasons
- Storage space for multiple seasons

**Benefits**:

- Track score evolution
- Identify roster changes impact
- Historical analysis

## Implementation Notes

*To be filled during implementation*
