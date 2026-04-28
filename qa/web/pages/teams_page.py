"""Teams page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class TeamsPage(BasePage):
    """
    Page Object Model for the teams page.

    Provides methods to interact with team standings, scores,
    and team-specific information.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """
        Initialize the teams page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/teams"

    def navigate(self) -> None:
        """Navigate to the teams page."""
        super().navigate(self.url)

    def get_page_title(self) -> str:
        """
        Get the page title/header.

        Returns:
            Page title text
        """
        return self.get_text("h1")

    def get_team_count(self) -> int:
        """
        Get the number of teams displayed.

        Returns:
            Number of team entries
        """
        return self.count_elements("table tbody tr")

    def get_team_name(self, row_index: int = 0) -> str:
        """
        Get team name from a specific row.

        Args:
            row_index: Zero-based row index in the table

        Returns:
            Team name text
        """
        return self.get_text(f"table tbody tr:nth-child({row_index + 1}) td:nth-child(1)")

    def get_team_score(self, row_index: int = 0) -> str:
        """
        Get team Scrabble score from a specific row.

        Args:
            row_index: Zero-based row index in the table

        Returns:
            Team score text
        """
        return self.get_text(f"table tbody tr:nth-child({row_index + 1}) td.score")

    def has_standings_table(self) -> bool:
        """
        Check if standings table is visible.

        Returns:
            True if table is present
        """
        return self.is_visible("table")

    def has_team_with_name(self, team_name: str) -> bool:
        """
        Check if a team with specific name exists in the table.

        Args:
            team_name: Team name to search for

        Returns:
            True if team is found
        """
        selector = f"table tbody tr:has-text('{team_name}')"
        return self.count_elements(selector) > 0

    def get_all_team_names(self) -> list[str]:
        """
        Get all team names from the standings table.

        Returns:
            List of team names
        """
        count = self.get_team_count()
        return [self.get_team_name(i) for i in range(count)]

    def sort_by_column(self, column_name: str) -> None:
        """
        Click on a column header to sort by that column.

        Args:
            column_name: Column header text (e.g., "Team", "Score")
        """
        self.click(f"table thead th:has-text('{column_name}')")

    def filter_teams(self, filter_text: str) -> None:
        """
        Enter text in the teams filter/search box.

        Args:
            filter_text: Text to filter teams by
        """
        self.fill("#team-filter", filter_text)
