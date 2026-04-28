"""Pytest configuration for visual regression tests.

Provides fixtures and configuration specific to visual testing:
- Screenshot comparison settings
- Baseline management
- Diff threshold configuration
"""

from collections.abc import Generator
from typing import Any

import pytest
from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage
from playwright.sync_api import Page


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
