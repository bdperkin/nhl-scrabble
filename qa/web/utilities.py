"""Test utilities and helper functions for Playwright tests."""

import random
import string
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, expect


class AssertionHelpers:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_element_visible(page: Page, selector: str, timeout: int = 10000) -> None:
        """Assert that element is visible.

        Args:
            page: Playwright Page object
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds

        Raises:
            AssertionError: If element is not visible
        """
        expect(page.locator(selector)).to_be_visible(timeout=timeout)

    @staticmethod
    def assert_element_hidden(page: Page, selector: str, timeout: int = 10000) -> None:
        """Assert that element is hidden.

        Args:
            page: Playwright Page object
            selector: CSS selector or text selector
            timeout: Maximum wait time in milliseconds

        Raises:
            AssertionError: If element is visible
        """
        expect(page.locator(selector)).to_be_hidden(timeout=timeout)

    @staticmethod
    def assert_text_contains(page: Page, selector: str, text: str, timeout: int = 10000) -> None:
        """Assert that element contains specific text.

        Args:
            page: Playwright Page object
            selector: CSS selector or text selector
            text: Expected text content
            timeout: Maximum wait time in milliseconds

        Raises:
            AssertionError: If element doesn't contain text
        """
        expect(page.locator(selector)).to_contain_text(text, timeout=timeout)

    @staticmethod
    def assert_url_contains(page: Page, url_part: str, timeout: int = 10000) -> None:
        """Assert that current URL contains specific text.

        Args:
            page: Playwright Page object
            url_part: Expected URL substring
            timeout: Maximum wait time in milliseconds

        Raises:
            AssertionError: If URL doesn't contain expected part
        """
        expect(page).to_have_url(f".*{url_part}.*", timeout=timeout)

    @staticmethod
    def assert_count(page: Page, selector: str, expected_count: int) -> None:
        """Assert that number of elements matches expected count.

        Args:
            page: Playwright Page object
            selector: CSS selector or text selector
            expected_count: Expected number of elements

        Raises:
            AssertionError: If count doesn't match
        """
        expect(page.locator(selector)).to_have_count(expected_count)


class WaitHelpers:
    """Helper methods for waiting operations."""

    @staticmethod
    def wait_for_multiple_selectors(page: Page, selectors: list[str], timeout: int = 10000) -> None:
        """Wait for multiple selectors to appear.

        Args:
            page: Playwright Page object
            selectors: List of CSS selectors to wait for
            timeout: Maximum wait time in milliseconds per selector

        Raises:
            TimeoutError: If any selector doesn't appear within timeout
        """
        for selector in selectors:
            page.wait_for_selector(selector, timeout=timeout)

    @staticmethod
    def wait_for_text(page: Page, text: str, timeout: int = 10000) -> None:
        """Wait for specific text to appear anywhere on page.

        Args:
            page: Playwright Page object
            text: Text to wait for
            timeout: Maximum wait time in milliseconds

        Raises:
            TimeoutError: If text doesn't appear within timeout
        """
        page.wait_for_selector(f"text={text}", timeout=timeout)

    @staticmethod
    def wait_for_navigation(page: Page, action: callable, timeout: int = 30000) -> None:
        """Wait for navigation after performing an action.

        Args:
            page: Playwright Page object
            action: Callable that triggers navigation
            timeout: Maximum wait time in milliseconds

        Example:
            wait_for_navigation(page, lambda: page.click("#submit-btn"))
        """
        with page.expect_navigation(timeout=timeout):
            action()

    @staticmethod
    def wait_for_ajax(page: Page, timeout: int = 10000) -> None:
        """Wait for all AJAX/fetch requests to complete.

        Args:
            page: Playwright Page object
            timeout: Maximum wait time in milliseconds
        """
        page.wait_for_load_state("networkidle", timeout=timeout)


