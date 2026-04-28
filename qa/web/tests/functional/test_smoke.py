"""Smoke tests to verify basic functionality and framework setup."""

import pytest
from pages.index_page import IndexPage


@pytest.mark.smoke
def test_framework_setup(index_page: IndexPage) -> None:
    """Verify Playwright framework is set up correctly.

    This is a basic smoke test that checks:
    - Page object can be instantiated
    - Navigation works
    - Basic page interaction works

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to index page
    index_page.navigate()

    # Wait for page to load
    index_page.wait_for_load()

    # Verify we can get the page title
    title = index_page.get_title()
    assert title is not None, "Page title should not be None"

    # Verify page object methods work
    assert index_page.page is not None, "Page object should be initialized"


@pytest.mark.smoke
def test_page_navigation(index_page: IndexPage) -> None:
    """Verify basic page navigation works.

    Tests that we can navigate to the index page and
    verify basic page structure.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to index page
    index_page.navigate()

    # Verify URL is correct
    current_url = index_page.page.url
    assert (
        "localhost:5000" in current_url or index_page.base_url in current_url
    ), "Should be on correct domain"


@pytest.mark.smoke
def test_page_fixtures(
    index_page: IndexPage,
) -> None:
    """Verify all page object fixtures are working.

    Tests that page objects can be instantiated through fixtures
    and are properly configured.

    Args:
        index_page: IndexPage fixture
    """
    # Verify IndexPage fixture
    assert index_page is not None, "IndexPage fixture should work"
    assert index_page.page is not None, "IndexPage should have page object"
    assert index_page.base_url is not None, "IndexPage should have base URL"

    # Verify page methods are accessible
    assert callable(index_page.navigate), "navigate method should be callable"
    assert callable(index_page.get_title), "get_title method should be callable"


@pytest.mark.smoke
def test_playwright_imports() -> None:
    """Verify all required Playwright imports work.

    Tests that the Playwright library is correctly installed and all required modules can be
    imported.
    """
    # Test sync_api imports
    # Test that we can import all page objects
    from pages.base_page import BasePage  # noqa: F401
    from pages.conferences_page import ConferencesPage  # noqa: F401
    from pages.divisions_page import DivisionsPage  # noqa: F401
    from pages.index_page import IndexPage  # noqa: F401
    from pages.playoffs_page import PlayoffsPage  # noqa: F401
    from pages.stats_page import StatsPage  # noqa: F401
    from pages.teams_page import TeamsPage  # noqa: F401
    from playwright.sync_api import Page, expect  # noqa: F401

    # Test utilities import
    from utilities import (  # noqa: F401
        AssertionHelpers,
        DataGenerators,
        ScreenshotHelpers,
        TableHelpers,
        WaitHelpers,
    )

    # If we get here without ImportError, all imports work
    assert True


@pytest.mark.smoke
def test_utilities() -> None:
    """Verify test utilities are working.

    Tests that utility classes can be instantiated and basic methods are accessible.
    """
    from utilities import (
        AssertionHelpers,
        DataGenerators,
        ScreenshotHelpers,
        TableHelpers,
        WaitHelpers,
    )

    # Verify utility classes can be instantiated
    assert AssertionHelpers() is not None
    assert WaitHelpers() is not None
    assert DataGenerators() is not None
    assert ScreenshotHelpers() is not None
    assert TableHelpers() is not None

    # Test data generator methods
    random_str = DataGenerators.random_string(10)
    assert len(random_str) == 10, "Random string should have correct length"

    random_email = DataGenerators.random_email()
    assert "@" in random_email, "Random email should contain @"

    random_num = DataGenerators.random_number(1, 10)
    assert 1 <= random_num <= 10, "Random number should be in range"
