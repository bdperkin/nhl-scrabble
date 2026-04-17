# Implement HTML Output Format

**GitHub Issue**: #46 - https://github.com/bdperkin/nhl-scrabble/issues/46

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

The configuration includes `output_format: html` but HTML output is not actually implemented. HTML reports would provide better visualization, interactive tables, and shareable results.

## Current State

```python
@dataclass
class Config:
    """Application configuration."""
    output_format: Literal["text", "json", "html"] = "text"  # html not implemented
```

CLI accepts `--format html` but generates error or falls back to text.

## Proposed Solution

Implement HTML report generator using Jinja2 templates:

### 1. Create HTML Template

`src/nhl_scrabble/templates/report.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHL Scrabble Score Analysis - {{ timestamp }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #003087;
            border-bottom: 3px solid #C60C30;
            padding-bottom: 10px;
        }
        h2 {
            color: #003087;
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        th {
            background: #003087;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .rank {
            font-weight: bold;
            color: #003087;
        }
        .indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            line-height: 20px;
            text-align: center;
            border-radius: 50%;
            margin-left: 5px;
            font-size: 12px;
            font-weight: bold;
        }
        .indicator.playoff {
            background: #4CAF50;
            color: white;
        }
        .indicator.eliminated {
            background: #C60C30;
            color: white;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #003087;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 14px;
            text-align: center;
        }
        @media print {
            body {
                background: white;
            }
            table {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <h1>🏒 NHL Scrabble Score Analysis</h1>
    <p><strong>Generated:</strong> {{ timestamp }}</p>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-label">Total Players</div>
            <div class="stat-value">{{ stats.total_players }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Teams</div>
            <div class="stat-value">{{ stats.total_teams }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Average Score</div>
            <div class="stat-value">{{ stats.average_score | round(1) }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Highest Score</div>
            <div class="stat-value">{{ stats.highest_score }}</div>
        </div>
    </div>

    <h2>Top {{ top_n }} Players by Scrabble Score</h2>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Score</th>
            </tr>
        </thead>
        <tbody>
            {% for player in top_players %}
            <tr>
                <td class="rank">{{ loop.index }}</td>
                <td>{{ player.first_name }} {{ player.last_name }}</td>
                <td>{{ player.team }}</td>
                <td>{{ player.score }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>Conference Standings</h2>
    {% for conference in conferences %}
    <h3>{{ conference.name }}</h3>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Total Score</th>
                <th>Avg Score</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for team in conference.teams %}
            <tr>
                <td class="rank">{{ loop.index }}</td>
                <td>{{ team.name }} ({{ team.abbrev }})</td>
                <td>{{ team.total_score }}</td>
                <td>{{ team.avg_score | round(2) }}</td>
                <td>
                    {% if team.playoff %}
                    <span class="indicator playoff" title="Playoff team">✓</span>
                    {% else %}
                    <span class="indicator eliminated" title="Eliminated">✗</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endfor %}

    <div class="footer">
        <p>Generated by <a href="https://github.com/bdperkin/nhl-scrabble">nhl-scrabble</a> v{{ version }}</p>
        <p>Data source: NHL API • Scoring: Standard Scrabble letter values</p>
    </div>
</body>
</html>
```

### 2. Create HTML Report Generator

`src/nhl_scrabble/reports/html_report.py`:

```python
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
from nhl_scrabble.reports.base import BaseReport
from nhl_scrabble import __version__

class HTMLReport(BaseReport):
    """Generate HTML format reports."""

    def __init__(self) -> None:
        """Initialize HTML report generator."""
        super().__init__()

        # Setup Jinja2 environment
        self.env = Environment(
            loader=PackageLoader('nhl_scrabble', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate(
        self,
        team_scores: list[TeamScore],
        top_players: list[PlayerScore],
        conference_standings: dict[str, ConferenceStandings],
        division_standings: dict[str, DivisionStandings],
        playoff_bracket: dict[str, Any],
        stats: dict[str, Any],
    ) -> str:
        """Generate HTML report."""
        template = self.env.get_template('report.html')

        # Prepare data
        conferences = []
        for conf_name, standings in conference_standings.items():
            conferences.append({
                'name': conf_name,
                'teams': standings.teams
            })

        # Render template
        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            version=__version__,
            stats=stats,
            top_n=len(top_players),
            top_players=top_players,
            conferences=conferences,
            playoff_bracket=playoff_bracket,
        )

        return html
```

### 3. Update CLI to Support HTML

`src/nhl_scrabble/cli.py`:

```python
from nhl_scrabble.reports.html_report import HTMLReport

def analyze(...):
    """Analyze NHL player names by Scrabble score."""
    # ... existing code ...

    # Generate report based on format
    if format == "json":
        report = JSONReport()
    elif format == "html":
        report = HTMLReport()
    else:
        report = TextReport()

    output_content = report.generate(
        team_scores=team_scores,
        top_players=top_players,
        conference_standings=conference_standings,
        division_standings=division_standings,
        playoff_bracket=playoff_bracket,
        stats=stats,
    )

    # ... write output ...
```

## Testing Strategy

Add tests in `tests/unit/test_html_report.py`:

