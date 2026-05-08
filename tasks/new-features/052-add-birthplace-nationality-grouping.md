# Add Birthplace (Nationality) as Grouping Category

**GitHub Issue**: [#551](https://github.com/bdperkin/nhl-scrabble/issues/551)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

12-16 hours

## Description

Add birthplace (nationality) as a grouping category for listing, filtering, and analysis across all interface types (analyze, dashboard, interactive, search, WebUI). This enhancement will allow users to:

- View player rankings grouped by country/birthplace
- Filter players by nationality
- Compare Scrabble scores across different countries
- Generate country-specific reports and standings

Currently, the system groups players by team, division, and conference. Adding birthplace/nationality as a fourth grouping dimension provides valuable insights into international player contributions.

## Current State

**PlayerScore Model** (`src/nhl_scrabble/models/player.py`):
```python
@dataclass(slots=True)
class PlayerScore:
    """Represents a player with their Scrabble score information."""

    first_name: str
    last_name: str
    full_name: str
    first_score: int
    last_score: int
    full_score: int
    team: str
    division: str
    conference: str
```

**Current Groupings**:
- Team (e.g., TOR, MTL, EDM)
- Division (e.g., Atlantic, Metropolitan, Central, Pacific)
- Conference (e.g., Eastern, Western)

**NHL API Roster Response** (from `api-web.nhle.com/v1/roster/{team}/current`):

The NHL API typically provides birthplace information in player data:
```json
{
  "forwards": [
    {
      "firstName": {"default": "Connor"},
      "lastName": {"default": "McDavid"},
      "birthCity": {"default": "Richmond Hill"},
      "birthStateProvince": {"default": "ON"},
      "birthCountry": "CAN"
    }
  ]
}
```

**Note**: Need to verify if current NHL API endpoint includes birthplace data or if we need to fetch from player detail endpoint.

## Proposed Solution

### 1. Data Model Updates

**Update PlayerScore** (`src/nhl_scrabble/models/player.py`):
```python
@dataclass(slots=True)
class PlayerScore:
    """Represents a player with their Scrabble score information."""

    first_name: str
    last_name: str
    full_name: str
    first_score: int
    last_score: int
    full_score: int
    team: str
    division: str
    conference: str
    birthplace: str  # NEW: "City, Province/State" (e.g., "Richmond Hill, ON")
    birth_country: str  # NEW: ISO country code (e.g., "CAN", "USA", "SWE")
    nationality: str  # NEW: Full country name (e.g., "Canada", "United States", "Sweden")
```

**Add Country Mapping** (`src/nhl_scrabble/utils/countries.py`):
```python
"""Country code to full name mapping for internationalization."""

COUNTRY_CODES = {
    "CAN": "Canada",
    "USA": "United States",
    "SWE": "Sweden",
    "FIN": "Finland",
    "RUS": "Russia",
    "CZE": "Czech Republic",
    "SVK": "Slovakia",
    "CHE": "Switzerland",
    "DEU": "Germany",
    "LVA": "Latvia",
    # ... all NHL player countries
}

def get_country_name(country_code: str) -> str:
    """Convert ISO country code to full name."""
    return COUNTRY_CODES.get(country_code, country_code)
```

### 2. API Client Updates

**Update NHLApiClient.get_team_roster()** (`src/nhl_scrabble/api/nhl_client.py`):
```python
def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
    """Fetch team roster with birthplace data.

    Returns:
        Dictionary with forwards, defensemen, goalies, each including:
        - firstName, lastName
        - birthCity, birthStateProvince, birthCountry (if available)
    """
    # Existing implementation, verify birthplace fields are included
    # If not, may need to fetch from player detail endpoint
```

**Alternative: Fetch Player Details** (if roster endpoint lacks birthplace):
```python
def get_player_details(self, player_id: str) -> dict[str, Any]:
    """Fetch detailed player information including birthplace.

    Args:
        player_id: NHL player ID

    Returns:
        Player details including birthCity, birthCountry, etc.
    """
    endpoint = f"/player/{player_id}/landing"
    return self._make_request(endpoint)
```

### 3. Processor Updates

**Update TeamProcessor** (`src/nhl_scrabble/processors/team_processor.py`):
```python
def process_team_data(self, team_data: dict[str, Any]) -> list[PlayerScore]:
    """Process team roster with birthplace information."""
    players = []

    for position in ("forwards", "defensemen", "goalies"):
        for player in team_data.get(position, []):
            # Extract birthplace data
            birth_city = player.get("birthCity", {}).get("default", "")
            birth_state = player.get("birthStateProvince", {}).get("default", "")
            birth_country_code = player.get("birthCountry", "")

            # Format birthplace
            birthplace = f"{birth_city}, {birth_state}" if birth_state else birth_city
            nationality = get_country_name(birth_country_code)

            # Create PlayerScore with birthplace
            player_score = PlayerScore(
                # ... existing fields
                birthplace=birthplace,
                birth_country=birth_country_code,
                nationality=nationality,
            )
            players.append(player_score)

    return players
```

### 4. Grouping and Filtering

**Add Country Grouping** (`src/nhl_scrabble/processors/grouping.py` - new file):
```python
"""Player grouping utilities."""

from collections import defaultdict
from typing import Any

from nhl_scrabble.models.player import PlayerScore


def group_by_nationality(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by nationality.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping nationality to list of players
    """
    grouped = defaultdict(list)
    for player in players:
        grouped[player.nationality].append(player)
    return dict(grouped)


def group_by_birth_country(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by birth country code.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping country code to list of players
    """
    grouped = defaultdict(list)
    for player in players:
        grouped[player.birth_country].append(player)
    return dict(grouped)
```

### 5. CLI Updates

**Add Nationality Options** (`src/nhl_scrabble/cli.py`):
```python
@click.option(
    "--group-by",
    type=click.Choice(["team", "division", "conference", "nationality"]),
    default="team",
    help="Group players by team, division, conference, or nationality",
)
@click.option(
    "--filter-country",
    type=str,
    default=None,
    help="Filter players by country code (e.g., CAN, USA, SWE)",
)
def analyze(
    top_players: int,
    top_team_players: int,
    use_cache: bool,
    group_by: str,
    filter_country: str | None,
) -> None:
    """Analyze NHL player Scrabble scores."""
    # Apply grouping and filtering
```

### 6. Web Interface Updates

**Add Nationality Pages** (`src/nhl_scrabble/web/app.py`):
```python
@app.get("/nationalities", response_class=HTMLResponse)
async def nationalities_page(request: Request) -> HTMLResponse:
    """Nationality standings page - all countries ranked by total score."""
    # Group by nationality, calculate totals, sort by score

@app.get("/nationalities/{country_code}", response_class=HTMLResponse)
async def nationality_detail_page(
    request: Request,
    country_code: str,
) -> HTMLResponse:
    """Nationality detail page - all players from a specific country."""
    # Filter by country, show all players with rankings
```

**Add Menu Item** (`src/nhl_scrabble/web/templates/base.html`):
```html
<nav>
  <a href="/">Home</a>
  <a href="/teams">Teams</a>
  <a href="/divisions">Divisions</a>
  <a href="/conferences">Conferences</a>
  <a href="/nationalities">Nationalities</a>  <!-- NEW -->
  <a href="/playoffs">Playoffs</a>
  <a href="/stats">Stats</a>
</nav>
```

### 7. Report Updates

**Add Nationality Report** (`src/nhl_scrabble/reports/nationality_report.py` - new file):
```python
"""Nationality-based Scrabble score report."""

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.processors.grouping import group_by_nationality
from nhl_scrabble.reports.base import BaseReport


class NationalityReport(BaseReport):
    """Generate nationality standings report."""

    def generate(self, players: list[PlayerScore]) -> str:
        """Generate nationality standings with player counts and scores."""
        grouped = group_by_nationality(players)

        # Calculate standings
        standings = []
        for nationality, country_players in grouped.items():
            total_score = sum(p.full_score for p in country_players)
            avg_score = total_score / len(country_players)
            standings.append({
                "nationality": nationality,
                "players": len(country_players),
                "total_score": total_score,
                "average_score": avg_score,
            })

        # Sort by total score
        standings.sort(key=lambda x: x["total_score"], reverse=True)

        # Format report
        return self._format_standings(standings)
```

## Implementation Steps

1. **Investigate NHL API** (1-2h)
   - Verify birthplace data availability in roster endpoint
   - Test player detail endpoint if needed
   - Document API response structure
   - Identify all country codes used by NHL players

2. **Update Data Models** (2-3h)
   - Add birthplace, birth_country, nationality to PlayerScore
   - Create country code mapping utility
   - Update to_dict() method
   - Update serialization/deserialization

3. **Update API Client and Processors** (2-3h)
   - Fetch birthplace data from NHL API
   - Extract and format birthplace information
   - Handle missing/incomplete birthplace data
   - Add validation for country codes

4. **Implement Grouping and Filtering** (2-3h)
   - Create grouping utility functions
   - Add nationality-based filtering
   - Update existing processors to support nationality grouping
   - Optimize grouping performance

5. **Update CLI Interface** (1-2h)
   - Add --group-by nationality option
   - Add --filter-country option
   - Update help text and documentation
   - Add nationality report output

6. **Update Web Interface** (3-4h)
   - Create /nationalities page (list all countries)
   - Create /nationalities/{country_code} detail page
   - Add Nationalities menu item
   - Update templates with i18n support
   - Add nationality links to player listings

7. **Add Reports** (1-2h)
   - Create NationalityReport class
   - Add nationality standings formatting
   - Support JSON export
   - Add nationality filters to existing reports

8. **Testing** (2-3h)
   - Unit tests for country mapping
   - Unit tests for grouping functions
   - Integration tests for API data fetching
   - Web interface tests for nationality pages
   - CLI tests for nationality options

9. **Documentation** (1h)
   - Update README with nationality features
   - Add API documentation for new endpoints
   - Update CLI help text
   - Add examples to user guide

## Testing Strategy

### Unit Tests

**Test Country Mapping** (`tests/unit/utils/test_countries.py`):
```python
def test_country_code_mapping():
    """Test country code to name conversion."""
    assert get_country_name("CAN") == "Canada"
    assert get_country_name("USA") == "United States"
    assert get_country_name("SWE") == "Sweden"

def test_unknown_country_code():
    """Test handling of unknown country codes."""
    assert get_country_name("XXX") == "XXX"  # Returns code if unknown
```

**Test Grouping Functions** (`tests/unit/processors/test_grouping.py`):
```python
def test_group_by_nationality():
    """Test grouping players by nationality."""
    players = [
        PlayerScore(..., nationality="Canada"),
        PlayerScore(..., nationality="Canada"),
        PlayerScore(..., nationality="Sweden"),
    ]

    grouped = group_by_nationality(players)
    assert len(grouped["Canada"]) == 2
    assert len(grouped["Sweden"]) == 1

def test_group_by_birth_country():
    """Test grouping by country code."""
    players = [
        PlayerScore(..., birth_country="CAN"),
        PlayerScore(..., birth_country="SWE"),
    ]

    grouped = group_by_birth_country(players)
    assert "CAN" in grouped
    assert "SWE" in grouped
```

### Integration Tests

**Test NHL API Birthplace Data** (`tests/integration/test_nhl_api_birthplace.py`):
```python
def test_roster_includes_birthplace():
    """Test that roster API includes birthplace data."""
    client = NHLApiClient()
    roster = client.get_team_roster("TOR")

    # Verify birthplace fields exist
    player = roster["forwards"][0]
    assert "birthCity" in player or "birthCountry" in player
```

**Test Web Nationality Pages** (`tests/integration/test_web_nationality.py`):
```python
def test_nationalities_page_exists(client: TestClient):
    """Test nationality standings page."""
    response = client.get("/nationalities")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_nationality_detail_page(client: TestClient):
    """Test nationality detail page for Canada."""
    response = client.get("/nationalities/CAN")
    assert response.status_code == 200
    assert "Canada" in response.text
```

### Functional Tests (Playwright)

**Test Nationality Navigation** (`qa/web/tests/functional/test_nationality_pages.py`):
```python
@pytest.mark.parametrize("country_code", ["CAN", "USA", "SWE", "FIN"])
def test_nationality_page_loads(page, country_code):
    """Test nationality detail pages load correctly."""
    page.goto(f"/nationalities/{country_code}")
    expect(page.locator("h1")).to_be_visible()
```

### Manual Testing

1. Run CLI with nationality grouping:
   ```bash
   nhl-scrabble analyze --group-by nationality
   nhl-scrabble analyze --filter-country CAN
   ```

2. Test web interface:
   - Navigate to /nationalities
   - Verify all countries listed
   - Click on Canada
   - Verify all Canadian players shown
   - Check player count and total scores

3. Test i18n:
   - Switch to French Canadian locale
   - Verify nationality names translated
   - Verify country names localized

## Acceptance Criteria

- [ ] PlayerScore model includes birthplace, birth_country, and nationality fields
- [ ] Country code mapping utility created with all NHL countries
- [ ] NHL API client fetches birthplace data successfully
- [ ] Players can be grouped by nationality in all interfaces
- [ ] Players can be filtered by country code
- [ ] CLI supports `--group-by nationality` and `--filter-country` options
- [ ] Web interface includes /nationalities page with standings
- [ ] Web interface includes /nationalities/{country_code} detail pages
- [ ] Nationalities menu item added to web navigation
- [ ] Nationality report class implemented
- [ ] All grouping functions have unit tests
- [ ] Web nationality pages have integration tests
- [ ] Functional tests cover nationality navigation
- [ ] Documentation updated with nationality features
- [ ] All tests pass (unit, integration, functional)
- [ ] Type checking passes (mypy)
- [ ] Pre-commit hooks pass
- [ ] i18n support for nationality names

## Related Files

- `src/nhl_scrabble/models/player.py` - PlayerScore model updates
- `src/nhl_scrabble/utils/countries.py` - NEW: Country code mapping
- `src/nhl_scrabble/api/nhl_client.py` - API client birthplace fetching
- `src/nhl_scrabble/processors/team_processor.py` - Process birthplace data
- `src/nhl_scrabble/processors/grouping.py` - NEW: Grouping utilities
- `src/nhl_scrabble/reports/nationality_report.py` - NEW: Nationality report
- `src/nhl_scrabble/cli.py` - CLI nationality options
- `src/nhl_scrabble/web/app.py` - Web nationality routes
- `src/nhl_scrabble/web/templates/nationalities.html` - NEW: Nationality list page
- `src/nhl_scrabble/web/templates/nationality_detail.html` - NEW: Country detail page
- `src/nhl_scrabble/web/templates/base.html` - Navigation menu update
- `tests/unit/utils/test_countries.py` - NEW: Country mapping tests
- `tests/unit/processors/test_grouping.py` - NEW: Grouping tests
- `tests/integration/test_web_nationality.py` - NEW: Web nationality tests
- `qa/web/tests/functional/test_nationality_pages.py` - NEW: Functional tests

## Dependencies

**None** - This is a standalone feature addition.

**Optional Enhancements** (future tasks):
- Country flag icons in web interface
- Nationality-based playoff brackets
- Historical nationality statistics
- Nationality vs team comparison reports

## Additional Notes

### Performance Considerations

- **Caching**: Birthplace data should be cached with roster data
- **Grouping**: Pre-compute nationality groupings for web pages
- **API Calls**: Verify no additional API calls needed for birthplace data

### I18n Considerations

- **Country Names**: Add translations for all country names
  ```python
  # In locale files
  msgid "Canada"
  msgstr "Canada"  # en_US
  msgstr "Canada"  # fr_CA
  msgstr "Kanada"  # sv_SE
  ```

- **Nationality Labels**: Localize UI labels
  ```python
  _("Nationality")  # "Nationalité" in French
  _("Birth Country")  # "Pays de naissance" in French
  ```

### Data Quality

- **Missing Data**: Handle players with missing birthplace information
- **Validation**: Validate country codes against known NHL countries
- **Default Values**: Use "Unknown" for missing nationality data

### Security

- **Input Validation**: Validate country_code parameter in web routes
- **SQL Injection**: N/A (no database queries)
- **XSS**: Escape country names in templates (automatic with Jinja2)

### Breaking Changes

**None** - This is an additive change. Existing functionality remains unchanged.

**Migration**: No database migration needed (data fetched from API).

### Future Enhancements

1. **Flag Icons**: Add country flag emojis/icons to nationality listings
2. **Nationality Comparisons**: Compare countries head-to-head
3. **Historical Data**: Track nationality standings over time
4. **Birth Province/State**: Add province/state level grouping for CAN/USA
5. **City-Level Grouping**: Group by birth city for detailed analysis

## Implementation Notes

*To be filled during implementation:*

- Actual NHL API response structure for birthplace data
- Performance impact of additional data fields
- Challenges encountered during implementation
- Deviations from proposed solution
- Actual effort vs estimated