class DataGenerators:
    """Helper methods for generating test data."""

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random alphanumeric string.

        Args:
            length: Length of the string

        Returns:
            Random string
        """
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))  # noqa: S311

    @staticmethod
    def random_email() -> str:
        """Generate a random email address.

        Returns:
            Random email address
        """
        username = DataGenerators.random_string(8)
        domain = DataGenerators.random_string(6)
        return f"{username}@{domain}.com"

    @staticmethod
    def random_number(min_val: int = 0, max_val: int = 100) -> int:
        """Generate a random number within range.

        Args:
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Random integer
        """
        return random.randint(min_val, max_val)  # noqa: S311

    @staticmethod
    def random_team_name() -> str:
        """Generate a random NHL-style team name.

        Returns:
            Random team name
        """
        cities = ["Boston", "Toronto", "Montreal", "New York", "Chicago", "Detroit", "Vegas"]
        mascots = [
            "Bruins",
            "Maple Leafs",
            "Canadiens",
            "Rangers",
            "Blackhawks",
            "Red Wings",
            "Knights",
        ]
        return f"{random.choice(cities)} {random.choice(mascots)}"  # noqa: S311


class ScreenshotHelpers:
    """Helper methods for screenshot operations."""

    @staticmethod
    def capture_page(page: Page, name: str, full_page: bool = False) -> Path:
        """Capture screenshot of current page.

        Args:
            page: Playwright Page object
            name: Screenshot filename (without extension)
            full_page: Capture full scrollable page

        Returns:
            Path to saved screenshot
        """
        screenshot_dir = Path(__file__).parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"{name}.png"
        page.screenshot(path=str(screenshot_path), full_page=full_page)
        return screenshot_path

    @staticmethod
    def capture_element(page: Page, selector: str, name: str) -> Path:
        """Capture screenshot of a specific element.

        Args:
            page: Playwright Page object
            selector: CSS selector of element to capture
            name: Screenshot filename (without extension)

        Returns:
            Path to saved screenshot
        """
        screenshot_dir = Path(__file__).parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"{name}.png"
        page.locator(selector).screenshot(path=str(screenshot_path))
        return screenshot_path

    @staticmethod
    def capture_on_failure(page: Page, test_name: str) -> Path:
        """Capture screenshot when test fails.

        Args:
            page: Playwright Page object
            test_name: Test name for filename

        Returns:
            Path to saved screenshot
        """
        timestamp = DataGenerators.random_string(8)
        filename = f"{test_name}-failure-{timestamp}"
        return ScreenshotHelpers.capture_page(page, filename, full_page=True)


class TableHelpers:
    """Helper methods for interacting with HTML tables."""

    @staticmethod
    def get_table_headers(page: Page, table_selector: str = "table") -> list[str]:
        """Get all column headers from a table.

        Args:
            page: Playwright Page object
            table_selector: CSS selector for table

        Returns:
            List of header texts
        """
        headers = page.locator(f"{table_selector} thead th").all_text_contents()
        return headers

    @staticmethod
    def get_table_row_count(page: Page, table_selector: str = "table") -> int:
        """Get number of rows in table body.

        Args:
            page: Playwright Page object
            table_selector: CSS selector for table

        Returns:
            Number of rows
        """
        return page.locator(f"{table_selector} tbody tr").count()

    @staticmethod
    def get_table_cell(page: Page, row: int, col: int, table_selector: str = "table") -> str:
        """Get cell value from table.

        Args:
            page: Playwright Page object
            row: Row index (0-based)
            col: Column index (0-based)
            table_selector: CSS selector for table

        Returns:
            Cell text content
        """
        cell_selector = f"{table_selector} tbody tr:nth-child({row + 1}) td:nth-child({col + 1})"
        return page.locator(cell_selector).text_content() or ""

    @staticmethod
    def get_table_row(page: Page, row: int, table_selector: str = "table") -> list[str]:
        """Get all cell values from a row.

        Args:
            page: Playwright Page object
            row: Row index (0-based)
            table_selector: CSS selector for table

        Returns:
            List of cell values
        """
        row_selector = f"{table_selector} tbody tr:nth-child({row + 1}) td"
        return page.locator(row_selector).all_text_contents()

    @staticmethod
    def get_table_column(page: Page, col: int, table_selector: str = "table") -> list[str]:
        """Get all values from a column.

        Args:
            page: Playwright Page object
            col: Column index (0-based)
            table_selector: CSS selector for table

        Returns:
            List of column values
        """
        col_selector = f"{table_selector} tbody tr td:nth-child({col + 1})"
        return page.locator(col_selector).all_text_contents()

    @staticmethod
    def find_row_by_text(page: Page, text: str, table_selector: str = "table") -> int:
        """Find row index containing specific text.

        Args:
            page: Playwright Page object
            text: Text to search for
            table_selector: CSS selector for table

        Returns:
            Row index (0-based) or -1 if not found
        """
        rows = page.locator(f"{table_selector} tbody tr").all()
        for i, row in enumerate(rows):
            if text in row.text_content() or "":
                return i
        return -1


# Convenience function to access all helpers
def get_helpers() -> dict[str, Any]:
    """Get all helper classes initialized.

    Returns:
        Dictionary of helper instances
    """
    return {
        "assertions": AssertionHelpers(),
        "waits": WaitHelpers(),
        "data": DataGenerators(),
        "screenshots": ScreenshotHelpers(),
        "tables": TableHelpers(),
    }
