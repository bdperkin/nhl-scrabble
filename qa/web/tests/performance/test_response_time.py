"""Response time performance tests.

Measures API response times and page rendering performance.
"""

import shutil
import time

import pytest

# Skip all tests in this module if Playwright is not available
pytestmark = pytest.mark.skipif(
    shutil.which("playwright") is None,
    reason="Playwright not found (install with: playwright install)",
)

import httpx  # noqa: E402
from pages.index_page import IndexPage  # noqa: E402
from pages.teams_page import TeamsPage  # noqa: E402
from playwright.sync_api import Page  # noqa: E402

# Response time thresholds (in seconds)
API_RESPONSE_THRESHOLD = 1.0
RENDER_TIME_THRESHOLD = 0.5


@pytest.mark.performance
def test_api_homepage_response_time(base_url: str) -> None:
    """Test API response time for homepage endpoint.

    Args:
        base_url: Base URL of the application

    Asserts:
        API response time is under 1 second
    """
    with httpx.Client() as client:
        start = time.time()
        response = client.get(f"{base_url}/")
        duration = time.time() - start

        assert response.status_code == 200, f"Homepage returned status {response.status_code}"
        assert (
            duration < API_RESPONSE_THRESHOLD
        ), f"API response took {duration:.2f}s (threshold: {API_RESPONSE_THRESHOLD}s)"


@pytest.mark.performance
def test_api_teams_response_time(base_url: str) -> None:
    """Test API response time for teams endpoint.

    Args:
        base_url: Base URL of the application

    Asserts:
        API response time is under 1 second
    """
    with httpx.Client() as client:
        start = time.time()
        response = client.get(f"{base_url}/teams")
        duration = time.time() - start

        assert response.status_code == 200, f"Teams page returned status {response.status_code}"
        assert (
            duration < API_RESPONSE_THRESHOLD
        ), f"API response took {duration:.2f}s (threshold: {API_RESPONSE_THRESHOLD}s)"


@pytest.mark.performance
def test_api_stats_response_time(base_url: str) -> None:
    """Test API response time for stats endpoint.

    Args:
        base_url: Base URL of the application

    Asserts:
        API response time is under 1 second
    """
    with httpx.Client() as client:
        start = time.time()
        response = client.get(f"{base_url}/stats")
        duration = time.time() - start

        assert response.status_code == 200, f"Stats page returned status {response.status_code}"
        assert (
            duration < API_RESPONSE_THRESHOLD
        ), f"API response took {duration:.2f}s (threshold: {API_RESPONSE_THRESHOLD}s)"


@pytest.mark.performance
def test_page_render_time(page_fixture: Page, base_url: str) -> None:
    """Test page rendering time after initial load.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page rendering completes quickly after navigation
    """
    page = IndexPage(page_fixture, base_url)
    page.navigate()
    page.wait_for_load()

    # Measure rendering time for navigation
    start = time.time()
    page.navigate_to_teams()
    page_fixture.wait_for_load_state("networkidle")
    duration = time.time() - start

    assert (
        duration < API_RESPONSE_THRESHOLD
    ), f"Navigation/render took {duration:.2f}s (threshold: {API_RESPONSE_THRESHOLD}s)"


@pytest.mark.performance
@pytest.mark.benchmark
def test_api_response_benchmark(base_url: str, benchmark) -> None:
    """Benchmark API response time using pytest-benchmark.

    Args:
        base_url: Base URL of the application
        benchmark: pytest-benchmark fixture

    This test creates a performance baseline for API responses.
    """

    def fetch_homepage() -> None:
        """Fetch the homepage via API."""
        with httpx.Client() as client:
            response = client.get(f"{base_url}/")
            assert response.status_code == 200

    benchmark(fetch_homepage)


@pytest.mark.performance
@pytest.mark.benchmark
def test_navigation_benchmark(page_fixture: Page, base_url: str, benchmark) -> None:
    """Benchmark page navigation time using pytest-benchmark.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application
        benchmark: pytest-benchmark fixture

    This test creates a performance baseline for page navigation.
    """
    page = TeamsPage(page_fixture, base_url)

    # Pre-load page for consistent benchmark
    page.navigate()
    page.wait_for_load()

    def navigate_and_wait() -> None:
        """Navigate to teams page and wait for load."""
        page.navigate()
        page.wait_for_load()

    benchmark(navigate_and_wait)
