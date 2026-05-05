"""Pytest configuration for visual regression tests.

Provides fixtures and configuration specific to visual testing:
- Screenshot comparison settings
- Baseline management
- Diff threshold configuration
- Mocked NHL API data for deterministic tests
"""

import json
import sys
from collections.abc import Callable, Generator
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import Page


@pytest.fixture
def assert_snapshot(pytestconfig: Any, request: Any, browser_name: str) -> Callable:
    """Enhanced snapshot comparison fixture that saves diff images on failure.

    This fixture overrides pytest-playwright-snapshot's assert_snapshot to add
    visual diff generation when snapshots don't match. When a test fails, it saves:
    - actual.png: The screenshot that was captured
    - baseline.png: The expected baseline screenshot
    - diff.png: Visual diff highlighting pixel differences in red

    Files are saved to test-results/{test_name}/ for artifact upload.

    Args:
        pytestconfig: Pytest config object
        request: Pytest request object
        browser_name: Name of the browser being tested

    Returns:
        Comparison function that asserts snapshot matches and saves diffs on failure
    """

    def compare(img: bytes, name: str, *, threshold: float = 0.1) -> None:
        """Compare screenshot to baseline, generating diff images on failure.

        Args:
            img: Screenshot bytes to compare
            name: Snapshot filename
            threshold: Pixel difference threshold (0.0-1.0)

        Raises:
            pytest.fail: If baseline doesn't exist
            AssertionError: If snapshots don't match
        """
        update_snapshot = pytestconfig.getoption("--update-snapshots")

        # Determine snapshot path (matches pytest-playwright-snapshot behavior)
        filepath = (
            Path(request.node.fspath).parent.resolve()
            / "__snapshots__"
            / browser_name
            / sys.platform
        )
        filepath.mkdir(parents=True, exist_ok=True)
        file = filepath / name

        # Update mode: save new baseline
        if update_snapshot:
            file.write_bytes(img)
            return

        # Baseline doesn't exist
        if not file.exists():
            pytest.fail(f"Snapshot not found: {file}, use --update-snapshots to create it.")

        # Load images for comparison
        actual_image = Image.open(BytesIO(img))
        baseline_image = Image.open(file)

        # Create diff image (same size as actual)
        diff_image = Image.new("RGBA", actual_image.size)

        # Compare images using pixelmatch
        diff_pixels = pixelmatch(
            actual_image,
            baseline_image,
            diff_image,
            threshold=threshold,
        )

        # If snapshots match, we're done
        if diff_pixels == 0:
            return

        # Snapshots don't match - save diagnostic images for debugging
        test_name = request.node.name.replace("[", "-").replace("]", "")
        result_dir = Path("reports") / "visual-diffs" / browser_name / test_name
        result_dir.mkdir(parents=True, exist_ok=True)

        # Debug: Print absolute paths
        cwd = Path.cwd()
        abs_result_dir = result_dir.resolve()
        print("\n🔍 DEBUG: Saving diff images")
        print(f"  CWD: {cwd}")
        print(f"  Relative result_dir: {result_dir}")
        print(f"  Absolute result_dir: {abs_result_dir}")
        print(f"  Directory exists: {abs_result_dir.exists()}")

        # Save actual screenshot (what the test captured)
        actual_path = result_dir / name.replace(".png", "-actual.png")
        actual_path.write_bytes(img)
        print(f"  Wrote actual: {actual_path.resolve()} (exists: {actual_path.exists()})")

        # Save baseline for easy comparison
        baseline_path = result_dir / name.replace(".png", "-baseline.png")
        baseline_image.save(baseline_path)
        print(f"  Wrote baseline: {baseline_path.resolve()} (exists: {baseline_path.exists()})")

        # Save diff image (highlights differences)
        diff_path = result_dir / name.replace(".png", "-diff.png")
        diff_image.save(diff_path)
        print(f"  Wrote diff: {diff_path.resolve()} (exists: {diff_path.exists()})")

        # List all files in result_dir
        if abs_result_dir.exists():
            files = list(abs_result_dir.glob("*"))
            print(f"  Files in directory: {[f.name for f in files]}")

        # Fail with detailed diagnostic info
        pytest.fail(
            f"Snapshots does not match\n"
            f"  Diff pixels: {diff_pixels}\n"
            f"  Threshold: {threshold}\n"
            f"  Actual: {actual_path}\n"
            f"  Baseline: {baseline_path}\n"
            f"  Diff: {diff_path}",
        )

    return compare


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, Any]:
    """Return browser launch arguments for visual tests.

    Returns:
        Browser launch configuration optimized for visual testing
    """
    return {
        "headless": True,  # Run in headless mode for CI
        "slow_mo": 0,  # No artificial delays
    }


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, Any]:
    """Return browser context arguments for visual tests.

    Returns:
        Browser context configuration for consistent screenshots
    """
    return {
        "viewport": {"width": 1920, "height": 1080},  # Desktop viewport
        "device_scale_factor": 1,  # Standard DPI
        "ignore_https_errors": True,
        "has_touch": False,  # Desktop mode
        "is_mobile": False,
        "locale": "en-US",  # Consistent locale
        "timezone_id": "America/New_York",  # Consistent timezone
    }