```python
import pytest
from bs4 import BeautifulSoup
from nhl_scrabble.reports.html_report import HTMLReport

def test_html_report_generates_valid_html():
    """Test that HTML report generates valid HTML."""
    report = HTMLReport()

    # Generate with sample data
    html = report.generate(
        team_scores=[...],
        top_players=[...],
        conference_standings={...},
        division_standings={...},
        playoff_bracket={...},
        stats={...},
    )

    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Verify structure
    assert soup.find('html') is not None
    assert soup.find('head') is not None
    assert soup.find('body') is not None
    assert soup.find('title') is not None

def test_html_report_includes_all_sections():
    """Test that HTML report includes all required sections."""
    report = HTMLReport()
    html = report.generate(...)
    soup = BeautifulSoup(html, 'html.parser')

    # Check for key sections
    assert soup.find('h1', string='NHL Scrabble Score Analysis') is not None
    assert soup.find('h2', string='Top Players by Scrabble Score') is not None
    assert soup.find('h2', string='Conference Standings') is not None

    # Check for tables
    tables = soup.find_all('table')
    assert len(tables) >= 3  # Top players + 2 conferences

def test_html_report_escapes_dangerous_content():
    """Test that HTML report escapes XSS attempts."""
    report = HTMLReport()

    # Create player with XSS attempt in name
    player = PlayerScore(
        first_name="<script>alert('xss')</script>",
        last_name="Test",
        team="TOR",
        score=50
    )

    html = report.generate(top_players=[player], ...)

    # Should not contain raw script tag
    assert "<script>" not in html
    assert "alert('xss')" not in html or "&lt;script&gt;" in html

def test_html_report_responsive_design():
    """Test that HTML includes responsive meta tag."""
    report = HTMLReport()
    html = report.generate(...)
    soup = BeautifulSoup(html, 'html.parser')

    meta = soup.find('meta', attrs={'name': 'viewport'})
    assert meta is not None
    assert 'width=device-width' in meta['content']
```

## Acceptance Criteria

- [ ] `jinja2` dependency added to pyproject.toml
- [ ] HTML template created with responsive design
- [ ] HTMLReport class generates valid HTML
- [ ] All sections included (stats, top players, standings, playoff bracket)
- [ ] HTML escapes user-generated content (XSS prevention)
- [ ] Tables are sortable (optional enhancement)
- [ ] Print-friendly stylesheet included
- [ ] Unit tests verify HTML generation
- [ ] Integration tests verify CLI `--format html` works
- [ ] Documentation updated with HTML output examples

## Related Files

- `src/nhl_scrabble/templates/report.html` (new)
- `src/nhl_scrabble/reports/html_report.py` (new)
- `src/nhl_scrabble/cli.py`
- `pyproject.toml` (add jinja2 dependency)
- `tests/unit/test_html_report.py` (new)
- `README.md` (add HTML examples)

## Dependencies

- `jinja2>=3.1.0` (new dependency)
- `beautifulsoup4>=4.12.0` (for testing only)

## Example Usage

```bash
# Generate HTML report to file
nhl-scrabble analyze --format html --output report.html

# Open in browser
xdg-open report.html  # Linux
open report.html      # macOS
start report.html     # Windows
```

## Future Enhancements

- [ ] Add interactive sorting to tables (JavaScript)
- [ ] Add charts/graphs (Chart.js or plotly)
- [ ] Add dark mode toggle
- [ ] Add export to PDF button
- [ ] Add team logos
- [ ] Add player photos
- [ ] Add search/filter functionality
- [ ] Add comparison view

## Implementation Notes

**Implemented**: 2026-04-16
**Branch**: enhancement/001-html-output
**PR**: #92 - https://github.com/bdperkin/nhl-scrabble/pull/92
**Commits**: 1 commit (b0b5d3b)

### Actual Implementation

Followed the proposed solution with implementation directly in `cli.py` instead of creating a separate `HTMLReport` class:

- Created HTML template at `src/nhl_scrabble/templates/report.html` with NHL color scheme
- Implemented `generate_html_report()` function in `cli.py` using Jinja2 templating
- Used existing data models (PlayerScore, TeamScore, PlayoffTeam) instead of custom data structures
- Added Jinja2 autoescape for automatic XSS protection
- Integrated with existing CLI analyze command via config.output_format check

### Challenges Encountered

- **Python 3.10 Compatibility**: `datetime.UTC` not available in Python 3.10

  - Solution: Used `datetime.now(tz=timezone.utc)` instead

- **Data Model Field Names**: Template needed to match actual model fields

  - Fixed: Used `abbrev`, `total`, `avg`, `full_score` instead of assumed names

- **Test Fixtures**: Initial fixtures used incorrect field names

  - Fixed: Updated fixtures to match PlayerScore and TeamScore dataclass definitions

### Deviations from Plan

- **No separate HTMLReport class**: Implemented directly in `cli.py` as `generate_html_report()` function for simplicity
- **Simplified data preparation**: Used PlayoffTeam objects directly from playoff standings instead of creating custom team dictionaries
- **Division standings organization**: Pulled division teams from playoff standings rather than separate processing

### Actual vs Estimated Effort

- **Estimated**: 4-6h
- **Actual**: ~4h
- **Reason**: Implementation was straightforward, most time spent on test fixture corrections and Python 3.10 compatibility

### Related PRs

- PR #92 - Main implementation

### Lessons Learned

- Always verify data model field names before writing templates
- Python 3.10 compatibility requires checking for newer stdlib features (datetime.UTC)
- Jinja2's autoescape provides excellent XSS protection out of the box
- BeautifulSoup is valuable for HTML test validation
