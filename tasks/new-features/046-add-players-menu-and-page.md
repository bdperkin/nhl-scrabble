# Add Players Menu Item and Dedicated Players Page

**GitHub Issue**: #539 - https://github.com/bdperkin/nhl-scrabble/issues/539

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add a new "Players" navigation menu item between "Home" and "Teams" in the web interface. The new page should display a comprehensive list of top NHL players ranked by Scrabble score, mimicking the design and functionality of the "Top 20 Players by Scrabble Score" section currently shown on the Stats page.

## Current State

**Navigation Structure** (base.html lines 64-97):
- Home (/)
- Teams (/teams)
- Divisions (/divisions)
- Conferences (/conferences)
- Playoffs (/playoffs)
- Stats (/stats)
- API Docs, Documentation, GitHub

**Top Players Display**:
- Stats page (stats.html lines 71-100) shows "Top 10 Players by Scrabble Score"
- Limited to 10 players in display even though API fetches 20
- Embedded within stats page alongside charts and team statistics
- No dedicated page focused solely on player rankings

**FastAPI Route Structure** (app.py):
- `GET /` - Home page (index.html)
- `GET /teams` - Teams standings page
- `GET /divisions` - Divisions standings page
- `GET /conferences` - Conferences standings page
- `GET /playoffs` - Playoff bracket page
- `GET /stats` - Statistics page with charts
- `POST /api/analyze` - API endpoint (returns top_players data)

**Data Available**:
- `/api/analyze` endpoint already fetches player data
- Default `top_players=20` parameter
- Returns player objects with: first_name, last_name, full_name, team, score
- Data includes all NHL players sorted by Scrabble score

## Proposed Solution

### Step 1: Create New Route in app.py

Add a new `/players` route similar to existing pages:

```python
@app.get("/players", response_class=HTMLResponse)
async def players_page(request: Request) -> HTMLResponse:
    """Serve the players ranking page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered players.html template with player rankings

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        # Use higher top_players count for dedicated players page
        analysis_request = AnalysisRequest(top_players=50, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "top_players": data["top_players"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="players.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch players data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
```

**Location**: Insert after `root()` function (around line 458) and before `/teams` route

### Step 2: Create players.html Template

Create `src/nhl_scrabble/web/templates/players.html`:

