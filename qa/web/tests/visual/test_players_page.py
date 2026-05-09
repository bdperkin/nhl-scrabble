"""Visual regression tests for the Players page.

This module contains Playwright-based visual regression tests for the Players ranking page, ensuring
consistent visual appearance across browsers and viewports.

Visual tests run in TEST_MODE with mocked NHL API data for deterministic results.
"""

from collections.abc import Callable

import pytest
from playwright.sync_api import Page


@pytest.mark.visual
def test_players_page_desktop(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of players page on desktop.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently on desktop viewport
        - Screenshot matches baseline
    """
    # Set desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})

    # Navigate to players page
    page.goto(f"{base_url}/players")

    # Wait for content to load
    page.wait_for_selector("#playersTable", state="visible")
    page.wait_for_selector("#playersTable tbody tr", state="visible")
    page.wait_for_selector(".stats-summary .stat-card", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for all browsers due to text rendering variations in large tables
    screenshot = page.screenshot(full_page=True)
    threshold = 0.15
    assert_snapshot(screenshot, "players-desktop.png", threshold=threshold)


@pytest.mark.visual
def test_players_page_mobile(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of players page on mobile.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently on mobile viewport
        - Screenshot matches baseline
        - Mobile layout adapts correctly
    """
    # Set mobile viewport (iPhone 12)
    page.set_viewport_size({"width": 390, "height": 844})

    # Navigate to players page
    page.goto(f"{base_url}/players")

    # Wait for content to load
    page.wait_for_selector("#playersTable", state="visible")
    page.wait_for_selector("#playersTable tbody tr", state="visible")
    page.wait_for_selector(".stats-summary .stat-card", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for all browsers due to text rendering variations in large tables
    screenshot = page.screenshot(full_page=True)
    threshold = 0.15
    assert_snapshot(screenshot, "players-mobile.png", threshold=threshold)


@pytest.mark.visual
def test_players_page_tablet(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of players page on tablet.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently on tablet viewport
        - Screenshot matches baseline
        - Tablet layout adapts correctly
    """
    # Set tablet viewport (iPad)
    page.set_viewport_size({"width": 768, "height": 1024})

    # Navigate to players page
    page.goto(f"{base_url}/players")

    # Wait for content to load
    page.wait_for_selector("#playersTable", state="visible")
    page.wait_for_selector("#playersTable tbody tr", state="visible")
    page.wait_for_selector(".stats-summary .stat-card", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for all browsers due to text rendering variations in large tables
    screenshot = page.screenshot(full_page=True)
    threshold = 0.15
    assert_snapshot(screenshot, "players-tablet.png", threshold=threshold)


@pytest.mark.visual
def test_players_stats_cards(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture screenshot of stats summary cards.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Stats cards render consistently
        - All four stat cards are visible
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/players")

    # Wait for stats cards
    page.wait_for_selector(".stats-summary .stat-card", state="visible")
    page.wait_for_timeout(300)

    # Screenshot just the stats summary section
    stats_element = page.locator(".stats-summary")
    screenshot = stats_element.screenshot()

    # Higher threshold due to stat value rendering
    threshold = 0.25
    assert_snapshot(screenshot, "players-stats-cards.png", threshold=threshold)


@pytest.mark.visual
def test_players_table_header(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture screenshot of players table header.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Table header renders consistently
        - Column headers are properly styled
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/players")

    # Wait for table to load
    page.wait_for_selector("#playersTable thead", state="visible")
    page.wait_for_timeout(300)

    # Screenshot table header
    header_element = page.locator("#playersTable thead")
    screenshot = header_element.screenshot()

    threshold = 0.1
    assert_snapshot(screenshot, "players-table-header.png", threshold=threshold)


@pytest.mark.visual
def test_players_legend_section(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture screenshot of Scrabble letter values legend.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Legend section renders consistently
        - All point values are displayed
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/players")

    # Wait for legend section
    page.wait_for_selector(".legend-section", state="visible")
    page.wait_for_timeout(300)

    # Screenshot legend section
    legend_element = page.locator(".legend-section")
    screenshot = legend_element.screenshot()

    threshold = 0.1
    assert_snapshot(screenshot, "players-legend.png", threshold=threshold)


@pytest.mark.visual
def test_players_export_buttons(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture screenshot of export buttons.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Export buttons render consistently
        - Button styling is correct
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/players")

    # Wait for export buttons
    page.wait_for_selector(".export-buttons", state="visible")
    page.wait_for_timeout(300)

    # Screenshot export buttons section
    buttons_element = page.locator(".export-buttons")
    screenshot = buttons_element.screenshot()

    threshold = 0.1
    assert_snapshot(screenshot, "players-export-buttons.png", threshold=threshold)


@pytest.mark.visual
def test_players_full_page_all_browsers(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Test players page visual consistency across browsers.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently across different browsers
        - Screenshots match baselines for each browser

    Note:
        Browsers are parametrized via command line --browser flags.
        This test will run once per browser (chromium, firefox, webkit).
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/players")

    # Wait for content
    page.wait_for_selector("#playersTable", state="visible")
    page.wait_for_selector("#playersTable tbody tr", state="visible")
    page.wait_for_timeout(500)

    # Take screenshot
    screenshot = page.screenshot(full_page=True)

    # Higher threshold for all browsers due to text rendering variations in large tables
    browser_name = page.context.browser.browser_type.name
    threshold = 0.15

    assert_snapshot(screenshot, f"players-full-{browser_name}.png", threshold=threshold)
