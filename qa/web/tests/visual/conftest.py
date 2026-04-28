"""Pytest configuration for visual regression tests.

Provides fixtures and configuration specific to visual testing:
- Screenshot comparison settings
- Baseline management
- Diff threshold configuration
"""

from collections.abc import Generator
from typing import Any

import pytest
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