```html
{% extends "base.html" %}

{% block title %}{% trans %}NHL Scrabble Analyzer - Top Players{% endtrans %}{% endblock %}

{% block og_title %}{% trans %}Top NHL Players by Scrabble Score{% endtrans %}{% endblock %}
{% block twitter_title %}{% trans %}Top NHL Players by Scrabble Score{% endtrans %}{% endblock %}

{% block content %}
    <div class="page-header fade-on-scroll">
        <h2>{% trans %}Top NHL Players by Scrabble Score{% endtrans %}</h2>
        <p class="page-description">
            {% trans %}Ranking of all NHL players based on the Scrabble value of their names. Higher scores indicate names with higher-value letters.{% endtrans %}
        </p>
        <p class="timestamp">
            {% trans %}Data as of{% endtrans %}: {{ timestamp_date }} {{ timestamp_time }}
        </p>
    </div>

    <!-- Summary Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Total Players{% endtrans %}</h4>
            <p class="stat-value">{{ stats.total_players }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Highest Score{% endtrans %}</h4>
            <p class="stat-value">{{ stats.highest_score }}</p>
            <p class="stat-detail">{{ stats.highest_player_name }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Average Score{% endtrans %}</h4>
            <p class="stat-value">{{ stats.avg_score|round(1) }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Lowest Score{% endtrans %}</h4>
            <p class="stat-value">{{ stats.lowest_score }}</p>
        </div>
    </div>

    <!-- Top Players Table -->
    <section class="results-section fade-on-scroll">
        <div class="section-header">
            <h3>{% trans %}Player Rankings{% endtrans %}</h3>
            <div class="export-buttons">
                <button onclick="exportTableToCSV('playersTable', 'nhl-players-scrabble-scores.csv')"
                        class="export-btn"
                        aria-label="{% trans %}Export to CSV{% endtrans %}">
                    📊 {% trans %}Export CSV{% endtrans %}
                </button>
                <button onclick="exportTableToJSON('playersTable', 'nhl-players-scrabble-scores.json')"
                        class="export-btn"
                        aria-label="{% trans %}Export to JSON{% endtrans %}">
                    📋 {% trans %}Export JSON{% endtrans %}
                </button>
            </div>
        </div>

        <div class="table-container">
            <table id="playersTable"
                   class="results-table sortable"
                   role="table"
                   aria-label="{% trans %}Top players by Scrabble score{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="name" data-sort-type="string">{% trans %}Player Name{% endtrans %}</th>
                        <th scope="col" data-sort="team" data-sort-type="string">{% trans %}Team{% endtrans %}</th>
                        <th scope="col" data-sort="score" data-sort-type="number">{% trans %}Score{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in top_players %}
                        <tr data-original-index="{{ loop.index }}">
                            <td data-value="{{ loop.index }}">{{ loop.index }}</td>
                            <td class="player-name" data-value="{{ player.first_name }} {{ player.last_name }}">
                                {{ player.first_name }} {{ player.last_name }}
                            </td>
                            <td class="team-abbrev" data-value="{{ player.team }}">{{ player.team }}</td>
                            <td class="score" data-value="{{ player.score }}">{{ player.score }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="table-info">
            <p>{% trans %}Showing{% endtrans %} {{ top_players|length }} {% trans %}of{% endtrans %} {{ stats.total_players }} {% trans %}total players{% endtrans %}</p>
        </div>
    </section>

    <!-- Scrabble Scoring Legend -->
    <section class="legend-section fade-on-scroll">
        <h3>{% trans %}Scrabble Letter Values{% endtrans %}</h3>
        <div class="letter-values">
            <div class="value-group">
                <span class="value-label">1 {% trans %}point{% endtrans %}:</span>
                <span class="letters">A, E, I, O, U, L, N, S, T, R</span>
            </div>
            <div class="value-group">
                <span class="value-label">2 {% trans %}points{% endtrans %}:</span>
                <span class="letters">D, G</span>
            </div>
            <div class="value-group">
                <span class="value-label">3 {% trans %}points{% endtrans %}:</span>
                <span class="letters">B, C, M, P</span>
            </div>
            <div class="value-group">
                <span class="value-label">4 {% trans %}points{% endtrans %}:</span>
                <span class="letters">F, H, V, W, Y</span>
            </div>
            <div class="value-group">
                <span class="value-label">5 {% trans %}points{% endtrans %}:</span>
                <span class="letters">K</span>
            </div>
            <div class="value-group">
                <span class="value-label">8 {% trans %}points{% endtrans %}:</span>
                <span class="letters">J, X</span>
            </div>
            <div class="value-group">
                <span class="value-label">10 {% trans %}points{% endtrans %}:</span>
                <span class="letters">Q, Z</span>
            </div>
        </div>
    </section>
{% endblock %}
```

### Step 3: Update Navigation in base.html

Modify navigation menu to insert "Players" between "Home" and "Teams":

```html
<!-- Navigation menu -->
<nav id="navMenu" class="main-nav" aria-label="{% trans %}Main navigation{% endtrans %}">
    <ul>
        <li>
            <a href="/?lang={{ locale }}">{% trans %}Home{% endtrans %}</a>
        </li>
        <li>
            <a href="/players?lang={{ locale }}">{% trans %}Players{% endtrans %}</a>
        </li>
        <li>
            <a href="/teams?lang={{ locale }}">{% trans %}Teams{% endtrans %}</a>
        </li>
        <!-- Rest of navigation unchanged -->
    </ul>
</nav>
```

**Location**: base.html lines 64-97

### Step 4: Add i18n Translations

Extract new translatable strings and update all locale files:

```bash
# Extract new strings
make i18n-extract

# Update existing translations
make i18n-update

# Compile translations
make i18n-compile
```

**New translatable strings**:
- "Players" (navigation)
- "Top NHL Players by Scrabble Score" (page title)
- "Ranking of all NHL players..." (description)
- "Player Rankings" (section header)
- "Showing X of Y total players" (table info)
- "Scrabble Letter Values" (legend title)
- "point" / "points" (legend labels)

## Implementation Steps

1. **Create players.html template**:
   ```bash
   # Create new template file
   touch src/nhl_scrabble/web/templates/players.html
   # Add content from proposed solution above
   ```

2. **Add route to app.py**:
   - Open `src/nhl_scrabble/web/app.py`
   - Insert `players_page()` function after `root()` (around line 458)
   - Increase `top_players` to 50 for dedicated page (vs 20 on other pages)

3. **Update navigation in base.html**:
   - Open `src/nhl_scrabble/web/templates/base.html`
   - Insert Players menu item at line 69 (between Home and Teams)
   - Add `{% trans %}Players{% endtrans %}` for i18n

4. **Extract and update translations**:
   ```bash
   make i18n-extract    # Extract new strings to messages.pot
   make i18n-update     # Update all .po files
   ```

