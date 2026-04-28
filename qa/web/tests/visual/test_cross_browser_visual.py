"""Cross-browser visual regression tests.

Tests ensure visual consistency across different browsers (Chromium, Firefox, WebKit).
Captures screenshots on each browser to detect browser-specific rendering differences.

Note: These tests use pytest-playwright's built-in browser fixtures rather than
manual browser instantiation to avoid parameter conflicts.
"""

from pages.index_page import IndexPage
from pages.teams_page import TeamsPage
from playwright.sync_api import Page, expect


def test_index_page_chromium(index_page: IndexPage) -> None:
    """Test index page rendering in Chromium.

    Verifies consistent rendering of the home page in Chromium browser.

    Args:
        index_page: IndexPage fixture instance
    """
    index_page.navigate()
    index_page.wait_for_load()

    # Browser-specific screenshot
    expect(index_page.page).to_have_screenshot(
        "index-page-chromium.png",
        full_page=True,
    )


def test_teams_page_chromium(teams_page: TeamsPage) -> None:
    """Test teams page rendering in Chromium.

    Verifies consistent table rendering in Chromium browser.

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Browser-specific screenshot
    expect(teams_page.page).to_have_screenshot(
        "teams-page-chromium.png",
        full_page=True,
    )


def test_table_component_chromium(teams_page: TeamsPage) -> None:
    """Test table component rendering in Chromium.

    Verifies consistent table styling in Chromium to detect:
    - Border rendering differences
    - Cell padding variations
    - Font rendering differences
    - Spacing inconsistencies

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Table component screenshot
    table = teams_page.page.locator("table")
    if table.count() > 0:
        expect(table.first).to_have_screenshot("table-component-chromium.png")


def test_responsive_mobile_viewport(page: Page, base_url: str) -> None:
    """Test mobile viewport rendering.

    Verifies mobile rendering with:
    - Mobile viewport (375x667)
    - Touch-optimized layout
    - Responsive design elements

    Args:
        page: Playwright Page fixture
        base_url: Base URL fixture
    """
    # Set mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})

    # Navigate to index page
    index_page = IndexPage(page, base_url)
    index_page.navigate()
    index_page.wait_for_load()

    # Mobile screenshot
    expect(page).to_have_screenshot(
        "index-page-mobile.png",
        full_page=True,
    )


def test_responsive_tablet_viewport(page: Page, base_url: str) -> None:
    """Test tablet viewport rendering.

    Verifies tablet rendering with:
    - Tablet viewport (768x1024)
    - Medium screen layout
    - Responsive breakpoints

    Args:
        page: Playwright Page fixture
        base_url: Base URL fixture
    """
    # Set tablet viewport
    page.set_viewport_size({"width": 768, "height": 1024})

    # Navigate to teams page
    teams_page = TeamsPage(page, base_url)
    teams_page.navigate()
    teams_page.wait_for_load()

    # Tablet screenshot
    expect(page).to_have_screenshot(
        "teams-page-tablet.png",
        full_page=True,
    )
