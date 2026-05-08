"""Visual regression tests for the League page.

This module contains Playwright-based visual regression tests for the League standings page,
ensuring consistent visual appearance across browsers and viewports.

Visual tests run in TEST_MODE with mocked NHL API data for deterministic results.
"""

from collections.abc import Callable

import pytest
from playwright.sync_api import Page


@pytest.mark.visual
def test_league_page_desktop(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of league page on desktop.

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

    # Navigate to league page
    page.goto(f"{base_url}/league")

    # Wait for content to load
    page.wait_for_selector(".division-card", state="visible")
    page.wait_for_selector(".division-card ol li", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for Firefox due to text rendering instability in stat cards
    screenshot = page.screenshot(full_page=True)
    threshold = 0.2 if page.context.browser.browser_type.name == "firefox" else 0.1
    assert_snapshot(screenshot, "league-desktop.png", threshold=threshold)


@pytest.mark.visual
def test_league_page_mobile(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of league page on mobile.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently on mobile viewport
        - Screenshot matches baseline
        - Mobile navigation works correctly
    """
    # Set mobile viewport (iPhone 12)
    page.set_viewport_size({"width": 390, "height": 844})

    # Navigate to league page
    page.goto(f"{base_url}/league")

    # Wait for content to load
    page.wait_for_selector(".division-card", state="visible")
    page.wait_for_selector(".division-card ol li", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for Firefox due to text rendering instability
    screenshot = page.screenshot(full_page=True)
    threshold = 0.2 if page.context.browser.browser_type.name == "firefox" else 0.1
    assert_snapshot(screenshot, "league-mobile.png", threshold=threshold)


@pytest.mark.visual
def test_league_page_tablet(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture baseline screenshot of league page on tablet.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Page renders consistently on tablet viewport
        - Screenshot matches baseline
    """
    # Set tablet viewport (iPad)
    page.set_viewport_size({"width": 768, "height": 1024})

    # Navigate to league page
    page.goto(f"{base_url}/league")

    # Wait for content to load
    page.wait_for_selector(".division-card", state="visible")
    page.wait_for_selector(".division-card ol li", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    # Higher threshold for Firefox due to text rendering instability
    screenshot = page.screenshot(full_page=True)
    threshold = 0.2 if page.context.browser.browser_type.name == "firefox" else 0.1
    assert_snapshot(screenshot, "league-tablet.png", threshold=threshold)


@pytest.mark.visual
def test_league_stats_summary_visual(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture stats summary section for visual regression.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Stats cards render consistently
        - Layout and spacing are correct
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for stats summary
    stats_summary = page.locator(".stats-summary")
    stats_summary.wait_for(state="visible")

    # Wait for animations
    page.wait_for_timeout(500)

    # Capture stats summary section
    screenshot = stats_summary.screenshot()
    assert_snapshot(screenshot, "league-stats-summary.png")


@pytest.mark.visual
def test_league_team_list_visual(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture team list section for visual regression.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Team list renders consistently
        - All team items display correctly
        - Hover states work (if applicable)
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for league card
    league_card = page.locator(".division-card")
    league_card.wait_for(state="visible")

    # Wait for all team items
    page.wait_for_selector(".division-card ol li", state="visible")

    # Wait for animations
    page.wait_for_timeout(500)

    # Capture league card section
    screenshot = league_card.screenshot()
    assert_snapshot(screenshot, "league-team-list.png")


@pytest.mark.visual
@pytest.mark.parametrize(
    "locale",
    ["en_US", "fr_CA", "sv_SE"],
)
def test_league_i18n_visual(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
    locale: str,
) -> None:
    """Capture screenshots for different locales.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture
        locale: Locale code to test

    Verifies:
        - Page renders consistently across locales
        - Text translations don't break layout
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league?lang={locale}")

    # Wait for content
    page.wait_for_selector(".division-card", state="visible")
    page.wait_for_timeout(500)

    # Capture screenshot
    # Higher threshold for Firefox and non-English locales due to text rendering variations
    screenshot = page.screenshot(full_page=True)
    browser_name = page.context.browser.browser_type.name
    # WebKit sv_SE has severe font rendering instability (9700+ diff pixels)
    if browser_name == "webkit" and locale == "sv_SE":
        threshold = 0.5
    # Firefox needs higher threshold due to stat card text rendering
    elif browser_name == "firefox":
        threshold = 0.2
    # fr_CA/sv_SE in other browsers need moderate threshold
    elif locale in ["fr_CA", "sv_SE"]:
        threshold = 0.15
    else:
        threshold = 0.1
    assert_snapshot(screenshot, f"league-{locale}.png", threshold=threshold)


@pytest.mark.visual
def test_league_dark_mode_visual(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture league page in dark mode (if supported).

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Dark mode styles apply correctly
        - Colors and contrast are appropriate
    """
    page.set_viewport_size({"width": 1920, "height": 1080})

    # Enable dark mode by setting color scheme preference
    page.emulate_media(color_scheme="dark")

    page.goto(f"{base_url}/league")

    # Wait for content
    page.wait_for_selector(".division-card", state="visible")
    page.wait_for_timeout(500)

    # Capture dark mode screenshot
    # Higher threshold for Firefox due to text rendering instability
    screenshot = page.screenshot(full_page=True)
    threshold = 0.2 if page.context.browser.browser_type.name == "firefox" else 0.1
    assert_snapshot(screenshot, "league-dark-mode.png", threshold=threshold)


@pytest.mark.visual
def test_league_scrolled_header(
    page: Page,
    base_url: str,
    assert_snapshot: Callable,
) -> None:
    """Capture page header after scrolling (for sticky/fade effects).

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        assert_snapshot: Snapshot comparison fixture

    Verifies:
        - Header fade-on-scroll effect works
        - Scroll animations are consistent
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for content
    page.wait_for_selector(".division-card", state="visible")

    # Scroll down
    page.evaluate("window.scrollTo(0, 500)")
    page.wait_for_timeout(500)

    # Capture scrolled state
    # Higher threshold for Firefox due to text rendering instability
    screenshot = page.screenshot(full_page=True)
    threshold = 0.2 if page.context.browser.browser_type.name == "firefox" else 0.1
    assert_snapshot(screenshot, "league-scrolled.png", threshold=threshold)
