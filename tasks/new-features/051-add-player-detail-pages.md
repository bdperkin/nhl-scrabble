# Add Player Detail Pages with Comprehensive Player Information

**GitHub Issue**: #544 - https://github.com/bdperkin/nhl-scrabble/issues/544

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

6-8 hours

## Description

Add dynamic player detail pages accessible via `/players/{PLAYER_ID}` URL paths. Each page will display comprehensive player information including personal details (name, photo, birthplace with national flag), team affiliation (team name, logo, division, conference), and hockey statistics (player number, position, Scrabble score). This extends the hierarchical navigation to the individual player level.

## Current State

**Players Page** (`/players`):
- Shows top 50+ players ranked by Scrabble score
- Displays: Rank, Player Name, Team, Division, Conference, Score
- No links to individual player detail pages
- No player photos or detailed information

**Data Available**:
- `PlayerScore` model: Basic player info (first name, last name, team, division, conference, scores)
- Missing data: player ID, photo URL, birthplace, nationality, player number, position
- NHL API roster endpoint provides: position, jersey number
- NHL API player endpoint (`/v1/player/{playerId}/landing`) provides: full player profile

**Existing Detail Pages**:
- Task #048: Conference detail pages
- Task #049: Division detail pages
- Task #050: Team detail pages
- Same pattern can be applied to players

## Proposed Solution

### Step 1: Enhance Player Data Model

Add extended player information to support detail pages:

```python
@dataclass(slots=True)
class PlayerDetail:
    """Extended player information for detail pages.

    Attributes:
        player_id: NHL player ID (e.g., 8478402 for Connor McDavid)
        first_name: Player's first name
        last_name: Player's last name
        full_name: Player's full name
        photo_url: URL to player headshot
        birthplace: City, Province/State, Country
        birth_country: Country code (e.g., 'CAN', 'USA', 'SWE')
        team_abbrev: Team abbreviation
        team_name: Team full name
        division: Division name
        conference: Conference name
        position: Player position (C, LW, RW, D, G)
        jersey_number: Player jersey number
        scrabble_scores: PlayerScore object with scoring details
    """
    player_id: int
    first_name: str
    last_name: str
    full_name: str
    photo_url: str
    birthplace: str
    birth_country: str
    team_abbrev: str
    team_name: str
    division: str
    conference: str
    position: str
    jersey_number: int
    scrabble_scores: PlayerScore
```

### Step 2: Add NHL API Player Detail Method

Add method to `NHLApiClient` to fetch player details:

```python
def get_player_details(self, player_id: int) -> dict[str, Any]:
    """Fetch detailed player information from NHL API.

    Args:
        player_id: NHL player ID (numeric)

    Returns:
        Player detail data including photo, birthplace, position, etc.

    Raises:
        NHLApiNotFoundError: If player not found
        NHLApiError: If API request fails
    """
    url = f"{self.base_url}/player/{player_id}/landing"

    try:
        response = self._make_request(url)
        data = response.json()

        # Validate response structure
        validate_api_response_structure(data, expected_keys=["playerId", "firstName", "lastName"])

        return data
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            raise NHLApiNotFoundError(f"Player {player_id} not found") from exc
        raise NHLApiError(f"Failed to fetch player {player_id}: {exc}") from exc
```

### Step 3: Add Dynamic Player Route

Add a new `/players/{player_id}` route in `app.py`:

