"""Playoffs page object model."""

from pages.base_page import BasePage
from playwright.sync_api import Page


class PlayoffsPage(BasePage):
    """Page Object Model for the playoffs/bracket page.

    Provides methods to interact with playoff brackets and matchups.
    """

    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        """Initialize the playoffs page.

        Args:
            page: Playwright Page object
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/playoffs"

    def navigate(self) -> None:
        """Navigate to the playoffs page."""
        super().navigate(self.url)

    def get_page_title(self) -> str:
        """Get the page title/header.

        Returns:
            Page title text
        """
        return self.get_text("h1")

    def has_eastern_bracket(self) -> bool:
        """Check if Eastern Conference bracket is visible.

        Returns:
            True if Eastern bracket is present
        """
        return self.is_visible(".bracket-eastern")

    def has_western_bracket(self) -> bool:
        """Check if Western Conference bracket is visible.

        Returns:
            True if Western bracket is present
        """
        return self.is_visible(".bracket-western")

    def get_matchup_count(self, conference: str = "eastern") -> int:
        """Get the number of matchups in a conference bracket.

        Args:
            conference: Conference name ("eastern" or "western")

        Returns:
            Number of matchups
        """
        return self.count_elements(f".bracket-{conference} .matchup")

    def get_matchup_team(self, conference: str, round_num: int, matchup_num: int, seed: int) -> str:
        """Get team name from a specific matchup.

        Args:
            conference: Conference name ("eastern" or "western")
            round_num: Round number (1 for first round, 2 for semis, etc.)
            matchup_num: Matchup number within round (0-indexed)
            seed: Seed position (1 for top seed, 2 for bottom seed)

        Returns:
            Team name text
        """
        selector = (
            f".bracket-{conference} "
            f".round-{round_num} "
            f".matchup:nth-child({matchup_num + 1}) "
            f".team:nth-child({seed})"
        )
        return self.get_text(selector)

    def get_matchup_score(
        self, conference: str, round_num: int, matchup_num: int, seed: int
    ) -> str:
        """Get team score from a specific matchup.

        Args:
            conference: Conference name ("eastern" or "western")
            round_num: Round number
            matchup_num: Matchup number within round (0-indexed)
            seed: Seed position (1 for top, 2 for bottom)

        Returns:
            Team score text
        """
        selector = (
            f".bracket-{conference} "
            f".round-{round_num} "
            f".matchup:nth-child({matchup_num + 1}) "
            f".team:nth-child({seed}) .score"
        )
        return self.get_text(selector)

    def has_stanley_cup_final(self) -> bool:
        """Check if Stanley Cup Final matchup is visible.

        Returns:
            True if final is present
        """
        return self.is_visible(".stanley-cup-final")

    def get_finals_teams(self) -> list[str]:
        """Get the two teams in Stanley Cup Final.

        Returns:
            List of two team names [Eastern champ, Western champ]
        """
        return [
            self.get_text(".stanley-cup-final .team:nth-child(1)"),
            self.get_text(".stanley-cup-final .team:nth-child(2)"),
        ]

    def has_wild_card_indicators(self) -> bool:
        """Check if wild card indicators (x) are shown.

        Returns:
            True if wild card indicators are present
        """
        return self.is_visible(".indicator-wildcard")

    def has_division_leader_indicators(self) -> bool:
        """Check if division leader indicators (y) are shown.

        Returns:
            True if division leader indicators are present
        """
        return self.is_visible(".indicator-division")

    def expand_round(self, round_name: str) -> None:
        """Expand/collapse a playoff round section (if collapsible).

        Args:
            round_name: Round name (e.g., "First Round", "Conference Finals")
        """
        self.click(f".round-section:has-text('{round_name}') .expand-button")

    def get_bracket_legend(self) -> bool:
        """Check if bracket legend/key is visible.

        Returns:
            True if legend is present
        """
        return self.is_visible(".bracket-legend")
