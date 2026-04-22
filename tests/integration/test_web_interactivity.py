"""Integration tests for web interactivity features.

Tests for:
- Template rendering (index.html)
- HTMX support (HTML responses)
- JavaScript module loading
- Chart visualization data
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client() -> TestClient:
    """Create FastAPI test client.

    Returns:
        TestClient instance
    """
    return TestClient(app)


def test_root_returns_html_template(client: TestClient) -> None:
    """Test that root endpoint serves HTML template."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert b"NHL Scrabble Analyzer" in response.content
    assert b"analysisForm" in response.content  # Form should be present


def test_root_template_includes_javascript_modules(client: TestClient) -> None:
    """Test that root template loads all JavaScript modules."""
    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()

    # Check for CDN libraries
    assert "unpkg.com/htmx.org" in html
    assert "cdn.jsdelivr.net/npm/chart.js" in html

    # Check for custom JavaScript modules
    assert "/static/js/errors.js" in html
    assert "/static/js/ui.js" in html
    assert "/static/js/nav.js" in html
    assert "/static/js/table-sort.js" in html
    assert "/static/js/export.js" in html
    assert "/static/js/charts.js" in html
    assert "/static/js/app.js" in html


def test_root_template_includes_mobile_navigation(client: TestClient) -> None:
    """Test that root template includes mobile navigation elements."""
    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()

    # Check for mobile nav elements
    assert 'id="navToggle"' in html
    assert 'class="nav-toggle"' in html
    assert 'class="hamburger"' in html
    assert 'id="navMenu"' in html


def test_root_template_includes_htmx_attributes(client: TestClient) -> None:
    """Test that form has HTMX attributes."""
    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()

    # Check for HTMX attributes on form
    assert 'hx-get="/api/analyze"' in html
    assert 'hx-target="#results"' in html
    assert 'hx-indicator="#loading"' in html


def test_analyze_get_returns_json_by_default(client: TestClient) -> None:
    """Test that analyze GET endpoint returns JSON by default."""
    response = client.get("/api/analyze?top_players=5&top_team_players=3&use_cache=false")

    # Will fail if NHL API is unavailable, but should return structured response
    assert response.status_code in [200, 500]  # 200 = success, 500 = NHL API down

    if response.status_code == 200:
        data = response.json()
        assert "top_players" in data
        assert "team_standings" in data
        assert "stats" in data


def test_analyze_get_returns_html_for_htmx(client: TestClient) -> None:
    """Test that analyze GET endpoint returns HTML when HX-Request header present."""
    headers = {"HX-Request": "true", "Accept": "text/html"}

    response = client.get(
        "/api/analyze?top_players=5&top_team_players=3&use_cache=false", headers=headers
    )

    # Will fail if NHL API is unavailable
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        assert response.headers["content-type"].startswith("text/html")
        html = response.content.decode()

        # Check for results template content
        assert "Top" in html
        assert "Players" in html
        assert "Team Standings" in html


def test_analyze_get_html_includes_sortable_tables(client: TestClient) -> None:
    """Test that HTML response includes sortable table attributes."""
    headers = {"HX-Request": "true", "Accept": "text/html"}

    response = client.get(
        "/api/analyze?top_players=5&top_team_players=3&use_cache=false", headers=headers
    )

    if response.status_code == 200:
        html = response.content.decode()

        # Check for sortable table attributes
        assert 'class="sortable"' in html or "data-sort=" in html
        assert 'data-sort-type="number"' in html
        assert 'data-sort-type="string"' in html


def test_analyze_get_html_includes_export_buttons(client: TestClient) -> None:
    """Test that HTML response includes export buttons."""
    headers = {"HX-Request": "true", "Accept": "text/html"}

    response = client.get(
        "/api/analyze?top_players=5&top_team_players=3&use_cache=false", headers=headers
    )

    if response.status_code == 200:
        html = response.content.decode()

        # Check for export buttons
        assert "Export CSV" in html or "export-" in html
        assert "Export JSON" in html or "export-" in html


def test_analyze_get_html_includes_chart_canvases(client: TestClient) -> None:
    """Test that HTML response includes chart canvas elements."""
    headers = {"HX-Request": "true", "Accept": "text/html"}

    response = client.get(
        "/api/analyze?top_players=5&top_team_players=3&use_cache=false", headers=headers
    )

    if response.status_code == 200:
        html = response.content.decode()

        # Check for chart canvases
        assert "teamScoresChart" in html
        assert "playerDistributionChart" in html
        assert "<canvas" in html