5. **Translate new strings** in all locale files:
   - `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po`
   - Add translations for "Players" and other new strings
   - Minimum: en_US, en_CA, fr_CA, sv_SE (primary locales)

6. **Compile translations**:
   ```bash
   make i18n-compile    # Generate .mo files
   ```

7. **Test locally**:
   ```bash
   # Start web server
   nhl-scrabble web

   # Visit in browser
   # http://localhost:8000/players

   # Test:
   # - Navigation menu shows Players item
   # - Players page loads with data
   # - Table is sortable
   # - Export buttons work
   # - i18n works (change language selector)
   # - Mobile navigation works
   ```

8. **Run automated tests**:
   ```bash
   # Unit tests (if any route tests exist)
   pytest tests/unit/test_web.py -v

   # QA web tests
   cd qa/web
   pytest tests/functional/ -v
   pytest tests/visual/ -v
   ```

9. **Update documentation** (if needed):
   - Update web interface screenshots
   - Update navigation documentation

## Testing Strategy

### Manual Testing

**Functional Tests**:
```bash
# Start server
nhl-scrabble web

# Test cases:
1. Navigate to http://localhost:8000/
2. Click "Players" in navigation menu
3. Verify players page loads with table
4. Verify table shows 50 players (or all available)
5. Click column headers to sort table
6. Click "Export CSV" button
7. Click "Export JSON" button
8. Change language selector - verify translations
9. Test mobile view (responsive design)
10. Test with different browsers (Chrome, Firefox, Safari)
```

**i18n Testing**:
```bash
# Test each locale
for locale in en_US en_CA fr_CA sv_SE fi_FI cs_CZ de_DE de_CH it_CH sk_SK ru_RU lv_LV; do
    echo "Testing locale: $locale"
    curl "http://localhost:8000/players?lang=$locale" | grep -o "<title>.*</title>"
done
```

### Automated Testing

**QA Web Tests**:
```bash
# Functional test for new page
cd qa/web
pytest tests/functional/test_players_page.py -v

# Visual regression test
pytest tests/visual/test_players_page.py --browser chromium -v
```

**Example Playwright Test** (tests/functional/test_players_page.py):
```python
import pytest
from playwright.sync_api import Page, expect

def test_players_page_loads(page: Page, base_url: str):
    """Test that players page loads successfully."""
    page.goto(f"{base_url}/players")
    expect(page).to_have_title("NHL Scrabble Analyzer - Top Players")

def test_players_navigation_exists(page: Page, base_url: str):
    """Test that Players menu item exists in navigation."""
    page.goto(base_url)
    players_link = page.locator('nav a:has-text("Players")')
    expect(players_link).to_be_visible()

def test_players_table_sortable(page: Page, base_url: str):
    """Test that players table is sortable."""
    page.goto(f"{base_url}/players")

    # Click "Score" column header to sort
    page.click('th[data-sort="score"]')

    # Verify first player has highest score
    first_score = page.locator('tbody tr:first-child td.score')
    expect(first_score).to_be_visible()

def test_players_export_buttons(page: Page, base_url: str):
    """Test that export buttons are present."""
    page.goto(f"{base_url}/players")

    csv_button = page.locator('button:has-text("Export CSV")')
    json_button = page.locator('button:has-text("Export JSON")')

    expect(csv_button).to_be_visible()
    expect(json_button).to_be_visible()
```

### Performance Testing

**Load Test**:
```bash
# Test with hey or ab
hey -n 100 -c 10 http://localhost:8000/players

# Verify caching works
curl -w "@curl-format.txt" http://localhost:8000/players
# Should be fast on subsequent requests
```

## Acceptance Criteria

- [ ] New "Players" menu item appears in navigation between "Home" and "Teams"
- [ ] Players menu item is visible on all pages
- [ ] `/players` route exists and returns HTTP 200
- [ ] Players page displays table with player rankings
- [ ] Table shows at least 50 players (or all available)
- [ ] Table columns: Rank, Player Name, Team, Score
- [ ] Table is sortable by all columns
- [ ] Export CSV button works
- [ ] Export JSON button works
- [ ] Page includes summary statistics (total players, highest/lowest/avg score)
- [ ] Page includes Scrabble letter values legend
- [ ] Timestamp shows data freshness
- [ ] i18n works for all supported locales (12 locales)
- [ ] Responsive design works on mobile devices
- [ ] Navigation menu works on mobile (hamburger menu)
- [ ] Page follows same design patterns as other pages (Teams, Divisions, etc.)
- [ ] Caching works (uses same cache as other endpoints)
- [ ] No performance regression (page loads < 2 seconds)
- [ ] All automated tests pass
- [ ] QA functional tests pass
- [ ] QA visual regression tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if needed)