@pytest.fixture
def visual_page(page: Page) -> Generator[Page, None, None]:
    """Enhanced page fixture for visual testing.

    Configures page with settings optimized for consistent screenshots:
    - Disables animations
    - Sets consistent timeouts
    - Waits for fonts to load

    Args:
        page: Playwright Page object from pytest-playwright

    Yields:
        Configured Page object for visual testing
    """
    # Disable animations for consistent screenshots
    page.add_init_script("""
        // Disable CSS animations and transitions
        const style = document.createElement('style');
        style.innerHTML = `
            *, *::before, *::after {
                animation-duration: 0s !important;
                animation-delay: 0s !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
            }
        `;
        document.head.appendChild(style);

        // Wait for fonts to fully load and metrics to stabilize
        document.fonts.ready.then(() => {
            console.log('Fonts loaded');
        });
    """)

    # Set default timeout
    page.set_default_timeout(30000)

    # Set default navigation timeout
    page.set_default_navigation_timeout(30000)

    yield page


def pytest_configure(config):
    """Configure pytest for visual testing.

    Adds custom markers for visual tests:
    - visual: Mark test as visual regression test
    - cross_browser: Mark test as cross-browser visual test

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers",
        "visual: Mark test as visual regression test",
    )
    config.addinivalue_line(
        "markers",
        "cross_browser: Mark test as cross-browser visual test",
    )


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the application under test."""
    return "http://localhost:5000"


@pytest.fixture
def page_fixture(page: Page) -> Page:
    """Enhanced page fixture with common setup and teardown.

    Args:
        page: Playwright Page object from pytest-playwright

    Returns:
        Configured Page object
    """
    # Set default timeout to 10 seconds
    page.set_default_timeout(10000)

    # Set default navigation timeout to 30 seconds
    page.set_default_navigation_timeout(30000)

    return page


@pytest.fixture
def index_page(page_fixture: Page, base_url: str) -> IndexPage:
    """Fixture providing an IndexPage instance."""
    return IndexPage(page_fixture, base_url)


@pytest.fixture
def teams_page(page_fixture: Page, base_url: str) -> TeamsPage:
    """Fixture providing a TeamsPage instance."""
    return TeamsPage(page_fixture, base_url)


@pytest.fixture
def divisions_page(page_fixture: Page, base_url: str) -> DivisionsPage:
    """Fixture providing a DivisionsPage instance."""
    return DivisionsPage(page_fixture, base_url)


@pytest.fixture
def conferences_page(page_fixture: Page, base_url: str) -> ConferencesPage:
    """Fixture providing a ConferencesPage instance."""
    return ConferencesPage(page_fixture, base_url)


@pytest.fixture
def playoffs_page(page_fixture: Page, base_url: str) -> PlayoffsPage:
    """Fixture providing a PlayoffsPage instance."""
    return PlayoffsPage(page_fixture, base_url)


@pytest.fixture
def stats_page(page_fixture: Page, base_url: str) -> StatsPage:
    """Fixture providing a StatsPage instance."""
    return StatsPage(page_fixture, base_url)


# ============================================================================
# NHL API Mocking for Visual Tests
# ============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def nhl_standings_data() -> dict[str, Any]:
    """Load NHL standings fixture data.

    Returns:
        Standings data from fixtures/nhl_standings.json
    """
    fixture_file = FIXTURES_DIR / "nhl_standings.json"
    with open(fixture_file) as f:
        return json.load(f)  # type: ignore[no-any-return]


@pytest.fixture(scope="session")
def nhl_rosters_data() -> dict[str, Any]:
    """Load NHL rosters fixture data.

    Returns:
        Rosters data from fixtures/nhl_rosters.json
    """
    fixture_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(fixture_file) as f:
        return json.load(f)  # type: ignore[no-any-return]


@pytest.fixture(autouse=True)
def mock_nhl_api_client(
    nhl_standings_data: dict[str, Any],
    nhl_rosters_data: dict[str, Any],
) -> Generator[MagicMock, None, None]:
    """Mock NHLApiClient with fixed fixture data for visual tests.

    This fixture automatically applies to all visual tests (autouse=True),
    ensuring deterministic API responses for consistent screenshots.

    The mock client returns fixture data instead of making real API calls,
    which ensures:
    - Consistent data across test runs
    - Fast test execution (no network calls)
    - Reliable baselines regardless of live NHL data changes

    Args:
        nhl_standings_data: Standings fixture data
        nhl_rosters_data: Rosters fixture data

    Yields:
        Mocked NHLApiClient instance configured with fixture data
    """
    # Create mock client instance
    mock_client_instance = MagicMock()

    # Configure get_teams() to return teams from standings
    def mock_get_teams(season: str | None = None) -> dict[str, dict[str, str]]:
        """Extract teams from standings fixture data."""
        teams_info: dict[str, dict[str, str]] = {}
        for team in nhl_standings_data["standings"]:
            team_abbrev = team["teamAbbrev"]["default"]
            team_name = team.get("teamName", {}).get("default", team_abbrev)
            teams_info[team_abbrev] = {
                "name": team_name,
                "division": team.get("divisionName", "Unknown"),
                "conference": team.get("conferenceName", "Unknown"),
            }
        return teams_info

    mock_client_instance.get_teams.side_effect = mock_get_teams

    # Configure get_team_roster() to return roster from fixtures
    def mock_get_team_roster(
        team_abbrev: str,
        season: str | None = None,
    ) -> dict[str, Any]:
        """Return roster from fixture data."""
        if team_abbrev not in nhl_rosters_data:
            # Return empty roster if team not found (shouldn't happen with valid fixtures)
            return {"forwards": [], "defensemen": [], "goalies": []}
        return nhl_rosters_data[team_abbrev]

    mock_client_instance.get_team_roster.side_effect = mock_get_team_roster

    # Mock context manager methods
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None

    # Patch NHLApiClient class to return our mock instance
    # This patches at the source (nhl_scrabble.api.nhl_client), so all imports get the mock
    with patch("nhl_scrabble.api.nhl_client.NHLApiClient", return_value=mock_client_instance):
        yield mock_client_instance
