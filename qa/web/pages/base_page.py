"""Base page class with common functionality for all page objects."""

from pathlib import Path
from typing import Literal

from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects.

    Provides common functionality for navigation, waiting, screenshots, and element interactions.
    All page-specific classes should inherit from this base class.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """Initialize the base page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        """Navigate to a URL path.

        Args:
            path: URL path relative to base_url (e.g., "/teams")
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)

    def get_title(self) -> str:
        """Get the page title.

        Returns:
            Page title text
        """
        return self.page.title()

    def wait_for_load(
        self,
        state: Literal["load", "domcontentloaded", "networkidle"] = "networkidle",
    ) -> None:
        """Wait for page to reach a specific load state.

        Args:
            state: Load state to wait for. Options:
                - "load": Page load event fired
                - "domcontentloaded": DOMContentLoaded event fired
                - "networkidle": No network activity for 500ms
        """
        self.page.wait_for_load_state(state)

    def wait_for_selector(self, selector: str, timeout: int = 10000) -> None:
        """Wait for element matching selector to appear.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 10s)
        """
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_url(self, url: str | None = None, timeout: int = 10000) -> None:
        """Wait for URL to match pattern.

        Args:
            url: URL string or regex pattern to match. If None, waits for any URL change.
            timeout: Maximum wait time in milliseconds (default: 10s)
        """
        if url:
            self.page.wait_for_url(url, timeout=timeout)
        else:
            # Wait for any URL change
            current_url = self.page.url
            self.page.wait_for_function(
                f'window.location.href !== "{current_url}"',
                timeout=timeout,
            )

    def screenshot(self, name: str, full_page: bool = False) -> Path:
        """Take a screenshot of the current page.

        Args:
            name: Screenshot filename (without extension)
            full_page: Capture full scrollable page (default: False)

        Returns:
            Path to saved screenshot file
        """
        screenshot_dir = Path(__file__).parent.parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        return screenshot_path

    def click(self, selector: str, timeout: int = 10000) -> None:
        """Click an element matching selector.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 10s)
        """
        self.page.locator(selector).click(timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        """Fill an input element with a value.

        Args:
            selector: CSS selector for input element
            value: Value to fill
            timeout: Maximum wait time in milliseconds (default: 10s)
        """
        self.page.locator(selector).fill(value, timeout=timeout)

    def get_text(self, selector: str, timeout: int = 10000) -> str:
        """Get text content of an element.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 10s)

        Returns:
            Element text content
        """
        return self.page.locator(selector).text_content(timeout=timeout) or ""

    def get_attribute(self, selector: str, attribute: str, timeout: int = 10000) -> str | None:
        """Get attribute value of an element.

        Args:
            selector: CSS selector or text selector
            attribute: Attribute name (e.g., "href", "class")
            timeout: Maximum wait time in milliseconds (default: 10s)

        Returns:
            Attribute value or None if not found
        """
        return self.page.locator(selector).get_attribute(attribute, timeout=timeout)

    def is_visible(self, selector: str, timeout: int = 1000) -> bool:
        """Check if element is visible.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 1s)

        Returns:
            True if element is visible, False otherwise
        """
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except TimeoutError:
            return False

    def is_enabled(self, selector: str, timeout: int = 1000) -> bool:
        """Check if element is enabled.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 1s)

        Returns:
            True if element is enabled, False otherwise
        """
        try:
            return self.page.locator(selector).is_enabled(timeout=timeout)
        except TimeoutError:
            return False

    def count_elements(self, selector: str) -> int:
        """Count number of elements matching selector.

        Args:
            selector: CSS selector or text selector

        Returns:
            Number of matching elements
        """
        return self.page.locator(selector).count()

    def expect_visible(self, selector: str, timeout: int = 10000) -> None:
        """Assert that element is visible.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 10s)

        Raises:
            AssertionError: If element is not visible within timeout
        """
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def expect_hidden(self, selector: str, timeout: int = 10000) -> None:
        """Assert that element is hidden.

        Args:
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds (default: 10s)

        Raises:
            AssertionError: If element is visible within timeout
        """
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)

    def expect_text(self, selector: str, text: str, timeout: int = 10000) -> None:
        """Assert that element contains specific text.

        Args:
            selector: CSS selector or text selector
            text: Expected text content
            timeout: Maximum wait time in milliseconds (default: 10s)

        Raises:
            AssertionError: If element doesn't contain expected text within timeout
        """
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout)

    def expect_url(self, url: str, timeout: int = 10000) -> None:
        """Assert that current URL matches expected pattern.

        Args:
            url: Expected URL or regex pattern
            timeout: Maximum wait time in milliseconds (default: 10s)

        Raises:
            AssertionError: If URL doesn't match within timeout
        """
        expect(self.page).to_have_url(url, timeout=timeout)

    def expect_title(self, title: str, timeout: int = 10000) -> None:
        """Assert that page title matches expected value.

        Args:
            title: Expected title text or regex pattern
            timeout: Maximum wait time in milliseconds (default: 10s)

        Raises:
            AssertionError: If title doesn't match within timeout
        """
        expect(self.page).to_have_title(title, timeout=timeout)
