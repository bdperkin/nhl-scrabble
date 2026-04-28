"""Index/Home page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class IndexPage(BasePage):
    """
    Page Object Model for the index/home page.

    Provides methods to interact with the home page elements
    and navigate to other sections of the application.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """
        Initialize the index page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/"

    def navigate(self) -> None:
        """Navigate to the index/home page."""
        super().navigate(self.url)

    def get_welcome_message(self) -> str:
        """
        Get the welcome/header message from the page.

        Returns:
            Welcome message text
        """
        return self.get_text("h1")

    def click_analyze_button(self) -> None:
        """Click the analyze/run button if present."""
        self.click("#analyze-button")

    def has_teams_link(self) -> bool:
        """
        Check if teams navigation link is visible.

        Returns:
            True if teams link is visible
        """
        return self.is_visible('a[href="/teams"]')

    def has_divisions_link(self) -> bool:
        """
        Check if divisions navigation link is visible.

        Returns:
            True if divisions link is visible
        """
        return self.is_visible('a[href="/divisions"]')

    def has_conferences_link(self) -> bool:
        """
        Check if conferences navigation link is visible.

        Returns:
            True if conferences link is visible
        """
        return self.is_visible('a[href="/conferences"]')

    def has_playoffs_link(self) -> bool:
        """
        Check if playoffs navigation link is visible.

        Returns:
            True if playoffs link is visible
        """
        return self.is_visible('a[href="/playoffs"]')

    def has_stats_link(self) -> bool:
        """
        Check if stats navigation link is visible.

        Returns:
            True if stats link is visible
        """
        return self.is_visible('a[href="/stats"]')

    def navigate_to_teams(self) -> None:
        """Navigate to the teams page."""
        self.click('a[href="/teams"]')

    def navigate_to_divisions(self) -> None:
        """Navigate to the divisions page."""
        self.click('a[href="/divisions"]')

    def navigate_to_conferences(self) -> None:
        """Navigate to the conferences page."""
        self.click('a[href="/conferences"]')

    def navigate_to_playoffs(self) -> None:
        """Navigate to the playoffs page."""
        self.click('a[href="/playoffs"]')

    def navigate_to_stats(self) -> None:
        """Navigate to the stats page."""
        self.click('a[href="/stats"]')
