# Add FastAPI Infrastructure and Web Server Foundation

**GitHub Issue**: #103 - https://github.com/bdperkin/nhl-scrabble/issues/103

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Set up the foundational infrastructure for the NHL Scrabble web interface. This task creates the basic FastAPI application structure, adds required dependencies, implements a minimal web server with health check endpoint, and adds a CLI command to start the server. This is the first step in building the complete web interface - subsequent tasks will build upon this foundation to add API endpoints, frontend templates, and interactivity.

## Current State

The project currently has:

- Command-line only interface via `nhl-scrabble analyze`
- No web server or HTTP API
- No FastAPI or uvicorn dependencies
- CLI defined in `src/nhl_scrabble/cli.py` with only `analyze` command

**Current CLI** (`src/nhl_scrabble/cli.py`):

```python
import click
from nhl_scrabble.config import Config
from nhl_scrabble.logging_config import setup_logging
# ...

@click.command()
@click.option("--format", type=click.Choice(["text", "json", "html"]), default="text")
@click.option("-o", "--output", type=click.Path(), help="Output file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
# ... other options
def analyze(...):
    """Analyze NHL player names by Scrabble score."""
    # Implementation
    pass

if __name__ == "__main__":
    analyze()
```

**Current Dependencies** (`pyproject.toml`):

```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "rich>=13.7.0",
    "pydantic>=2.5.0",
    "click>=8.1.7",
    "python-dotenv>=1.0.0",
]
```

## Proposed Solution

Create minimal FastAPI web application infrastructure with health endpoint and server CLI command.

### 1. Add Web Dependencies

Update `pyproject.toml` to add web server dependencies:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.9",
]
```

**Dependency Justification**:

- `fastapi`: Modern, fast (high-performance) web framework
- `uvicorn[standard]`: ASGI server with WebSocket support
- `jinja2`: Template engine for HTML rendering
- `python-multipart`: For form data and file uploads

### 2. Create Web Module Structure

Create directory structure:

```
src/nhl_scrabble/web/
├── __init__.py
├── app.py           # FastAPI application
├── templates/       # Jinja2 templates (empty for now)
└── static/          # Static files (empty for now)
    ├── css/
    ├── js/
    └── img/
```

### 3. Implement Basic FastAPI Application

Create `src/nhl_scrabble/web/__init__.py`:

```python
"""Web interface for NHL Scrabble analyzer."""

from __future__ import annotations

__all__ = ["app"]

