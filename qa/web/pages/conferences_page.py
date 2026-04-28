"""Conferences page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class ConferencesPage(BasePage):
    """Page Object Model for the conferences page.

    Provides methods to interact with conference standings and scores.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """Initialize the conferences page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/conferences"

    def navigate(self) -> None:
        """Navigate to the conferences page."""
        super().navigate(self.url)

    def get_page_title(self) -> str:
        """Get the page title/header.

        Returns:
            Page title text
        """
        return self.get_text("h1")

    def get_conference_count(self) -> int:
        """Get the number of conferences displayed.

        Returns:
            Number of conference sections (should be 2: Eastern, Western)
        """
        return self.count_elements(".conference-section")

    def get_conference_name(self, conference_index: int = 0) -> str:
        """Get conference name from a specific section.

        Args:
            conference_index: Zero-based conference index (0=Eastern, 1=Western)

        Returns:
            Conference name text
        """
        return self.get_text(f".conference-section:nth-child({conference_index + 1}) h2")

    def get_conference_score(self, conference_index: int = 0) -> str:
        """Get conference total score.

        Args:
            conference_index: Zero-based conference index

        Returns:
            Conference score text
        """
        return self.get_text(
            f".conference-section:nth-child({conference_index + 1}) .conference-score"
        )

    def get_teams_in_conference(self, conference_index: int = 0) -> int:
        """Get the number of teams in a specific conference.

        Args:
            conference_index: Zero-based conference index

        Returns:
            Number of teams in conference
        """
        return self.count_elements(
            f".conference-section:nth-child({conference_index + 1}) table tbody tr"
        )

    def has_conference_table(self, conference_name: str) -> bool:
        """Check if a conference table exists.

        Args:
            conference_name: Conference name to check (e.g., "Eastern", "Western")

        Returns:
            True if conference table is present
        """
        selector = f".conference-section:has-text('{conference_name}') table"
        return self.is_visible(selector)

    def expand_conference(self, conference_name: str) -> None:
        """Expand/collapse a conference section (if collapsible).

        Args:
            conference_name: Conference name to expand
        """
        self.click(f".conference-section:has-text('{conference_name}') .expand-button")

    def get_all_conference_names(self) -> list[str]:
        """Get all conference names.

        Returns:
            List of conference names (typically ["Eastern Conference", "Western Conference"])
        """
        count = self.get_conference_count()
        return [self.get_conference_name(i) for i in range(count)]

    def has_wild_card_section(self) -> bool:
        """Check if wild card standings section is visible.

        Returns:
            True if wild card section is present
        """
        return self.is_visible(".wild-card-section")

    def get_wild_card_teams(self) -> int:
        """Get the number of wild card teams shown.

        Returns:
            Number of wild card teams
        """
        return self.count_elements(".wild-card-section table tbody tr")
