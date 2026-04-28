"""Stats/analytics page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class StatsPage(BasePage):
    """
    Page Object Model for the stats/analytics page.

    Provides methods to interact with player statistics,
    top scorers, and analytical data.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """
        Initialize the stats page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/stats"

    def navigate(self) -> None:
        """Navigate to the stats page."""
        super().navigate(self.url)

    def get_page_title(self) -> str:
        """
        Get the page title/header.

        Returns:
            Page title text
        """
        return self.get_text("h1")

    def has_top_players_section(self) -> bool:
        """
        Check if top players section is visible.

        Returns:
            True if section is present
        """
        return self.is_visible(".top-players-section")

    def get_top_players_count(self) -> int:
        """
        Get the number of top players shown.

        Returns:
            Number of player entries (typically 30)
        """
        return self.count_elements(".top-players-section table tbody tr")

    def get_player_name(self, rank: int = 1) -> str:
        """
        Get player name by rank.

        Args:
            rank: Player rank (1-based, e.g., 1 for #1 player)

        Returns:
            Player name text
        """
        return self.get_text(f".top-players-section table tbody tr:nth-child({rank}) .player-name")

    def get_player_score(self, rank: int = 1) -> str:
        """
        Get player Scrabble score by rank.

        Args:
            rank: Player rank (1-based)

        Returns:
            Player score text
        """
        return self.get_text(f".top-players-section table tbody tr:nth-child({rank}) .score")

    def get_player_team(self, rank: int = 1) -> str:
        """
        Get player's team by rank.

        Args:
            rank: Player rank (1-based)

        Returns:
            Team name/abbreviation
        """
        return self.get_text(f".top-players-section table tbody tr:nth-child({rank}) .team")

    def has_team_stats_section(self) -> bool:
        """
        Check if team statistics section is visible.

        Returns:
            True if section is present
        """
        return self.is_visible(".team-stats-section")

    def get_highest_scoring_team(self) -> str:
        """
        Get the highest scoring team name.

        Returns:
            Team name text
        """
        return self.get_text(".highest-scoring-team .team-name")

    def get_lowest_scoring_team(self) -> str:
        """
        Get the lowest scoring team name.

        Returns:
            Team name text
        """
        return self.get_text(".lowest-scoring-team .team-name")

    def has_letter_distribution_chart(self) -> bool:
        """
        Check if letter distribution chart is visible.

        Returns:
            True if chart is present
        """
        return self.is_visible(".letter-distribution-chart")

    def has_score_distribution_chart(self) -> bool:
        """
        Check if score distribution chart is visible.

        Returns:
            True if chart is present
        """
        return self.is_visible(".score-distribution-chart")

    def filter_by_position(self, position: str) -> None:
        """
        Filter players by position.

        Args:
            position: Position filter (e.g., "C", "LW", "RW", "D", "G")
        """
        self.click(f"#position-filter option:has-text('{position}')")

    def filter_by_team(self, team: str) -> None:
        """
        Filter players by team.

        Args:
            team: Team name or abbreviation
        """
        self.fill("#team-filter", team)

    def sort_players_by(self, column: str) -> None:
        """
        Sort players by a specific column.

        Args:
            column: Column name (e.g., "Name", "Score", "Team")
        """
        self.click(f".top-players-section table thead th:has-text('{column}')")

    def get_total_players(self) -> str:
        """
        Get total number of players analyzed.

        Returns:
            Total players count text
        """
        return self.get_text(".total-players-stat")

    def get_average_score(self) -> str:
        """
        Get average player score statistic.

        Returns:
            Average score text
        """
        return self.get_text(".average-score-stat")

    def has_export_button(self) -> bool:
        """
        Check if export/download button is visible.

        Returns:
            True if export button is present
        """
        return self.is_visible("#export-stats")

    def export_stats(self) -> None:
        """Click the export/download stats button."""
        self.click("#export-stats")