from nhl_scrabble.web.app import app
```

Create `src/nhl_scrabble/web/app.py`:

```python
"""FastAPI application for NHL Scrabble web interface.

This module provides a web interface to the NHL Scrabble analyzer,
allowing users to access analysis results via browser instead of CLI.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from nhl_scrabble import __version__

# Get paths relative to this module
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

# Create FastAPI application
app = FastAPI(
    title="NHL Scrabble Analyzer",
    description="Analyze NHL player names by Scrabble score",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files (if directory exists)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Jinja2 templates (if directory exists)
templates: Jinja2Templates | None = None
if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status including version and timestamp
    """
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint placeholder.

    Returns:
        Simple message directing to docs
    """
    return {
        "message": "NHL Scrabble Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }
```

### 4. Add Serve Command to CLI

Update `src/nhl_scrabble/cli.py` to add `serve` command:

```python
import click

# ... existing imports ...

@click.group()
def cli() -> None:
    """NHL Scrabble - Analyze NHL player names by Scrabble score."""
    pass


@cli.command()
@click.option("--format", type=click.Choice(["text", "json", "html"]), default="text")
@click.option("-o", "--output", type=click.Path(), help="Output file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
# ... other options (keep existing)
def analyze(...):
    """Analyze NHL player names by Scrabble score."""
    # Existing implementation
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload (development only)")
def serve(host: str, port: int, reload: bool) -> None:
    """Start web interface server.

    Starts a FastAPI web server providing browser-based access to
    NHL Scrabble analysis. Visit http://localhost:8000 after starting.

    Examples:
        # Start server on default port
        nhl-scrabble serve

        # Development mode with auto-reload
        nhl-scrabble serve --reload

        # Custom host and port
        nhl-scrabble serve --host 0.0.0.0 --port 5000
    """
    try:
        import uvicorn
    except ImportError:
        click.echo(
            "Error: uvicorn not installed. Install with: pip install nhl-scrabble[web]",
            err=True,
        )
        raise click.Abort()

    click.echo(f"Starting NHL Scrabble web server at http://{host}:{port}")
    click.echo("Press CTRL+C to stop")

    # Import here to avoid loading FastAPI when not needed
    from nhl_scrabble.web.app import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    cli()
```

Update CLI entry point in `src/nhl_scrabble/__main__.py`:

```python
"""Main entry point for nhl-scrabble package."""

from nhl_scrabble.cli import cli

if __name__ == "__main__":
    cli()
```

### 5. Create Empty Directory Structure

Create placeholder files to ensure directories exist:

`src/nhl_scrabble/web/templates/.gitkeep`:

```
# Placeholder for templates directory
```

`src/nhl_scrabble/web/static/css/.gitkeep`:

```
# Placeholder for CSS files
```

`src/nhl_scrabble/web/static/js/.gitkeep`:

```
# Placeholder for JavaScript files
```

`src/nhl_scrabble/web/static/img/.gitkeep`:

```
# Placeholder for image files
```

## Implementation Steps

1. **Update Dependencies**

   - Add FastAPI, uvicorn, jinja2, python-multipart to pyproject.toml
   - Run `uv lock` to update lock file
   - Install with `uv pip install -e ".[dev]" --system`

1. **Create Directory Structure**

   - Create `src/nhl_scrabble/web/` directory
   - Create subdirectories: `templates/`, `static/css/`, `static/js/`, `static/img/`
   - Add `.gitkeep` files to preserve empty directories

1. **Implement FastAPI Application**

   - Create `src/nhl_scrabble/web/__init__.py`
   - Create `src/nhl_scrabble/web/app.py` with FastAPI app
   - Add health endpoint
   - Add root endpoint
   - Configure static files and templates

1. **Update CLI**

   - Convert `analyze` function to subcommand under `cli` group
   - Add `serve` command with host, port, reload options
   - Update `__main__.py` to use CLI group
   - Add helpful error messages for missing dependencies

1. **Add Tests**

   - Create `tests/integration/test_web_infrastructure.py`
   - Test health endpoint returns correct structure
   - Test root endpoint returns API info
   - Test server starts successfully
   - Test FastAPI app metadata

1. **Update Documentation**

   - Update README.md with web server usage
   - Update CHANGELOG.md
   - Add docstrings to all new code

## Testing Strategy

### Unit Tests

None needed for this task - primarily integration and manual testing.

### Integration Tests

Create `tests/integration/test_web_infrastructure.py`:

```python
"""Integration tests for FastAPI web infrastructure."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble import __version__
from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app."""
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint returns correct structure."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns API information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "docs" in data
    assert "health" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_openapi_docs_available(client: TestClient) -> None:
    """Test OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs_available(client: TestClient) -> None:
    """Test ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_json_available(client: TestClient) -> None:
    """Test OpenAPI JSON spec is available."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert data["info"]["title"] == "NHL Scrabble Analyzer"
    assert data["info"]["version"] == __version__
```

### Manual Testing

```bash
# Test dependency installation
uv pip install -e ".[dev]" --system
python -c "import fastapi, uvicorn, jinja2; print('Dependencies OK')"

# Test CLI help
nhl-scrabble --help
nhl-scrabble serve --help

# Test server start
nhl-scrabble serve --reload

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
open http://localhost:8000/docs

# Test with custom host/port
nhl-scrabble serve --host 0.0.0.0 --port 5000
curl http://localhost:5000/health