```python
@app.get("/players/{player_id}", response_class=HTMLResponse)
async def player_detail_page(
    request: Request,
    player_id: int,
) -> HTMLResponse:
    """Serve a player detail page with comprehensive information.

    Args:
        request: FastAPI request object
        player_id: NHL player ID (numeric)

    Returns:
        Rendered player_detail.html template with player data

    Raises:
        HTTPException: If player not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data to get all players
        analysis_request = AnalysisRequest(top_players=500, use_cache=True)
        data = await analyze_post(analysis_request)

        # Find the player in top_players list
        player_data = None
        for player in data["top_players"]:
            # We need to match by name since current data doesn't have player_id
            # This will need enhancement once player_id is added to the model
            if str(player_id) in [str(p.get("id", "")) for p in data["top_players"]]:
                player_data = player
                break

        if player_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Player {player_id} not found",
            )

        # Fetch extended player details from NHL API
        nhl_client = NHLApiClient()
        try:
            nhl_data = nhl_client.get_player_details(player_id)
        finally:
            nhl_client.close()

        # Extract player information
        player_info = {
            "player_id": player_id,
            "full_name": player_data["name"],
            "first_name": player_data["first_name"],
            "last_name": player_data["last_name"],
            "photo_url": nhl_data.get("headshot", ""),
            "birthplace": f"{nhl_data.get('birthCity', {}).get('default', '')}, {nhl_data.get('birthStateProvince', {}).get('default', '')}, {nhl_data.get('birthCountry', '')}",
            "birth_country": nhl_data.get("birthCountry", ""),
            "team_abbrev": player_data["team"],
            "team_name": player_data.get("team_name", ""),
            "division": player_data["division"],
            "conference": player_data["conference"],
            "position": nhl_data.get("position", ""),
            "jersey_number": nhl_data.get("sweaterNumber", 0),
            "scrabble_score": player_data["score"],
            "first_score": player_data["first_score"],
            "last_score": player_data["last_score"],
            "team_logo_url": f"https://assets.nhle.com/logos/nhl/svg/{player_data['team']}_light.svg",
            "country_flag_url": f"https://flagcdn.com/w320/{nhl_data.get('birthCountry', '').lower()}.png",
        }

        # Get locale for i18n
        locale = get_request_locale(request)

        # Load translations
        try:
            translation = gettext.translation(
                "messages",
                localedir=str(LOCALES_DIR),
                languages=[locale],
            )
            templates.env.install_gettext_translations(translation, newstyle=True)  # type: ignore[attr-defined]
        except FileNotFoundError:
            logger.warning(f"Translation not found for locale: {locale}, using default")

        return templates.TemplateResponse(
            "player_detail.html",
            {
                "request": request,
                "player": player_info,
                "current_locale": locale,
            },
        )

    except NHLApiError as exc:
        logger.exception("NHL API error during player detail page generation")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error generating player detail page")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
```

### Step 4: Create Player Detail Template

Create `src/nhl_scrabble/web/templates/player_detail.html`:

```jinja2
{% extends "base.html" %}

{% block title %}{% trans player_name=player.full_name %}{{ player_name }} - Player Profile{% endtrans %}{% endblock %}

{% block content %}
    <!-- Player Profile Header -->
    <div class="player-header fade-on-scroll">
        <div class="player-photo-container">
            <img
                src="{{ player.photo_url }}"
                alt="{{ player.full_name }} photo"
                class="player-photo"
                loading="lazy"
                onerror="this.src='/static/img/placeholder-player.png'"
            />
        </div>
        <div class="player-info-container">
            <h2>{{ player.full_name }}</h2>
            <div class="player-number-position">
                <span class="jersey-number">#{{ player.jersey_number }}</span>
                <span class="position-badge">{{ player.position }}</span>
            </div>
            <div class="player-birthplace">
                <img
                    src="{{ player.country_flag_url }}"
                    alt="{{ player.birth_country }} flag"
                    class="country-flag"
                    loading="lazy"
                    onerror="this.style.display='none'"
                />
                <span>{{ player.birthplace }}</span>
            </div>
        </div>
    </div>

    <!-- Team Affiliation -->
    <div class="team-affiliation fade-on-scroll">
        <img
            src="{{ player.team_logo_url }}"
            alt="{{ player.team_name }} logo"
            class="team-logo-small"
            loading="lazy"
            onerror="this.style.display='none'"
        />
        <div class="team-info">
            <h3><a href="/teams/{{ player.team_abbrev }}">{{ player.team_name }}</a></h3>
            <p class="team-meta">
                <a href="/divisions/{{ player.division }}">{{ player.division }}</a> /
                <a href="/conferences/{{ player.conference }}">{{ player.conference }}</a>
            </p>
        </div>
    </div>

    <!-- Scrabble Score Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Total Score{% endtrans %}</h4>
            <p class="stat-value">{{ player.scrabble_score }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}First Name Score{% endtrans %}</h4>
            <p class="stat-value">{{ player.first_score }}</p>
            <p class="stat-detail">{{ player.first_name }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Last Name Score{% endtrans %}</h4>
            <p class="stat-value">{{ player.last_score }}</p>
            <p class="stat-detail">{{ player.last_name }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Position{% endtrans %}</h4>
            <p class="stat-value">{{ player.position }}</p>
        </div>
    </div>

    <!-- Navigation Links -->
    <div class="player-navigation fade-on-scroll">
        <a href="/players" class="btn btn-secondary">
            ← {% trans %}Back to All Players{% endtrans %}
        </a>
        <a href="/teams/{{ player.team_abbrev }}" class="btn btn-secondary">
            {% trans %}View Team Roster{% endtrans %} →
        </a>
    </div>
{% endblock %}
```

