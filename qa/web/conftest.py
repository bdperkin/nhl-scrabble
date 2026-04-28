"""Pytest configuration and shared fixtures for web automation tests."""

from collections.abc import Generator
from typing import Any

import pytest
from pages.base_page import BasePage
from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, Any]:
    """Return browser launch arguments."""
    return {
        "headless": True,
        "slow_mo": 0,
    }


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, Any]:
    """Return browser context arguments."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the application under test."""
    return "http://localhost:5000"


@pytest.fixture
def page_fixture(page: Page) -> Generator[Page, None, None]:
    """Enhanced page fixture with common setup and teardown.

    Sets default timeout and handles cleanup after test.

    Args:
        page: Playwright Page object from pytest-playwright

    Yields:
        Configured Page object
    """
    # Set default timeout to 10 seconds
    page.set_default_timeout(10000)

    # Set default navigation timeout to 30 seconds
    page.set_default_navigation_timeout(30000)

    return page

    # Cleanup after test (page is automatically closed by pytest-playwright)


@pytest.fixture
def base_page(page_fixture: Page, base_url: str) -> BasePage:
    """Fixture providing a BasePage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        BasePage instance
    """
    return BasePage(page_fixture, base_url)


@pytest.fixture
def index_page(page_fixture: Page, base_url: str) -> IndexPage:
    """Fixture providing an IndexPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        IndexPage instance
    """
    return IndexPage(page_fixture, base_url)


@pytest.fixture
def teams_page(page_fixture: Page, base_url: str) -> TeamsPage:
    """Fixture providing a TeamsPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        TeamsPage instance
    """
    return TeamsPage(page_fixture, base_url)


@pytest.fixture
def divisions_page(page_fixture: Page, base_url: str) -> DivisionsPage:
    """Fixture providing a DivisionsPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        DivisionsPage instance
    """
    return DivisionsPage(page_fixture, base_url)


@pytest.fixture
def conferences_page(page_fixture: Page, base_url: str) -> ConferencesPage:
    """Fixture providing a ConferencesPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        ConferencesPage instance
    """
    return ConferencesPage(page_fixture, base_url)


@pytest.fixture
def playoffs_page(page_fixture: Page, base_url: str) -> PlayoffsPage:
    """Fixture providing a PlayoffsPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        PlayoffsPage instance
    """
    return PlayoffsPage(page_fixture, base_url)


@pytest.fixture
def stats_page(page_fixture: Page, base_url: str) -> StatsPage:
    """Fixture providing a StatsPage instance.

    Args:
        page_fixture: Configured Playwright Page
        base_url: Base URL of the application

    Returns:
        StatsPage instance
    """
    return StatsPage(page_fixture, base_url)
