"""Divisions page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class DivisionsPage(BasePage):
    """Page Object Model for the divisions page.

    Provides methods to interact with division standings and scores.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """Initialize the divisions page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/divisions"

    def navigate(self) -> None:
        """Navigate to the divisions page."""
        super().navigate(self.url)

    def get_page_title(self) -> str:
        """Get the page title/header.

        Returns:
            Page title text
        """
        return self.get_text("h1")

    def get_division_count(self) -> int:
        """Get the number of divisions displayed.

        Returns:
            Number of division sections
        """
        return self.count_elements(".division-section")

    def get_division_name(self, division_index: int = 0) -> str:
        """Get division name from a specific section.

        Args:
            division_index: Zero-based division index

        Returns:
            Division name text
        """
        return self.get_text(f".division-section:nth-child({division_index + 1}) h2")

    def get_division_score(self, division_index: int = 0) -> str:
        """Get division total score.

        Args:
            division_index: Zero-based division index

        Returns:
            Division score text
        """
        return self.get_text(f".division-section:nth-child({division_index + 1}) .division-score")

    def get_teams_in_division(self, division_index: int = 0) -> int:
        """Get the number of teams in a specific division.

        Args:
            division_index: Zero-based division index

        Returns:
            Number of teams in division
        """
        return self.count_elements(
            f".division-section:nth-child({division_index + 1}) table tbody tr",
        )

    def has_division_table(self, division_name: str) -> bool:
        """Check if a division table exists.

        Args:
            division_name: Division name to check

        Returns:
            True if division table is present
        """
        selector = f".division-section:has-text('{division_name}') table"
        return self.is_visible(selector)

    def expand_division(self, division_name: str) -> None:
        """Expand/collapse a division section (if collapsible).

        Args:
            division_name: Division name to expand
        """
        self.click(f".division-section:has-text('{division_name}') .expand-button")

    def get_all_division_names(self) -> list[str]:
        """Get all division names.

        Returns:
            List of division names
        """
        count = self.get_division_count()
        return [self.get_division_name(i) for i in range(count)]

    def has_standings_summary(self) -> bool:
        """Check if standings summary is visible.

        Returns:
            True if summary is present
        """
        return self.is_visible(".standings-summary")