### Step 5: Add CSS for Player Profile

Add to `src/nhl_scrabble/web/static/css/styles.css`:

```css
/* Player Detail Page - Profile Header */
.player-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin: 2rem 0;
    padding: 2rem;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-md);
}

.player-photo-container {
    flex-shrink: 0;
}

.player-photo {
    width: 200px;
    height: 200px;
    object-fit: cover;
    border-radius: 50%;
    border: 4px solid var(--primary-color);
}

.player-info-container h2 {
    margin: 0 0 1rem 0;
    color: var(--text-primary);
}

.player-number-position {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1rem;
}

.jersey-number {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color);
}

.position-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: var(--primary-color);
    color: white;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: bold;
}

.player-birthplace {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
}

.country-flag {
    width: 32px;
    height: 24px;
    object-fit: cover;
    border: 1px solid var(--border-color);
    border-radius: 2px;
}

/* Team Affiliation Section */
.team-affiliation {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
}

.team-logo-small {
    width: 80px;
    height: 80px;
    object-fit: contain;
    flex-shrink: 0;
}

.team-info h3 {
    margin: 0 0 0.5rem 0;
}

.team-info h3 a {
    color: var(--text-primary);
    text-decoration: none;
}

.team-info h3 a:hover {
    color: var(--primary-color);
}

/* Player Navigation */
.player-navigation {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin: 2rem 0;
}

/* Responsive */
@media (max-width: 768px) {
    .player-header {
        flex-direction: column;
        text-align: center;
    }

    .player-photo {
        width: 150px;
        height: 150px;
    }

    .player-number-position {
        justify-content: center;
    }

    .player-navigation {
        flex-direction: column;
    }
}
```

### Step 6: Update Players Page with Links

Modify `src/nhl_scrabble/web/templates/players.html` to link player names to detail pages:

**Challenge**: Current implementation doesn't have player IDs. Need to either:

**Option A** (Recommended): Add player ID to PlayerScore model and fetch from NHL API
**Option B** (Temporary): Use URL-safe player name slugs (e.g., `/players/connor-mcdavid`)

For now, document that this task depends on adding player IDs to the data model.

### Step 7: Update CSP Headers for External Resources

Modify `app.py` CSP headers to allow player photos and country flags:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://assets.nhle.com https://flagcdn.com; "  # Added flagcdn.com
    "font-src 'self'; "
    "connect-src 'self'"
)
```

## Implementation Steps

1. Research NHL API player endpoint structure and available data
2. Add `PlayerDetail` model to `src/nhl_scrabble/models/player.py`
3. Add `get_player_details()` method to `src/nhl_scrabble/api/nhl_client.py`
4. Enhance `PlayerScore` model to include `player_id` field
5. Update team roster fetching to capture player IDs
6. Add `/players/{player_id}` route in `src/nhl_scrabble/web/app.py`
7. Create `src/nhl_scrabble/web/templates/player_detail.html` template
8. Add player profile CSS styles to `src/nhl_scrabble/web/static/css/styles.css`
9. Update CSP headers in `app.py` to allow `https://flagcdn.com`
10. Modify `players.html` template to link player names to detail pages
11. Extract i18n strings and update translation files
12. Add QA tests for player detail pages
13. Test photo/flag fallback behavior
14. Test responsive layout on mobile devices
15. Update documentation

## Testing Strategy

### Unit Tests

**File**: `tests/unit/web/test_player_detail_routes.py`

