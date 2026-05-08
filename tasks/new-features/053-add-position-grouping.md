# Add Player Position as Grouping Category

**GitHub Issue**: [#552](https://github.com/bdperkin/nhl-scrabble/issues/552)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

8-12 hours

## Description

Add player position as a grouping category for listing, filtering, and analysis across all interface types (analyze, dashboard, interactive, search, WebUI). This enhancement will allow users to:

- View player rankings grouped by position (Center, Left Wing, Right Wing, Defense, Goalie)
- Filter players by specific positions
- Compare Scrabble scores across different positions
- Generate position-specific reports and standings
- Analyze positional strength of teams

Currently, the system groups players by team, division, and conference. Adding position as a fourth grouping dimension provides valuable insights into positional contributions and allows comparison of players within the same role.

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

The NHL API provides position information in two ways:
1. **Top-level grouping**: `forwards`, `defensemen`, `goalies`
2. **Position code**: Each player has a `positionCode` field

```json
{
  "forwards": [
    {
      "firstName": {"default": "Connor"},
      "lastName": {"default": "McDavid"},
      "positionCode": "C",  // Center
      "shootsCatches": "L"
    }
  ],
  "defensemen": [
    {
      "firstName": {"default": "Cale"},
      "lastName": {"default": "Makar"},
      "positionCode": "D",  // Defense
      "shootsCatches": "R"
    }
  ],
  "goalies": [
    {
      "firstName": {"default": "Connor"},
      "lastName": {"default": "Hellebuyck"},
      "positionCode": "G",  // Goalie
      "shootsCatches": "L"
    }
  ]
}
```

**Position Codes**:
- **C**: Center
- **L**: Left Wing
- **R**: Right Wing
- **D**: Defense (Defenseman)
- **G**: Goalie

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
    position_code: str  # NEW: Single-letter code (C, L, R, D, G)
    position: str  # NEW: Full position name (Center, Left Wing, Defense, Goalie)
    position_type: str  # NEW: Position category (Forward, Defense, Goalie)
```

**Add Position Mapping** (`src/nhl_scrabble/utils/positions.py` - new file):
```python
"""Position code to full name mapping."""

POSITION_CODES = {
    "C": "Center",
    "L": "Left Wing",
    "R": "Right Wing",
    "D": "Defense",
    "G": "Goalie",
}

POSITION_TYPES = {
    "C": "Forward",
    "L": "Forward",
    "R": "Forward",
    "D": "Defense",
    "G": "Goalie",
}

def get_position_name(position_code: str) -> str:
    """Convert position code to full name.

    Args:
        position_code: Single-letter position code (C, L, R, D, G)

    Returns:
        Full position name

    Examples:
        >>> get_position_name("C")
        'Center'
        >>> get_position_name("G")
        'Goalie'
    """
    return POSITION_CODES.get(position_code.upper(), position_code)


def get_position_type(position_code: str) -> str:
    """Convert position code to position type.

    Args:
        position_code: Single-letter position code (C, L, R, D, G)

    Returns:
        Position type (Forward, Defense, Goalie)

    Examples:
        >>> get_position_type("C")
        'Forward'
        >>> get_position_type("D")
        'Defense'
    """
    return POSITION_TYPES.get(position_code.upper(), "Unknown")
```

### 2. Processor Updates

**Update TeamProcessor** (`src/nhl_scrabble/processors/team_processor.py`):
```python
from nhl_scrabble.utils.positions import get_position_name, get_position_type

def process_team_data(self, team_data: dict[str, Any]) -> list[PlayerScore]:
    """Process team roster with position information."""
    players = []

    # Map position category to position type
    position_type_map = {
        "forwards": "Forward",
        "defensemen": "Defense",
        "goalies": "Goalie",
    }

    for position_category in ("forwards", "defensemen", "goalies"):
        for player in team_data.get(position_category, []):
            # Extract position data
            position_code = player.get("positionCode", "")
            position_name = get_position_name(position_code)
            position_type = position_type_map.get(position_category, "Unknown")

            # Create PlayerScore with position
            player_score = PlayerScore(
                # ... existing fields
                position_code=position_code,
                position=position_name,
                position_type=position_type,
            )
            players.append(player_score)

    return players
```

### 3. Grouping and Filtering

**Add Position Grouping** (`src/nhl_scrabble/processors/grouping.py`):
```python
"""Player grouping utilities."""

from collections import defaultdict

from nhl_scrabble.models.player import PlayerScore


def group_by_position(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by specific position.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping position name to list of players

    Examples:
        >>> grouped = group_by_position(players)
        >>> grouped.keys()
        dict_keys(['Center', 'Left Wing', 'Right Wing', 'Defense', 'Goalie'])
    """
    grouped = defaultdict(list)
    for player in players:
        grouped[player.position].append(player)
    return dict(grouped)


def group_by_position_type(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by position type (Forward, Defense, Goalie).

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping position type to list of players

    Examples:
        >>> grouped = group_by_position_type(players)
        >>> grouped.keys()
        dict_keys(['Forward', 'Defense', 'Goalie'])
    """
    grouped = defaultdict(list)
    for player in players:
        grouped[player.position_type].append(player)
    return dict(grouped)


def group_by_position_code(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by position code (C, L, R, D, G).

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping position code to list of players
    """
    grouped = defaultdict(list)
    for player in players:
        grouped[player.position_code].append(player)
    return dict(grouped)
```

### 4. CLI Updates

**Add Position Options** (`src/nhl_scrabble/cli.py`):
```python
@click.option(
    "--group-by",
    type=click.Choice(["team", "division", "conference", "position", "position-type"]),
    default="team",
    help="Group players by team, division, conference, position, or position-type",
)
@click.option(
    "--filter-position",
    type=click.Choice(["C", "L", "R", "D", "G", "Forward", "Defense", "Goalie"]),
    default=None,
    help="Filter players by position code or type",
)
def analyze(
    top_players: int,
    top_team_players: int,
    use_cache: bool,
    group_by: str,
    filter_position: str | None,
) -> None:
    """Analyze NHL player Scrabble scores."""
    # Apply grouping and filtering
```

### 5. Web Interface Updates

**Add Position Pages** (`src/nhl_scrabble/web/app.py`):
```python
@app.get("/positions", response_class=HTMLResponse)
async def positions_page(request: Request) -> HTMLResponse:
    """Position standings page - all positions ranked by total/average score."""
    # Group by position, calculate totals and averages, sort by score

@app.get("/positions/{position_type}", response_class=HTMLResponse)
async def position_type_page(
    request: Request,
    position_type: str,  # Forward, Defense, Goalie
) -> HTMLResponse:
    """Position type page - all players in a position category."""
    # Filter by position type, show all players with rankings

@app.get("/positions/detail/{position_code}", response_class=HTMLResponse)
async def position_detail_page(
    request: Request,
    position_code: str,  # C, L, R, D, G
) -> HTMLResponse:
    """Position detail page - all players at a specific position."""
    # Filter by position code, show all players with rankings
```

**Add Menu Item** (`src/nhl_scrabble/web/templates/base.html`):
```html
<nav>
  <a href="/">Home</a>
  <a href="/teams">Teams</a>
  <a href="/divisions">Divisions</a>
  <a href="/conferences">Conferences</a>
  <a href="/positions">Positions</a>  <!-- NEW -->
  <a href="/playoffs">Playoffs</a>
  <a href="/stats">Stats</a>
</nav>
```

### 6. Report Updates

**Add Position Report** (`src/nhl_scrabble/reports/position_report.py` - new file):
```python
"""Position-based Scrabble score report."""

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.processors.grouping import group_by_position, group_by_position_type
from nhl_scrabble.reports.base import BaseReport


class PositionReport(BaseReport):
    """Generate position standings report."""

    def generate(self, players: list[PlayerScore]) -> str:
        """Generate position standings with player counts and scores."""
        grouped = group_by_position(players)

        # Calculate standings by specific position
        standings = []
        for position, position_players in grouped.items():
            total_score = sum(p.full_score for p in position_players)
            avg_score = total_score / len(position_players)
            standings.append({
                "position": position,
                "players": len(position_players),
                "total_score": total_score,
                "average_score": avg_score,
                "top_player": max(position_players, key=lambda p: p.full_score),
            })

        # Sort by average score (position quality metric)
        standings.sort(key=lambda x: x["average_score"], reverse=True)

        return self._format_standings(standings)


class PositionTypeReport(BaseReport):
    """Generate position type (Forward/Defense/Goalie) standings report."""

    def generate(self, players: list[PlayerScore]) -> str:
        """Generate position type standings."""
        grouped = group_by_position_type(players)

        standings = []
        for pos_type, type_players in grouped.items():
            total_score = sum(p.full_score for p in type_players)
            avg_score = total_score / len(type_players)
            standings.append({
                "position_type": pos_type,
                "players": len(type_players),
                "total_score": total_score,
                "average_score": avg_score,
            })

        standings.sort(key=lambda x: x["total_score"], reverse=True)

        return self._format_standings(standings)
```

## Implementation Steps

1. **Add Position Utilities** (1-2h)
   - Create `src/nhl_scrabble/utils/positions.py`
   - Implement position code mapping functions
   - Add position type mapping
   - Add validation for position codes

2. **Update Data Models** (1-2h)
   - Add position_code, position, position_type to PlayerScore
   - Update to_dict() method
   - Update serialization/deserialization
   - Update type hints

3. **Update Processors** (2-3h)
   - Extract position data from NHL API response
   - Map position codes to full names
   - Determine position type from API grouping
   - Handle missing/invalid position data

4. **Implement Grouping Functions** (1-2h)
   - Create group_by_position() function
   - Create group_by_position_type() function
   - Create group_by_position_code() function
   - Add filtering by position

5. **Update CLI Interface** (1-2h)
   - Add --group-by position option
   - Add --group-by position-type option
   - Add --filter-position option
   - Update help text and examples

6. **Update Web Interface** (2-3h)
   - Create /positions page (position overview)
   - Create /positions/{type} pages (Forward/Defense/Goalie)
   - Create /positions/detail/{code} pages (C/L/R/D/G)
   - Add Positions menu item
   - Update templates with i18n support

7. **Add Reports** (1-2h)
   - Create PositionReport class
   - Create PositionTypeReport class
   - Add position filtering to existing reports
   - Support JSON export

8. **Testing** (2-3h)
   - Unit tests for position mapping utilities
   - Unit tests for grouping functions
   - Integration tests for position data extraction
   - Web interface tests for position pages
   - CLI tests for position options

9. **Documentation** (1h)
   - Update README with position features
   - Add API documentation
   - Update CLI help text
   - Add examples to user guide

## Testing Strategy

### Unit Tests

**Test Position Mapping** (`tests/unit/utils/test_positions.py`):
```python
def test_position_code_mapping():
    """Test position code to name conversion."""
    assert get_position_name("C") == "Center"
    assert get_position_name("L") == "Left Wing"
    assert get_position_name("R") == "Right Wing"
    assert get_position_name("D") == "Defense"
    assert get_position_name("G") == "Goalie"

def test_position_type_mapping():
    """Test position code to type conversion."""
    assert get_position_type("C") == "Forward"
    assert get_position_type("L") == "Forward"
    assert get_position_type("R") == "Forward"
    assert get_position_type("D") == "Defense"
    assert get_position_type("G") == "Goalie"

def test_case_insensitive_position():
    """Test position mapping is case-insensitive."""
    assert get_position_name("c") == "Center"
    assert get_position_name("C") == "Center"

def test_unknown_position_code():
    """Test handling of unknown position codes."""
    assert get_position_name("X") == "X"  # Returns code if unknown
```

**Test Grouping Functions** (`tests/unit/processors/test_grouping.py`):
```python
def test_group_by_position():
    """Test grouping players by specific position."""
    players = [
        PlayerScore(..., position="Center", position_code="C"),
        PlayerScore(..., position="Center", position_code="C"),
        PlayerScore(..., position="Defense", position_code="D"),
    ]

    grouped = group_by_position(players)
    assert len(grouped["Center"]) == 2
    assert len(grouped["Defense"]) == 1

def test_group_by_position_type():
    """Test grouping by position type."""
    players = [
        PlayerScore(..., position_type="Forward"),
        PlayerScore(..., position_type="Forward"),
        PlayerScore(..., position_type="Defense"),
        PlayerScore(..., position_type="Goalie"),
    ]

    grouped = group_by_position_type(players)
    assert len(grouped["Forward"]) == 2
    assert len(grouped["Defense"]) == 1
    assert len(grouped["Goalie"]) == 1
```

### Integration Tests

**Test Position Data Extraction** (`tests/integration/test_position_processing.py`):
```python
def test_team_processor_extracts_position():
    """Test that team processor extracts position data."""
    # Mock roster data with position codes
    roster_data = {
        "forwards": [
            {
                "firstName": {"default": "Connor"},
                "lastName": {"default": "McDavid"},
                "positionCode": "C",
            }
        ]
    }

    processor = TeamProcessor()
    players = processor.process_team_data(roster_data)

    assert players[0].position_code == "C"
    assert players[0].position == "Center"
    assert players[0].position_type == "Forward"
```

**Test Web Position Pages** (`tests/integration/test_web_positions.py`):
```python
def test_positions_page_exists(client: TestClient):
    """Test positions overview page."""
    response = client.get("/positions")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_position_type_page(client: TestClient):
    """Test position type page (Forward/Defense/Goalie)."""
    response = client.get("/positions/Forward")
    assert response.status_code == 200
    assert "Forward" in response.text

def test_position_detail_page(client: TestClient):
    """Test specific position detail page."""
    response = client.get("/positions/detail/C")
    assert response.status_code == 200
    assert "Center" in response.text
```

### Functional Tests (Playwright)

**Test Position Navigation** (`qa/web/tests/functional/test_position_pages.py`):
```python
@pytest.mark.parametrize("position_type", ["Forward", "Defense", "Goalie"])
def test_position_type_pages_load(page, position_type):
    """Test position type pages load correctly."""
    page.goto(f"/positions/{position_type}")
    expect(page.locator("h1")).to_be_visible()

@pytest.mark.parametrize("position_code", ["C", "L", "R", "D", "G"])
def test_position_detail_pages_load(page, position_code):
    """Test position detail pages load correctly."""
    page.goto(f"/positions/detail/{position_code}")
    expect(page.locator("h1")).to_be_visible()
```

### Manual Testing

1. Run CLI with position grouping:
   ```bash
   nhl-scrabble analyze --group-by position
   nhl-scrabble analyze --group-by position-type
   nhl-scrabble analyze --filter-position C
   nhl-scrabble analyze --filter-position Forward
   ```

2. Test web interface:
   - Navigate to /positions
   - Verify all positions listed with stats
   - Click on "Forward"
   - Verify all forwards shown
   - Click on specific position (e.g., Center)
   - Verify only centers shown
   - Check player count and score calculations

3. Test i18n:
   - Switch to French Canadian locale
   - Verify position names translated
   - Verify UI labels localized

## Acceptance Criteria

- [ ] PlayerScore model includes position_code, position, and position_type fields
- [ ] Position mapping utility created with all NHL positions
- [ ] Position data extracted from NHL API roster response
- [ ] Players can be grouped by position in all interfaces
- [ ] Players can be grouped by position type (Forward/Defense/Goalie)
- [ ] Players can be filtered by position code or type
- [ ] CLI supports `--group-by position` and `--group-by position-type` options
- [ ] CLI supports `--filter-position` option
- [ ] Web interface includes /positions page with overview
- [ ] Web interface includes /positions/{type} pages (Forward/Defense/Goalie)
- [ ] Web interface includes /positions/detail/{code} pages (C/L/R/D/G)
- [ ] Positions menu item added to web navigation
- [ ] PositionReport and PositionTypeReport classes implemented
- [ ] All grouping functions have unit tests
- [ ] Web position pages have integration tests
- [ ] Functional tests cover position navigation
- [ ] Documentation updated with position features
- [ ] All tests pass (unit, integration, functional)
- [ ] Type checking passes (mypy)
- [ ] Pre-commit hooks pass
- [ ] i18n support for position names

## Related Files

- `src/nhl_scrabble/models/player.py` - PlayerScore model updates
- `src/nhl_scrabble/utils/positions.py` - NEW: Position mapping utilities
- `src/nhl_scrabble/processors/team_processor.py` - Extract position data
- `src/nhl_scrabble/processors/grouping.py` - Position grouping functions
- `src/nhl_scrabble/reports/position_report.py` - NEW: Position reports
- `src/nhl_scrabble/cli.py` - CLI position options
- `src/nhl_scrabble/web/app.py` - Web position routes
- `src/nhl_scrabble/web/templates/positions.html` - NEW: Position overview page
- `src/nhl_scrabble/web/templates/position_type.html` - NEW: Position type page
- `src/nhl_scrabble/web/templates/position_detail.html` - NEW: Position detail page
- `src/nhl_scrabble/web/templates/base.html` - Navigation menu update
- `tests/unit/utils/test_positions.py` - NEW: Position mapping tests
- `tests/unit/processors/test_grouping.py` - Position grouping tests
- `tests/integration/test_position_processing.py` - NEW: Position extraction tests
- `tests/integration/test_web_positions.py` - NEW: Web position tests
- `qa/web/tests/functional/test_position_pages.py` - NEW: Functional tests

## Dependencies

**None** - This is a standalone feature addition.

**Synergy with Other Tasks**:
- Can be combined with task 052 (nationality grouping) for multi-dimensional analysis
- Complements player detail pages (task 051) with position-specific views

**Optional Enhancements** (future tasks):
- Position-specific analytics (e.g., highest-scoring position)
- Position comparison tools
- Team positional strength analysis
- Historical position statistics

## Additional Notes

### Performance Considerations

- **No Additional API Calls**: Position data is already in roster response
- **Efficient Grouping**: Use defaultdict for O(n) grouping performance
- **Caching**: Position groupings should be cached with roster data

### I18n Considerations

- **Position Names**: Add translations for all position names
  ```python
  # In locale files
  msgid "Center"
  msgstr "Center"  # en_US
  msgstr "Centre"  # fr_CA
  msgstr "Center"  # sv_SE

  msgid "Left Wing"
  msgstr "Left Wing"  # en_US
  msgstr "Ailier gauche"  # fr_CA
  msgstr "Vänsterforward"  # sv_SE

  msgid "Defense"
  msgstr "Defense"  # en_US
  msgstr "Défense"  # fr_CA
  msgstr "Försvar"  # sv_SE
  ```

- **Position Labels**: Localize UI labels
  ```python
  _("Position")  # "Position" in English, "Position" in French
  _("Forward")  # "Forward" / "Attaquant"
  _("Goalie")  # "Goalie" / "Gardien"
  ```

### Data Quality

- **Missing Position Codes**: Handle players with missing position data
- **Validation**: Validate position codes against known NHL positions
- **Default Values**: Use "Unknown" for missing position data

### Security

- **Input Validation**: Validate position_code and position_type parameters in web routes
- **SQL Injection**: N/A (no database queries)
- **XSS**: Escape position names in templates (automatic with Jinja2)

### Breaking Changes

**None** - This is an additive change. Existing functionality remains unchanged.

**Migration**: No database migration needed (data extracted from API).

### Analytics Opportunities

1. **Position Strength Analysis**: Which position has highest average Scrabble score?
2. **Team Positional Balance**: Compare team strength across positions
3. **Position Depth**: Analyze team depth at each position
4. **Cross-Position Comparison**: Compare top scorers across different positions

### Future Enhancements

1. **Position-Specific Filters**: Add more granular filtering (e.g., all left-shooting centers)
2. **Handedness Integration**: Combine with shootsCatches data for detailed analysis
3. **Position Tiers**: Create position tiers (1st line, 2nd line, etc.) based on ice time
4. **Advanced Stats**: Integrate with position-specific NHL statistics

## Implementation Notes

*To be filled during implementation:*

- Actual position codes found in NHL API data
- Performance impact of additional grouping dimensions
- Challenges encountered during implementation
- Deviations from proposed solution
- Actual effort vs estimated