## Related Files

- `src/nhl_scrabble/web/app.py` - FastAPI application (add new route)
- `src/nhl_scrabble/web/templates/base.html` - Base template (update navigation)
- `src/nhl_scrabble/web/templates/players.html` - New players page template (create)
- `src/nhl_scrabble/web/templates/stats.html` - Reference for player table design
- `src/nhl_scrabble/web/static/js/table-sort.js` - Table sorting functionality (already exists)
- `src/nhl_scrabble/web/static/js/export.js` - Export functionality (already exists)
- `src/nhl_scrabble/web/static/css/style.css` - Styles (may need minor additions)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - Translation files (all 12 locales)
- `qa/web/tests/functional/` - Functional tests directory
- `qa/web/tests/visual/` - Visual regression tests directory

## Dependencies

**No blocking dependencies**, but related to:
- Web interface infrastructure (already implemented)
- i18n system (already implemented)
- Table sorting functionality (already implemented)
- Export functionality (already implemented)
- QA test infrastructure (already implemented)

**Runtime dependencies**:
- FastAPI (already installed)
- Jinja2 templates (already configured)
- NHL API client (already implemented)
- Caching system (already implemented)

## Additional Notes

### Design Consistency

**Follow existing page patterns**:
- Use same header structure as other pages (Teams, Divisions, etc.)
- Use same table styling and classes
- Use same export button styling
- Use same fade-on-scroll animations
- Use same responsive breakpoints

**CSS Classes** (from existing pages):
- `.page-header` - Page title and description
- `.stats-summary` - Statistics cards
- `.stat-card` - Individual statistic card
- `.results-section` - Main content section
- `.table-container` - Table wrapper
- `.results-table.sortable` - Sortable table
- `.export-buttons` - Export button container
- `.legend-section` - Scrabble values legend

### Performance Considerations

**Caching Strategy**:
- Players page uses same cache as other pages (1 hour TTL)
- Cache key: `{top_players}_{top_team_players}`
- Cache hit reduces load on NHL API
- First request: ~2-3 seconds (API calls)
- Cached requests: < 100ms

**Data Volume**:
- NHL has ~700-800 active players
- Displaying 50 players: ~10-15 KB HTML
- Full player list (800): ~100-120 KB HTML
- Table sorting happens client-side (fast)

### i18n Considerations

**Translation Coverage**:
- Minimum viable: en_US, en_CA, fr_CA (North American hockey markets)
- Recommended: Add sv_SE, fi_FI, cs_CZ (European hockey markets)
- Full coverage: All 12 supported locales

**Locale-Specific Notes**:
- Player names NOT translated (proper nouns)
- Team abbreviations NOT translated (standard)
- UI strings translated (navigation, headers, labels)
- Number formatting may vary by locale (use Jinja2 filters)

### Mobile Responsiveness

**Hamburger Menu**:
- Players item appears in mobile navigation
- Same behavior as existing items
- Handled by existing `nav.js` script

**Table Responsiveness**:
- Table already responsive (existing CSS)
- May need horizontal scroll on small screens
- Consider card view for mobile (future enhancement)

### Future Enhancements

**Phase 2 Ideas** (not in this task):
- Player detail pages (`/players/{player_id}`)
- Search/filter functionality
- Pagination for large lists
- Player comparison tool
- Historical player rankings
- Player statistics integration (goals, assists, etc.)
- Team filtering (show players from specific team)

### Testing in TEST_MODE

**Visual Tests**:
- Set `NHL_SCRABBLE_TEST_MODE=1`
- Uses fixture data from `qa/web/tests/visual/fixtures/`
- Deterministic player data for visual regression tests
- Ensures consistent screenshots

### Accessibility

**WCAG 2.1 Compliance**:
- Table has proper ARIA labels (`role="table"`, `aria-label`)
- Navigation has `aria-label` for screen readers
- Buttons have `aria-label` for export actions
- Color contrast meets AA standards
- Keyboard navigation works (tab through table)

### Browser Compatibility

**Tested Browsers**:
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Mobile Chrome (Android)

### SEO Considerations

**Meta Tags**:
- Add Open Graph tags for social sharing
- Add Twitter Card tags
- Use semantic HTML (`<table>`, `<thead>`, `<tbody>`)
- Include descriptive page title
- Add meta description

## Implementation Notes

*To be filled during implementation:*
- Actual number of players displayed (50 or different?)
- Any CSS adjustments needed
- Translation completion status per locale
- QA test results (functional + visual)
- Performance metrics (load time, cache hit rate)
- Browser compatibility test results
- Accessibility audit results
- Date of implementation completion