```python
"""Tests for player detail page routes."""

import pytest
from fastapi.testclient import TestClient


def test_player_detail_page_loads(test_client: TestClient) -> None:
    """Test that player detail page loads successfully."""
    response = test_client.get("/players/8478402")  # Connor McDavid
    assert response.status_code == 200
    assert b"Connor McDavid" in response.content


def test_player_detail_page_shows_photo(test_client: TestClient) -> None:
    """Test that player photo is displayed."""
    response = test_client.get("/players/8478402")
    assert b"player-photo" in response.content


def test_player_detail_page_invalid_player(test_client: TestClient) -> None:
    """Test 404 for non-existent player."""
    response = test_client.get("/players/9999999")
    assert response.status_code == 404


def test_player_detail_page_shows_team_logo(test_client: TestClient) -> None:
    """Test that team logo is displayed."""
    response = test_client.get("/players/8478402")
    assert b"team-logo" in response.content


def test_player_detail_page_shows_country_flag(test_client: TestClient) -> None:
    """Test that country flag is displayed."""
    response = test_client.get("/players/8478402")
    assert b"flagcdn.com" in response.content
```

### Integration Tests

**File**: `tests/integration/api/test_nhl_client_player_details.py`

```python
"""Integration tests for NHL API player details."""

import pytest
from nhl_scrabble.api import NHLApiClient
from nhl_scrabble.exceptions import NHLApiNotFoundError


def test_get_player_details_success() -> None:
    """Test fetching player details from NHL API."""
    client = NHLApiClient()
    try:
        data = client.get_player_details(8478402)  # Connor McDavid
        assert "playerId" in data
        assert "firstName" in data
        assert "lastName" in data
        assert data["playerId"] == 8478402
    finally:
        client.close()


def test_get_player_details_not_found() -> None:
    """Test 404 for non-existent player."""
    client = NHLApiClient()
    try:
        with pytest.raises(NHLApiNotFoundError):
            client.get_player_details(9999999)
    finally:
        client.close()
```

### QA Web Tests

**File**: `qa/web/tests/functional/test_player_detail.py`

```python
"""Functional tests for player detail pages."""

import pytest
from playwright.sync_api import Page, expect


def test_player_detail_page_loads(page: Page, base_url: str) -> None:
    """Test player detail page loads correctly."""
    page.goto(f"{base_url}/players/8478402")

    # Check page title
    expect(page).to_have_title(re.compile("Connor McDavid"))

    # Check player photo is visible
    photo = page.locator(".player-photo")
    expect(photo).to_be_visible()

    # Check stats cards
    expect(page.locator(".stats-summary")).to_be_visible()


def test_player_detail_navigation(page: Page, base_url: str) -> None:
    """Test navigation links on player page."""
    page.goto(f"{base_url}/players/8478402")

    # Click team link
    team_link = page.get_by_role("link", name=re.compile("Oilers"))
    expect(team_link).to_be_visible()

    # Should link to team detail page
    assert "/teams/EDM" in team_link.get_attribute("href")
```

### Manual Testing

1. **Player Photo Display**:
   - Navigate to `/players/8478402` (Connor McDavid)
   - Verify player headshot displays
   - Test photo fallback with invalid player

2. **Country Flag Display**:
   - Verify Canadian flag shows for Canadian players
   - Test with Swedish, Russian, American players
   - Verify flag fallback behavior

3. **Team Logo Display**:
   - Verify team logo appears in affiliation section
   - Click team logo → navigates to team detail page

4. **Navigation**:
   - From players page, click player name → player detail
   - From player detail, click team → team detail
   - From player detail, click division → division detail
   - From player detail, click conference → conference detail

5. **Responsive Design**:
   - Test on mobile (photo should be smaller, centered)
   - Test on tablet (layout should adapt)
   - Test on desktop (full layout)

## Acceptance Criteria

