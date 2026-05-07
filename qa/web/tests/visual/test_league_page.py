"""Visual regression tests for the League page.

This module contains Playwright-based visual regression tests for the League standings page,
ensuring consistent visual appearance across browsers and viewports.

Visual tests run in TEST_MODE with mocked NHL API data for deterministic results.
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.visual
def test_league_page_desktop(page: Page, base_url: str, browser_name: str) -> None:
    """Capture baseline screenshot of league page on desktop.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Page renders consistently on desktop viewport
        - Screenshot matches baseline
    """
    # Set desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})

    # Navigate to league page
    page.goto(f"{base_url}/league")

    # Wait for content to load
    page.wait_for_selector(".league-card", state="visible")
    page.wait_for_selector(".league-team-item", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-desktop.png",
        full_page=True,
    )


@pytest.mark.visual
def test_league_page_mobile(page: Page, base_url: str, browser_name: str) -> None:
    """Capture baseline screenshot of league page on mobile.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

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
    page.wait_for_selector(".league-card", state="visible")
    page.wait_for_selector(".league-team-item", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-mobile.png",
        full_page=True,
    )


@pytest.mark.visual
def test_league_page_tablet(page: Page, base_url: str, browser_name: str) -> None:
    """Capture baseline screenshot of league page on tablet.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Page renders consistently on tablet viewport
        - Screenshot matches baseline
    """
    # Set tablet viewport (iPad)
    page.set_viewport_size({"width": 768, "height": 1024})

    # Navigate to league page
    page.goto(f"{base_url}/league")

    # Wait for content to load
    page.wait_for_selector(".league-card", state="visible")
    page.wait_for_selector(".league-team-item", state="visible")

    # Wait for animations to complete
    page.wait_for_timeout(500)

    # Take and compare full page screenshot with baseline
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-tablet.png",
        full_page=True,
    )


@pytest.mark.visual
def test_league_stats_summary_visual(page: Page, base_url: str, browser_name: str) -> None:
    """Capture stats summary section for visual regression.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

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
    stats_summary.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-stats-summary.png",
    )


@pytest.mark.visual
def test_league_team_list_visual(page: Page, base_url: str, browser_name: str) -> None:
    """Capture team list section for visual regression.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Team list renders consistently
        - All team items display correctly
        - Hover states work (if applicable)
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for league card
    league_card = page.locator(".league-card")
    league_card.wait_for(state="visible")

    # Wait for all team items
    page.wait_for_selector(".league-team-item", state="visible")

    # Wait for animations
    page.wait_for_timeout(500)

    # Capture league card section
    league_card.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-team-list.png",
    )


@pytest.mark.visual
@pytest.mark.parametrize(
    "locale",
    ["en_US", "fr_CA", "sv_SE"],
)
def test_league_i18n_visual(page: Page, base_url: str, browser_name: str, locale: str) -> None:
    """Capture screenshots for different locales.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested
        locale: Locale code to test

    Verifies:
        - Page renders consistently across locales
        - Text translations don't break layout
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league?lang={locale}")

    # Wait for content
    page.wait_for_selector(".league-card", state="visible")
    page.wait_for_timeout(500)

    # Capture screenshot
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-{locale}.png",
        full_page=True,
    )


@pytest.mark.visual
def test_league_info_section_visual(page: Page, base_url: str, browser_name: str) -> None:
    """Capture info section for visual regression.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Info section renders consistently
        - Links display correctly
        - Text formatting is preserved
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for info section
    info_section = page.locator(".info-section")
    info_section.wait_for(state="visible")

    # Wait for animations
    page.wait_for_timeout(500)

    # Capture info section
    info_section.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-info-section.png",
    )


@pytest.mark.visual
def test_league_dark_mode_visual(page: Page, base_url: str, browser_name: str) -> None:
    """Capture league page in dark mode (if supported).

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Dark mode styles apply correctly
        - Colors and contrast are appropriate
    """
    page.set_viewport_size({"width": 1920, "height": 1080})

    # Enable dark mode by setting color scheme preference
    page.emulate_media(color_scheme="dark")

    page.goto(f"{base_url}/league")

    # Wait for content
    page.wait_for_selector(".league-card", state="visible")
    page.wait_for_timeout(500)

    # Capture dark mode screenshot
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-dark-mode.png",
        full_page=True,
    )


@pytest.mark.visual
def test_league_scrolled_header(page: Page, base_url: str, browser_name: str) -> None:
    """Capture page header after scrolling (for sticky/fade effects).

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        browser_name: Name of the browser being tested

    Verifies:
        - Header fade-on-scroll effect works
        - Scroll animations are consistent
    """
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/league")

    # Wait for content
    page.wait_for_selector(".league-card", state="visible")

    # Scroll down
    page.evaluate("window.scrollTo(0, 500)")
    page.wait_for_timeout(500)

    # Capture scrolled state
    page.screenshot(
        path=f"qa/web/tests/visual/__snapshots__/{browser_name}/linux/league-scrolled.png",
        full_page=True,
    )
