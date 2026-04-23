# Build Web Interface with FastAPI

**GitHub Issue**: #50 - https://github.com/bdperkin/nhl-scrabble/issues/50

## Priority

**NICE TO HAVE** - Next Quarter

## Estimated Effort

16-24 hours

## Description

Create a web interface using FastAPI to make the NHL Scrabble analyzer accessible via browser. This would enable:

- Easy access without command-line knowledge
- Shareable URLs for specific analyses
- Interactive exploration of results
- Real-time updates

## Current State

Command-line only:

```bash
nhl-scrabble analyze
```

Limited accessibility for non-technical users.

## Proposed Solution

Build FastAPI web application with:

### 1. Backend API

`src/nhl_scrabble/web/app.py`:

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime
from typing import Optional

from nhl_scrabble.api import NHLClient
from nhl_scrabble.config import Config
from nhl_scrabble.processors import TeamProcessor, PlayoffCalculator

app = FastAPI(
    title="NHL Scrabble Analyzer",
    description="Analyze NHL player names by Scrabble score",
    version="2.0.0",
)

# Mount static files
app.mount(
    "/static", StaticFiles(directory="src/nhl_scrabble/web/static"), name="static"
)

# Templates
templates = Jinja2Templates(directory="src/nhl_scrabble/web/templates")

# Cache for analysis results
analysis_cache = {}


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with analysis form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    top_players: int = 20,
    top_team_players: int = 5,
    use_cache: bool = True,
):
    """Run NHL Scrabble analysis."""
    cache_key = f"{top_players}_{top_team_players}"

    # Check cache
    if use_cache and cache_key in analysis_cache:
        cached = analysis_cache[cache_key]
        if (datetime.now() - cached["timestamp"]).seconds < 3600:  # 1 hour
            return cached["data"]

    # Run analysis
    try:
        config = Config(top_players=top_players, top_team_players=top_team_players)

        with NHLClient() as client:
            # Fetch data
            standings = client.get_standings()
            # ... rest of analysis logic ...

            result = {
                "timestamp": datetime.now().isoformat(),
                "top_players": top_players_data,
                "team_standings": team_standings_data,
                "conference_standings": conference_standings_data,
                "playoff_bracket": playoff_bracket_data,
                "stats": stats_data,
            }

            # Cache result
            analysis_cache[cache_key] = {"timestamp": datetime.now(), "data": result}

            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/players/{player_id}")
async def get_player(player_id: int):
    """Get details for a specific player."""
    # Implementation
    pass


@app.get("/api/teams/{team_abbrev}")
async def get_team(team_abbrev: str):
    """Get details for a specific team."""
    # Implementation
    pass


@app.get("/api/cache/clear")
async def clear_cache():
    """Clear the analysis cache."""
    analysis_cache.clear()
    return {"message": "Cache cleared"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)
```

### 2. Frontend Template

`src/nhl_scrabble/web/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
 <head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>
   NHL Scrabble Analyzer
  </title>
  <link href="/static/css/style.css" rel="stylesheet"/>
  <script src="https://unpkg.com/htmx.org@1.9.10">
  </script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js">
  </script>
 </head>
 <body>
  <div class="container">
   <header>
    <h1>
     🏒 NHL Scrabble Analyzer
    </h1>
    <p>
     Analyze NHL player names by Scrabble score
    </p>
   </header>
   <section class="controls">
    <form hx-indicator="#loading" hx-post="/api/analyze" hx-target="#results">
     <div class="form-group">
      <label for="top_players">
       Top Players:
      </label>
      <input id="top_players" max="100" min="1" name="top_players" type="number" value="20"/>
     </div>
     <div class="form-group">
      <label for="top_team_players">
       Top Team Players:
      </label>
      <input id="top_team_players" max="30" min="1" name="top_team_players" type="number" value="5"/>
     </div>
     <div class="form-group">
      <label for="use_cache">
       Use Cache:
      </label>
      <input checked="" id="use_cache" name="use_cache" type="checkbox"/>
     </div>
     <button type="submit">
      Analyze
     </button>
    </form>
    <div class="htmx-indicator" id="loading">
     <div class="spinner">
     </div>
     <p>
      Fetching NHL data...
     </p>
    </div>
   </section>
   <section id="results">
    <!-- Results will be loaded here via HTMX -->
   </section>
  </div>
  <script src="/static/js/app.js">
  </script>
 </body>
</html>
```

### 3. JavaScript

`src/nhl_scrabble/web/static/js/app.js`:

```javascript
// Handle analysis results
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'results') {
        renderCharts();
        initializeTables();
    }
});

