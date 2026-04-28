"""Page load performance tests.

Measures page load times and ensures they meet performance thresholds.
"""

import time

import pytest
from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage
from playwright.sync_api import Page

# Performance thresholds (in seconds)
PAGE_LOAD_THRESHOLD = 2.0
FAST_PAGE_THRESHOLD = 1.0


@pytest.mark.performance
def test_homepage_load_time(page_fixture: Page, base_url: str) -> None:
    """Test homepage loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = IndexPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Homepage loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
def test_teams_page_load_time(page_fixture: Page, base_url: str) -> None:
    """Test teams page loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = TeamsPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Teams page loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
def test_divisions_page_load_time(page_fixture: Page, base_url: str) -> None:
    """Test divisions page loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = DivisionsPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Divisions page loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
def test_conferences_page_load_time(page_fixture: Page, base_url: str) -> None:
    """Test conferences page loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = ConferencesPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Conferences page loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
def test_playoffs_page_load_time(page_fixture: Page, base_url: str) -> None:
    """Test playoffs page loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = PlayoffsPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Playoffs page loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
def test_stats_page_load_time(page_fixture: Page, base_url: str) -> None:
    """Test stats page loads within acceptable time.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application

    Asserts:
        Page load time is under 2 seconds
    """
    page = StatsPage(page_fixture, base_url)

    start = time.time()
    page.navigate()
    page.wait_for_load()
    duration = time.time() - start

    assert (
        duration < PAGE_LOAD_THRESHOLD
    ), f"Stats page loaded in {duration:.2f}s (threshold: {PAGE_LOAD_THRESHOLD}s)"


@pytest.mark.performance
@pytest.mark.benchmark
def test_homepage_load_benchmark(page_fixture: Page, base_url: str, benchmark) -> None:
    """Benchmark homepage load time using pytest-benchmark.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application
        benchmark: pytest-benchmark fixture

    This test creates a performance baseline for homepage loading.
    """
    page = IndexPage(page_fixture, base_url)

    def load_page() -> None:
        """Load the homepage."""
        page.navigate()
        page.wait_for_load()

    benchmark(load_page)


@pytest.mark.performance
@pytest.mark.benchmark
def test_teams_page_load_benchmark(page_fixture: Page, base_url: str, benchmark) -> None:
    """Benchmark teams page load time using pytest-benchmark.

    Args:
        page_fixture: Playwright Page fixture
        base_url: Base URL of the application
        benchmark: pytest-benchmark fixture

    This test creates a performance baseline for teams page loading.
    """
    page = TeamsPage(page_fixture, base_url)

    def load_page() -> None:
        """Load the teams page."""
        page.navigate()
        page.wait_for_load()

    benchmark(load_page)