# Verify auto-reload works (development)
# Change app.py and verify server reloads
```

## Acceptance Criteria

- [ ] FastAPI, uvicorn, jinja2, python-multipart added to pyproject.toml
- [ ] uv.lock updated with new dependencies
- [ ] Directory structure created: `web/`, `templates/`, `static/`
- [ ] `src/nhl_scrabble/web/__init__.py` created
- [ ] `src/nhl_scrabble/web/app.py` created with FastAPI app
- [ ] Health endpoint (`/health`) returns status, version, timestamp
- [ ] Root endpoint (`/`) returns API info
- [ ] OpenAPI docs available at `/docs`
- [ ] ReDoc docs available at `/redoc`
- [ ] CLI converted to command group
- [ ] `serve` command added with --host, --port, --reload options
- [ ] `analyze` command still works as before
- [ ] Server starts successfully with `nhl-scrabble serve`
- [ ] Integration tests pass for all endpoints
- [ ] Manual testing confirms server functionality
- [ ] Documentation updated (README, CHANGELOG)
- [ ] All tests pass (`pytest`)
- [ ] All quality checks pass (`make quality`)

## Related Files

- `pyproject.toml` - Add web dependencies
- `uv.lock` - Updated lock file
- `src/nhl_scrabble/web/__init__.py` - New module init
- `src/nhl_scrabble/web/app.py` - New FastAPI application
- `src/nhl_scrabble/web/templates/` - New directory (empty)
- `src/nhl_scrabble/web/static/` - New directory (empty)
- `src/nhl_scrabble/cli.py` - Add serve command, convert to group
- `src/nhl_scrabble/__main__.py` - Update to use CLI group
- `tests/integration/test_web_infrastructure.py` - New tests
- `README.md` - Add web server documentation
- `CHANGELOG.md` - Document new feature

## Dependencies

**No dependencies** - This is the foundation task. Subsequent web interface tasks depend on this:

- Task 003: Implement API endpoints (depends on this)
- Task 004: Build frontend templates (depends on this)
- Task 005: Add interactivity and charts (depends on this)
- Task 006: Testing and polish (depends on all above)

## Additional Notes

### Why FastAPI?

- **Modern**: Uses Python 3.10+ type hints and async/await
- **Fast**: Based on Starlette and Pydantic, very high performance
- **Auto docs**: Automatic OpenAPI/Swagger documentation
- **Type safety**: Full integration with Pydantic models
- **Easy**: Simple, intuitive API similar to Flask

### Development vs Production

**Development** (with --reload):

```bash
nhl-scrabble serve --reload
```

- Auto-reloads on code changes
- Useful for development
- Single worker process

**Production** (recommended: Gunicorn + Uvicorn):

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker nhl_scrabble.web.app:app
```

- Multiple worker processes
- Better performance
- More stable

### Directory Structure Rationale

```
src/nhl_scrabble/web/
├── app.py           # Main FastAPI app (this task)
├── templates/       # Jinja2 HTML templates (future task)
├── static/
│   ├── css/         # Stylesheets (future task)
│   ├── js/          # JavaScript (future task)
│   └── img/         # Images/icons (future task)
└── __init__.py
```

This structure:

- Keeps web code separate from core analysis logic
- Mirrors standard web application structure
- Makes it easy to add more files later
- Allows serving static files efficiently

### CLI Design

Using Click's command group pattern:

```bash
nhl-scrabble --help          # Shows all commands
nhl-scrabble analyze --help  # Analyze command help
nhl-scrabble serve --help    # Serve command help
```

This is:

- Extensible (easy to add more commands)
- Familiar (matches git, docker, etc.)
- Clear (command purpose obvious)

### Breaking Changes

**CLI Breaking Change**: The analyze command changes from:

```bash
python -m nhl_scrabble  # Old way
```

To:

```bash
nhl-scrabble analyze    # New way
```

**Migration**: Update `__main__.py` to maintain backwards compatibility:

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1 or not sys.argv[1] in ["analyze", "serve"]:
        # No command specified, default to analyze for backwards compat
        from nhl_scrabble.cli import analyze
        analyze()
    else:
        from nhl_scrabble.cli import cli
        cli()
```

### Security Considerations

- **No authentication** in this task (foundation only)
- **No rate limiting** in this task
- **No CORS** configuration yet
- **Development mode** (--reload) should not be used in production
- Future tasks will add proper security measures

### Performance Notes

- Health endpoint is lightweight (no I/O)
- Static file serving is efficient (Starlette handles this well)
- Template rendering not tested yet (no templates in this task)
- Async endpoints ready for future async operations

### Optional Dependencies

Consider making web dependencies optional:

```toml
[project.optional-dependencies]
web = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.9",
]
```

Then install with: `pip install nhl-scrabble[web]`

**Decision**: For now, include in main dependencies to keep installation simple. Can optimize later if package size becomes a concern.

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