function renderCharts() {
    // Render score distribution chart
    const ctx = document.getElementById('scoreChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: teamNames,
            datasets: [{
                label: 'Team Scrabble Scores',
                data: teamScores,
                backgroundColor: 'rgba(0, 48, 135, 0.6)',
                borderColor: 'rgba(0, 48, 135, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function initializeTables() {
    // Add sorting to tables
    document.querySelectorAll('th[data-sortable]').forEach(header => {
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
}

function sortTable(header) {
    // Table sorting logic
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const index = Array.from(header.parentElement.children).indexOf(header);

    rows.sort((a, b) => {
        const aValue = a.cells[index].textContent;
        const bValue = b.cells[index].textContent;
        return aValue.localeCompare(bValue, undefined, {
            numeric: true
        });
    });

    rows.forEach(row => tbody.appendChild(row));
}
```

### 4. CLI Command

Add web server command to CLI:

```python
@click.group()
def cli():
    """NHL Scrabble CLI."""
    pass

@cli.command()
def analyze(...):
    """Analyze NHL player names."""
    # Existing analyze command
    pass

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload (development)")
def serve(host: str, port: int, reload: bool):
    """Start web interface server."""
    import uvicorn
    from nhl_scrabble.web.app import app

    click.echo(f"Starting web server at http://{host}:{port}")
    uvicorn.run("nhl_scrabble.web.app:app", host=host, port=port, reload=reload)
```

## Testing Strategy

Add tests in `tests/integration/test_web.py`:

```python
import pytest
from fastapi.testclient import TestClient
from nhl_scrabble.web.app import app

client = TestClient(app)


def test_home_page():
    """Test home page loads."""
    response = client.get("/")

    assert response.status_code == 200
    assert "NHL Scrabble Analyzer" in response.text


def test_analyze_endpoint():
    """Test analyze API endpoint."""
    response = client.post(
        "/api/analyze",
        json={"top_players": 20, "top_team_players": 5, "use_cache": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert "top_players" in data
    assert "team_standings" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_clear_cache_endpoint():
    """Test cache clear endpoint."""
    response = client.get("/api/cache/clear")

    assert response.status_code == 200
    assert response.json()["message"] == "Cache cleared"


def test_invalid_parameters():
    """Test API handles invalid parameters."""
    response = client.post(
        "/api/analyze", json={"top_players": -5, "top_team_players": 5}  # Invalid
    )

    assert response.status_code == 422  # Validation error
```

## Acceptance Criteria

- [ ] FastAPI application serves web interface
- [ ] Home page with analysis form
- [ ] API endpoints for analysis, players, teams
- [ ] Results displayed with charts and tables
- [ ] Interactive table sorting
- [ ] Cache management
- [ ] Health check endpoint
- [ ] CLI `serve` command starts server
- [ ] Responsive design (mobile-friendly)
- [ ] Unit and integration tests
- [ ] Documentation with usage examples

## Related Files

- `src/nhl_scrabble/web/app.py` (new)
- `src/nhl_scrabble/web/templates/` (new directory)
- `src/nhl_scrabble/web/static/` (new directory)
- `src/nhl_scrabble/cli.py` (add serve command)
- `pyproject.toml` (add fastapi, uvicorn dependencies)
- `tests/integration/test_web.py` (new)
- `README.md` (add web interface documentation)

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
  # ... existing ...
  "fastapi>=0.110.0",
  "uvicorn[standard]>=0.27.0",
  "jinja2>=3.1.0",
  "python-multipart>=0.0.9",
]
```

## Deployment Options

1. **Local Development**:

   ```bash
   nhl-scrabble serve --reload
   ```

1. **Production**:

   ```bash
   # Using Gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker nhl_scrabble.web.app:app

   # Using Docker
   docker build -t nhl-scrabble .
   docker run -p 8000:8000 nhl-scrabble
   ```

1. **Cloud Platforms**:

   - Heroku
   - AWS Lambda + API Gateway
   - Google Cloud Run
   - Azure App Service

## Future Enhancements

- [ ] User accounts and saved analyses
- [ ] Historical data comparison
- [ ] Export to PDF/Excel
- [ ] Real-time updates with WebSockets
- [ ] Player/team search
- [ ] Custom scoring rules
- [ ] Admin dashboard
- [ ] API rate limiting
- [ ] GraphQL API
- [ ] OAuth authentication

## Example Usage

```bash
# Start development server
nhl-scrabble serve --reload

# Production server
nhl-scrabble serve --host 0.0.0.0 --port 8000

# Visit in browser
open http://localhost:8000
```

## Security Considerations

- [ ] Rate limiting on API endpoints
- [ ] CORS configuration
- [ ] Input validation
- [ ] XSS prevention (template escaping)
- [ ] CSRF protection
- [ ] HTTPS in production
- [ ] Security headers (helmet)