- [ ] `/players/{player_id}` route added and functional
- [ ] Player detail page displays NHL player photo
- [ ] Player birthplace shown with country flag
- [ ] Team logo displayed with link to team detail page
- [ ] Division and conference links work (breadcrumb navigation)
- [ ] Player number and position displayed
- [ ] Scrabble score statistics shown (total, first name, last name)
- [ ] CSP headers updated to allow `https://flagcdn.com`
- [ ] Photo/flag fallback behavior works (placeholder or hide)
- [ ] Players page links to individual player detail pages
- [ ] `PlayerScore` model includes `player_id` field
- [ ] `NHLApiClient.get_player_details()` method added
- [ ] I18n support for all UI text
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] QA web tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/models/player.py` - Add PlayerDetail model, enhance PlayerScore
- `src/nhl_scrabble/api/nhl_client.py` - Add get_player_details() method
- `src/nhl_scrabble/web/app.py` - Add player detail route
- `src/nhl_scrabble/web/templates/player_detail.html` - New template (create)
- `src/nhl_scrabble/web/templates/players.html` - Update with links
- `src/nhl_scrabble/web/static/css/styles.css` - Add player profile styles
- `tests/unit/web/test_player_detail_routes.py` - Unit tests (create)
- `tests/integration/api/test_nhl_client_player_details.py` - Integration tests (create)
- `qa/web/tests/functional/test_player_detail.py` - QA tests (create)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - I18n translations

## Dependencies

- FastAPI for routing
- Jinja2 for templating
- NHL API player endpoint (`/v1/player/{playerId}/landing`)
- NHL photo CDN availability
- Flagcdn.com for country flags
- Task #050 (Team detail pages) - provides team logo integration pattern
- **CRITICAL**: Requires adding player IDs to data model (currently missing)

## Additional Notes

### Player ID Challenge

**Current Issue**: The existing `PlayerScore` model and NHL roster data don't include player IDs. This makes it difficult to:
- Link directly to player pages (need unique identifier)
- Fetch additional player details from NHL API

**Solution Options**:

**Option 1** (Recommended): Enhance data collection to include player IDs
- Modify roster fetching to capture `id` field from NHL API
- Add `player_id: int` field to `PlayerScore` model
- Update all existing code to handle player IDs
- Benefits: Proper unique identifiers, can fetch extended data
- Effort: 2-3 hours additional work

**Option 2** (Temporary): Use URL-safe name slugs
- Route: `/players/connor-mcdavid`
- Generate slug from player name
- Look up player by name matching
- Benefits: Works with current data model
- Drawbacks: Names aren't unique (rare collisions possible)
- Effort: 1 hour

**Recommendation**: Implement Option 1 as part of this task to ensure robust player identification.

### NHL API Player Endpoint

The NHL provides a comprehensive player landing page endpoint:

```
GET https://api-web.nhle.com/v1/player/{playerId}/landing
```

**Available Data**:
- `playerId`: Unique player identifier
- `firstName`, `lastName`: Player name
- `headshot`: URL to player photo (e.g., `https://assets.nhle.com/mugs/nhl/{playerId}.png`)
- `birthDate`, `birthCity`, `birthStateProvince`, `birthCountry`: Birth information
- `position`: Player position (C, LW, RW, D, G)
- `sweaterNumber`: Jersey number
- `teamLogo`: Team logo URL
- Plus: height, weight, shoots/catches, draft year, etc.

### Country Flag Resources

**Flagcdn.com** provides free country flag images:

```
https://flagcdn.com/w320/{country_code}.png
```

**Sizes Available**:
- `w20`: 20px width
- `w40`: 40px width
- `w80`: 80px width
- `w160`: 160px width
- `w320`: 320px width (recommended for retina displays)

**Country Codes**: ISO 3166-1 alpha-2 (e.g., 'ca' for Canada, 'us' for USA, 'se' for Sweden)

**Alternative**: Could also use emoji flags (🇨🇦) but image flags provide better cross-platform consistency.

### Photo Fallback Strategy

**Primary**: NHL headshot from assets.nhle.com
**Fallback 1**: Use placeholder silhouette image
**Fallback 2**: Hide image container entirely

Implement with:
```html
<img src="{{ photo_url }}" onerror="this.src='/static/img/placeholder-player.png'" />
```

### Performance Considerations

**Caching**:
- Player detail pages should be cached (1 hour TTL)
- Photos loaded from NHL CDN (fast, reliable)
- Flags loaded from flagcdn.com (lightweight PNGs)

**Lazy Loading**:
- Use `loading="lazy"` for all images
- Improves initial page load time

**CSP Impact**:
- Adding flagcdn.com is safe (trusted source)
- Already allowing assets.nhle.com from task #050

### Future Enhancements

**Season Statistics**:
- Could add hockey stats (goals, assists, points)
- Would require additional NHL API calls
- Out of scope for this task (focus on Scrabble scoring)

**Career History**:
- Previous teams, draft information
- Available in NHL API but not needed for MVP

**Social Media Links**:
- Twitter, Instagram (if available in API)
- Nice-to-have but not essential

**Comparison Tool**:
- Compare two players' Scrabble scores
- Could be a separate task/feature

## Implementation Notes

*To be filled during implementation:*
- Actual approach taken for player ID integration
- Challenges encountered with NHL API
- Deviations from plan
- Actual effort vs estimated
- Player ID field migration strategy
