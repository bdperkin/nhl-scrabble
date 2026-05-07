# Auto-Link Entity Names Throughout Web Application

**GitHub Issue**: #545 - https://github.com/bdperkin/nhl-scrabble/issues/545

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Implement automatic linking for all text mentions of players, teams, divisions, and conferences throughout the web application. When any page displays text that matches an entity name (e.g., "Connor McDavid", "Toronto Maple Leafs", "Atlantic Division", "Eastern Conference"), it should automatically become a clickable link to that entity's detail page. This enhances navigation and improves the overall user experience by making the application more interconnected.

## Current State

**Existing Links**:
- Some pages have manual links (e.g., team names in tables link to `/teams/{abbrev}`)
- Player names in tables are plain text (no links to player detail pages yet, pending task #051)
- Division/conference names in breadcrumbs are manually linked
- Plain text mentions in descriptions, headers, or stat cards are not linked

**Manual Linking Examples**:
```jinja2
<!-- Manual link in team_detail.html -->
<a href="/divisions/{{ team_stats.team_division }}">{{ team_stats.team_division }}</a>

<!-- Table cells with manual links -->
<td class="team-name" data-value="{{ team.name }}">
    <a href="/teams/{{ team.abbrev }}">{{ team.name }}</a>
</td>
```

**Problem**:
- Inconsistent linking across pages
- Missed linking opportunities in plain text
- Manual linking is error-prone and tedious
- Hard to maintain as new entity types are added

## Proposed Solution

### Approach: Server-Side Jinja2 Filter

Implement a custom Jinja2 filter that automatically detects and links entity names in text content.

**Benefits**:
- Works with i18n (can preserve translated text)
- SEO-friendly (links rendered server-side)
- No client-side JavaScript overhead
- Consistent behavior across all pages

### Step 1: Create Auto-Linking Utility

Create `src/nhl_scrabble/web/utils/auto_link.py`:

```python
"""Automatic entity linking utilities for web templates."""

import re
from typing import Any


class EntityLinker:
    """Automatically link entity names to their detail pages."""

    def __init__(self, entities: dict[str, list[dict[str, Any]]]) -> None:
        """Initialize the entity linker with entity data.

        Args:
            entities: Dictionary containing entity lists by type:
                {
                    'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}, ...],
                    'divisions': [{'name': 'Atlantic'}, ...],
                    'conferences': [{'name': 'Eastern'}, ...],
                    'players': [{'name': 'Connor McDavid', 'id': 8478402}, ...]
                }
        """
        self.entities = entities
        self._build_patterns()

    def _build_patterns(self) -> None:
        """Build regex patterns for entity matching."""
        # Build patterns sorted by length (longest first to avoid partial matches)
        self.team_patterns = [
            (re.escape(team['name']), team['abbrev'])
            for team in sorted(
                self.entities.get('teams', []),
                key=lambda t: len(t['name']),
                reverse=True
            )
        ]

        self.division_patterns = [
            (re.escape(div['name']), div['name'])
            for div in sorted(
                self.entities.get('divisions', []),
                key=lambda d: len(d['name']),
                reverse=True
            )
        ]

        self.conference_patterns = [
            (re.escape(conf['name']), conf['name'])
            for conf in sorted(
                self.entities.get('conferences', []),
                key=lambda c: len(c['name']),
                reverse=True
            )
        ]

        # Players require player_id for linking (pending task #051)
        self.player_patterns = [
            (re.escape(player['name']), player.get('id'))
            for player in sorted(
                self.entities.get('players', []),
                key=lambda p: len(p['name']),
                reverse=True
            )
            if player.get('id')  # Only link players with IDs
        ]

    def link_text(self, text: str, exclude_types: list[str] | None = None) -> str:
        """Automatically link entity names in text.

        Args:
            text: Text to process
            exclude_types: Entity types to skip ('team', 'division', 'conference', 'player')

        Returns:
            Text with entity names wrapped in <a> tags

        Examples:
            >>> linker = EntityLinker({
            ...     'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}],
            ...     'divisions': [{'name': 'Atlantic'}]
            ... })
            >>> linker.link_text("The Maple Leafs play in the Atlantic division")
            'The <a href="/teams/TOR">Maple Leafs</a> play in the <a href="/divisions/Atlantic">Atlantic</a> division'
        """
        exclude_types = exclude_types or []
        result = text

        # Apply patterns in order: teams, divisions, conferences, players
        # Use word boundaries to avoid partial matches
        if 'team' not in exclude_types:
            for pattern, abbrev in self.team_patterns:
                regex = re.compile(rf'\b{pattern}\b', re.IGNORECASE)
                result = regex.sub(
                    lambda m: f'<a href="/teams/{abbrev}">{m.group(0)}</a>',
                    result
                )

        if 'division' not in exclude_types:
            for pattern, name in self.division_patterns:
                regex = re.compile(rf'\b{pattern}(?:\s+Division)?\b', re.IGNORECASE)
                result = regex.sub(
                    lambda m: f'<a href="/divisions/{name}">{m.group(0)}</a>',
                    result
                )

        if 'conference' not in exclude_types:
            for pattern, name in self.conference_patterns:
                regex = re.compile(rf'\b{pattern}(?:\s+Conference)?\b', re.IGNORECASE)
                result = regex.sub(
                    lambda m: f'<a href="/conferences/{name}">{m.group(0)}</a>',
                    result
                )

        if 'player' not in exclude_types:
            for pattern, player_id in self.player_patterns:
                if player_id:  # Only link if we have a player ID
                    regex = re.compile(rf'\b{pattern}\b', re.IGNORECASE)
                    result = regex.sub(
                        lambda m: f'<a href="/players/{player_id}">{m.group(0)}</a>',
                        result
                    )

        return result


def auto_link(text: str, entity_data: dict[str, Any], exclude: str = "") -> str:
    """Jinja2 filter to automatically link entity names.

    Usage in templates:
        {{ some_text | auto_link(entity_data) }}
        {{ some_text | auto_link(entity_data, exclude='team,player') }}

    Args:
        text: Text to process
        entity_data: Entity data dictionary (teams, divisions, conferences, players)
        exclude: Comma-separated list of entity types to exclude

    Returns:
        Text with entity names linked
    """
    exclude_types = [t.strip() for t in exclude.split(',') if t.strip()]
    linker = EntityLinker(entity_data)
    return linker.link_text(text, exclude_types)
```

### Step 2: Register Jinja2 Filter

Modify `src/nhl_scrabble/web/app.py` to add the custom filter:

```python
from nhl_scrabble.web.utils.auto_link import auto_link

# After templates initialization
if templates:
    # Register custom filters
    templates.env.filters['auto_link'] = auto_link
```

### Step 3: Prepare Entity Data for Templates

Modify route handlers to include entity data in template context:

```python
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request) -> HTMLResponse:
    # ... existing code to fetch data ...

    # Prepare entity data for auto-linking
    entity_data = {
        'teams': [
            {'name': team['name'], 'abbrev': team['abbrev']}
            for team in data['team_standings']
        ],
        'divisions': [
            {'name': div}
            for div in data['division_standings'].keys()
        ],
        'conferences': [
            {'name': conf}
            for conf in data['conference_standings'].keys()
        ],
        'players': [
            {'name': player['name'], 'id': player.get('id')}
            for player in data.get('top_players', [])
            if player.get('id')  # Only include players with IDs
        ],
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats,
            "entity_data": entity_data,  # Add to context
            # ... other context vars
        },
    )
```

### Step 4: Update Templates to Use Auto-Linking

**Example 1**: Auto-link stat card text:

```jinja2
<!-- Before -->
<p class="stat-detail">{{ stats.highest_team }} ({{ stats.highest_team_name }})</p>

<!-- After -->
<p class="stat-detail">{{ (stats.highest_team ~ " (" ~ stats.highest_team_name ~ ")") | auto_link(entity_data) | safe }}</p>
```

**Example 2**: Auto-link page headers:

```jinja2
<!-- Before -->
<h3>{% trans %}Team Standings by Total Scrabble Score{% endtrans %}</h3>

<!-- After (if header contains dynamic entity names) -->
<h3>{{ _("Team Standings by Total Scrabble Score") | auto_link(entity_data) | safe }}</h3>
```

**Example 3**: Exclude specific entity types:

```jinja2
<!-- Don't link team names in the teams table (already has manual links) -->
<td>{{ team.name | auto_link(entity_data, exclude='team') | safe }}</td>
```

### Step 5: Add CSS for Auto-Linked Entities

Add to `src/nhl_scrabble/web/static/css/styles.css`:

```css
/* Auto-linked entity names */
.stat-detail a,
.stat-value a {
    color: var(--link-color);
    text-decoration: none;
    border-bottom: 1px dotted var(--link-color);
    transition: border-bottom-color 0.2s;
}

.stat-detail a:hover,
.stat-value a:hover {
    border-bottom-color: transparent;
    color: var(--link-hover-color);
}

/* Prevent double-linking (if auto-link applied to already linked text) */
a a {
    pointer-events: none;
    text-decoration: none;
    color: inherit;
}
```

### Step 6: Performance Optimization

Cache entity patterns to avoid rebuilding on every request:

```python
# In app.py
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_entity_patterns(teams_hash: int, divisions_hash: int, conferences_hash: int) -> EntityLinker:
    """Get cached entity linker instance."""
    # Build from current data
    # ... implementation
```

## Implementation Steps

1. Create `src/nhl_scrabble/web/utils/` directory
2. Implement `src/nhl_scrabble/web/utils/auto_link.py` with `EntityLinker` class
3. Add `auto_link` Jinja2 filter to `app.py`
4. Update route handlers to include `entity_data` in template context
5. Identify all templates with entity name mentions
6. Update templates to use `| auto_link(entity_data) | safe` filter
7. Add CSS styles for auto-linked entities
8. Implement caching for entity patterns
9. Add unit tests for auto-linking logic
10. Add integration tests for template rendering
11. Test with various entity name formats (case sensitivity, partial matches)
12. Extract i18n strings if adding new translatable text
13. Update documentation

## Testing Strategy

### Unit Tests

**File**: `tests/unit/web/test_auto_link.py`

```python
"""Tests for automatic entity linking."""

import pytest
from nhl_scrabble.web.utils.auto_link import EntityLinker, auto_link


def test_auto_link_team_names() -> None:
    """Test linking team names."""
    entities = {
        'teams': [
            {'name': 'Maple Leafs', 'abbrev': 'TOR'},
            {'name': 'Canadiens', 'abbrev': 'MTL'},
        ]
    }
    linker = EntityLinker(entities)
    text = "The Maple Leafs beat the Canadiens 5-2."
    result = linker.link_text(text)
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result
    assert '<a href="/teams/MTL">Canadiens</a>' in result


def test_auto_link_division_names() -> None:
    """Test linking division names."""
    entities = {
        'divisions': [
            {'name': 'Atlantic'},
            {'name': 'Metropolitan'},
        ]
    }
    linker = EntityLinker(entities)
    text = "Atlantic Division leads over Metropolitan."
    result = linker.link_text(text)
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result
    assert '<a href="/divisions/Metropolitan">Metropolitan</a>' in result


def test_auto_link_case_insensitive() -> None:
    """Test case-insensitive matching."""
    entities = {
        'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}]
    }
    linker = EntityLinker(entities)
    text = "The maple leafs and MAPLE LEAFS are the same team."
    result = linker.link_text(text)
    # Should have 2 links (case-insensitive)
    assert result.count('<a href="/teams/TOR">') == 2


def test_auto_link_exclude_types() -> None:
    """Test excluding specific entity types."""
    entities = {
        'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}],
        'divisions': [{'name': 'Atlantic'}],
    }
    linker = EntityLinker(entities)
    text = "Maple Leafs play in Atlantic Division."
    result = linker.link_text(text, exclude_types=['team'])
    assert '<a href="/teams/TOR">Maple Leafs</a>' not in result
    assert '<a href="/divisions/Atlantic">Atlantic Division</a>' in result


def test_auto_link_no_partial_matches() -> None:
    """Test that partial words are not matched."""
    entities = {
        'divisions': [{'name': 'Pacific'}]
    }
    linker = EntityLinker(entities)
    text = "Specifically, the Pacific Division is strong."
    result = linker.link_text(text)
    # "Specifically" should not be linked (contains "Pacific")
    assert result.count('<a href="/divisions/Pacific">') == 1


def test_auto_link_jinja2_filter() -> None:
    """Test Jinja2 filter function."""
    entity_data = {
        'teams': [{'name': 'Maple Leafs', 'abbrev': 'TOR'}]
    }
    text = "The Maple Leafs won!"
    result = auto_link(text, entity_data)
    assert '<a href="/teams/TOR">Maple Leafs</a>' in result
```

### Integration Tests

**File**: `tests/integration/web/test_auto_link_templates.py`

```python
"""Integration tests for auto-linking in templates."""

import pytest
from fastapi.testclient import TestClient


def test_home_page_auto_links_entities(test_client: TestClient) -> None:
    """Test that home page auto-links entity names."""
    response = test_client.get("/")
    assert response.status_code == 200
    # Should contain links to teams, divisions, conferences
    assert b'href="/teams/' in response.content
    assert b'href="/divisions/' in response.content
    assert b'href="/conferences/' in response.content


def test_team_detail_page_auto_links(test_client: TestClient) -> None:
    """Test that team detail page auto-links division/conference."""
    response = test_client.get("/teams/TOR")
    assert response.status_code == 200
    # Division and conference should be linked
    assert b'href="/divisions/Atlantic"' in response.content
    assert b'href="/conferences/Eastern"' in response.content
```

### Manual Testing

1. **Home Page**:
   - Check stat cards for auto-linked team names
   - Verify top player names link to player pages (once #051 is implemented)

2. **Teams Page**:
   - Team names in table should have manual links (not auto-linked)
   - Division/conference in table should be auto-linked

3. **Player Detail Page**:
   - Team name should link to team page
   - Division/conference should link to respective pages

4. **Edge Cases**:
   - Test with teams that have similar names (e.g., "Rangers" vs "New York Rangers")
   - Test case sensitivity (MAPLE LEAFS vs Maple Leafs)
   - Test partial matches (should NOT link "Specifically" when "Pacific" is an entity)

5. **Performance**:
   - Check page load time with auto-linking enabled
   - Verify caching works (subsequent requests should be faster)

## Acceptance Criteria

- [ ] `EntityLinker` class implemented with pattern matching
- [ ] `auto_link` Jinja2 filter registered in app.py
- [ ] Entity data prepared and passed to all template contexts
- [ ] Team names auto-linked to `/teams/{abbrev}` pages
- [ ] Division names auto-linked to `/divisions/{name}` pages
- [ ] Conference names auto-linked to `/conferences/{name}` pages
- [ ] Player names auto-linked to `/players/{id}` pages (depends on task #051)
- [ ] Case-insensitive matching works correctly
- [ ] Word boundary matching prevents partial matches
- [ ] Exclude option works to prevent double-linking
- [ ] CSS styles added for auto-linked entities
- [ ] Performance caching implemented
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] No regression in page load times
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/web/utils/auto_link.py` - Auto-linking utility (create)
- `src/nhl_scrabble/web/app.py` - Register Jinja2 filter, add entity_data to contexts
- `src/nhl_scrabble/web/templates/*.html` - Update templates to use auto_link filter
- `src/nhl_scrabble/web/static/css/styles.css` - Add auto-link styles
- `tests/unit/web/test_auto_link.py` - Unit tests (create)
- `tests/integration/web/test_auto_link_templates.py` - Integration tests (create)

## Dependencies

- Jinja2 templating engine
- Task #046: Players page (provides player data)
- Task #047: League page (provides league-wide data)
- Task #048: Conference detail pages (provides conference URLs)
- Task #049: Division detail pages (provides division URLs)
- Task #050: Team detail pages (provides team URLs)
- Task #051: Player detail pages (provides player URLs) - **CRITICAL DEPENDENCY**

**Note**: Player auto-linking requires player IDs from task #051. Can implement team/division/conference linking first, add player linking later.

## Additional Notes

### Performance Considerations

**Regex Matching**:
- Sorting entities by length (longest first) prevents partial matches
- Using `\b` word boundaries ensures whole-word matching
- Compiled regex patterns cached for reuse

**Caching Strategy**:
- Entity patterns built once per request (with caching between requests)
- `@lru_cache` on pattern builder for repeated lookups
- Entity data passed through template context (avoid global state)

**Impact**:
- Minimal overhead (~10-20ms per page for pattern matching)
- Caching reduces to <1ms for cache hits

### Edge Cases

**Similar Names**:
- "Rangers" vs "New York Rangers"
- Solution: Sort by length, match longest first
- "New York Rangers" matched before "Rangers"

**Case Sensitivity**:
- Use `re.IGNORECASE` flag
- Preserve original case in output (use matched text, not pattern)

**Partial Matches**:
- "Pacific" should not match "Specifically"
- Solution: Use `\b` word boundaries in regex

**Double Linking**:
- If text already contains `<a>` tags, don't link inside them
- Solution: Exclude entity types that are already manually linked
- Alternative: Parse HTML, only link text nodes (more complex)

### I18n Considerations

**Translated Entity Names**:
- Team names are proper nouns (not translated)
- Division/conference names might be translated
- Solution: Match against original English names, preserve displayed text

**Filter Usage with I18n**:
```jinja2
<!-- Correct: Translate first, then auto-link -->
{{ _("Some text with entity names") | auto_link(entity_data) | safe }}

<!-- Incorrect: Auto-link before translation (breaks translation keys) -->
{{ ("Some text" | auto_link(entity_data)) | trans }}
```

### Alternative Approaches Considered

**Client-Side JavaScript**:
- **Pros**: No server-side processing, works on static content
- **Cons**: SEO issues, slower initial render, JavaScript dependency
- **Verdict**: Rejected (SEO and performance concerns)

**Pre-Processing at Data Layer**:
- **Pros**: One-time processing, very fast rendering
- **Cons**: Tight coupling, harder to maintain, breaks data/presentation separation
- **Verdict**: Rejected (architectural concerns)

**Markdown-Style Links**:
- **Pros**: Explicit control, easy to debug
- **Cons**: Manual work, error-prone, doesn't help with existing text
- **Verdict**: Rejected (doesn't solve the automation problem)

### Future Enhancements

**Tooltip Previews**:
- Hover over linked entity → show preview card
- Display: photo, key stats, quick info
- Requires JavaScript for hover behavior

**Customizable Linking**:
- User preference to enable/disable auto-linking
- Store in cookies or local storage
- Toggle in settings menu

**Smart Exclusions**:
- Automatically detect when text is already inside an `<a>` tag
- Skip linking in that context
- More robust than manual exclusions

**Performance Monitoring**:
- Track auto-linking overhead
- Log slow patterns (>50ms)
- Optimize problematic regex patterns

## Implementation Notes

*To be filled during implementation:*
- Actual performance impact measurements
- Challenges encountered with regex patterns
- Deviations from plan
- Actual effort vs estimated
- Edge cases discovered during testing