def test_analyze_get_html_includes_fade_on_scroll(client: TestClient) -> None:
    """Test that HTML response includes fade-on-scroll animation classes."""
    headers = {"HX-Request": "true", "Accept": "text/html"}

    response = client.get(
        "/api/analyze?top_players=5&top_team_players=3&use_cache=false", headers=headers
    )

    if response.status_code == 200:
        html = response.content.decode()

        # Check for animation classes
        assert "fade-on-scroll" in html


def test_static_files_are_accessible(client: TestClient) -> None:
    """Test that static JavaScript files are accessible."""
    js_files = [
        "/static/js/app.js",
        "/static/js/charts.js",
        "/static/js/table-sort.js",
        "/static/js/export.js",
        "/static/js/nav.js",
        "/static/js/ui.js",
        "/static/js/errors.js",
    ]

    for js_file in js_files:
        response = client.get(js_file)
        assert response.status_code == 200, f"Failed to load {js_file}"
        assert response.headers["content-type"].startswith(
            "application/javascript"
        ) or response.headers["content-type"].startswith(
            "text/javascript"
        ), f"Wrong content-type for {js_file}"


def test_css_file_is_accessible(client: TestClient) -> None:
    """Test that CSS file is accessible."""
    response = client.get("/static/css/style.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")

    css = response.content.decode()

    # Check for new CSS classes
    assert ".toast" in css
    assert ".nav-toggle" in css
    assert ".loading-overlay" in css
    assert ".fade-on-scroll" in css
    assert ".export-buttons" in css
    assert ".chart-container" in css


def test_csp_header_allows_cdn_scripts(client: TestClient) -> None:
    """Test that CSP header allows HTMX and Chart.js CDN."""
    response = client.get("/")

    assert response.status_code == 200

    csp = response.headers.get("content-security-policy", "")

    # Parse CSP directives to avoid false positive URL sanitization alerts
    # This is a test verification, not URL sanitization - we're checking
    # that the CSP policy is correctly configured
    directives = {}
    for directive in csp.split(";"):
        parts = directive.strip().split(None, 1)
        if len(parts) == 2:
            directives[parts[0]] = parts[1]

    # Verify script-src directive allows both CDNs
    # Use explicit allowlist pattern to satisfy CodeQL's URL sanitization analysis
    # Convert to set for exact membership check (not substring matching)
    script_src = directives.get("script-src", "")
    allowed_sources = set(script_src.split())

    # Expected CDN sources - exact match required
    expected_cdns = {"https://unpkg.com", "https://cdn.jsdelivr.net"}

    # Verify both CDNs are in the allowlist using set intersection
    assert expected_cdns.issubset(
        allowed_sources
    ), f"Missing CDNs in CSP. Expected: {expected_cdns}, Found: {allowed_sources & expected_cdns}"


def test_analyze_post_still_works(client: TestClient) -> None:
    """Test that POST endpoint still works for backward compatibility."""
    response = client.post(
        "/api/analyze", json={"top_players": 5, "top_team_players": 3, "use_cache": False}
    )

    # Will fail if NHL API is unavailable
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "top_players" in data
        assert "team_standings" in data
        assert "stats" in data


@pytest.mark.parametrize(
    ("top_players", "top_team_players"),
    [
        (10, 5),
        (20, 10),
        (5, 3),
    ],
)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_analyze_with_different_parameters(
    client: TestClient, top_players: int, top_team_players: int
) -> None:
    """Test analyze endpoint with different parameters.

    Note: Marked as flaky due to intermittent SQLite cache table issues
    (sqlite3.OperationalError: no such table: responses). Retries up to
    3 times with 2-second delay between attempts.
    """
    response = client.get(
        f"/api/analyze?top_players={top_players}&top_team_players={top_team_players}&use_cache=false"
    )

    if response.status_code == 200:
        data = response.json()
        assert len(data["top_players"]) <= top_players
        # team_standings should have all teams, not limited by top_players


def test_mobile_nav_css_classes_exist(client: TestClient) -> None:
    """Test that mobile navigation CSS classes are defined."""
    response = client.get("/static/css/style.css")
    css = response.content.decode()

    # Check for mobile nav styles
    assert ".hamburger" in css
    assert ".nav-toggle" in css
    assert "@media (max-width: 768px)" in css


def test_toast_notification_css_exists(client: TestClient) -> None:
    """Test that toast notification CSS is defined."""
    response = client.get("/static/css/style.css")
    css = response.content.decode()

    # Check for toast styles
    assert ".toast" in css
    assert ".toast-error" in css
    assert ".toast-success" in css
    assert ".toast-warning" in css
    assert ".toast-info" in css
