"""Functional tests for route navigation.

Tests verify that users can navigate to all pages via browser and that pages render correctly.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.functional
def test_home_page_accessible(page: Page, base_url: str) -> None:
    """Test home page is accessible via browser.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    page.goto(base_url)

    # Should see HTML page, not JSON error
    expect(page.locator("html")).to_be_visible()

    # Should not see JSON error
    content = page.content()
    assert '{"detail"' not in content


@pytest.mark.functional
def test_all_page_routes_accessible(page: Page, base_url: str) -> None:
    """Test all page routes are accessible via browser.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

    for route in routes:
        page.goto(f"{base_url}{route}")

        # Should render HTML page
        expect(page.locator("html")).to_be_visible()

        # Should not see JSON error
        content = page.content()
        assert '{"detail"' not in content, f"Route {route} returned JSON error"

        # Should have proper page structure
        expect(page.locator("body")).to_be_visible()


@pytest.mark.functional
def test_navigation_between_pages(page: Page, base_url: str) -> None:
    """Test user can navigate between pages.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    page.goto(base_url)

    # Navigate to teams page
    page.goto(f"{base_url}/teams")
    expect(page.locator("html")).to_be_visible()

    # Navigate to divisions page
    page.goto(f"{base_url}/divisions")
    expect(page.locator("html")).to_be_visible()

    # Navigate back to home
    page.goto(base_url)
    expect(page.locator("html")).to_be_visible()


@pytest.mark.functional
def test_favicon_loads(page: Page, base_url: str) -> None:
    """Test favicon is accessible.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    response = page.request.get(f"{base_url}/favicon.svg")
    assert response.ok
    assert "image/svg" in response.headers["content-type"]


@pytest.mark.functional
def test_robots_txt_accessible(page: Page, base_url: str) -> None:
    """Test robots.txt is accessible.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    response = page.request.get(f"{base_url}/robots.txt")
    assert response.ok
    assert "text/plain" in response.headers["content-type"]
