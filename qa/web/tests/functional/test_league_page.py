"""Functional tests for the League page.

This module contains Playwright-based functional tests for the League standings page, verifying
navigation, content display, and user interactions.
"""

import pytest
from playwright.sync_api import Page, expect


def test_league_page_loads(page: Page, base_url: str) -> None:
    """Test that league page loads successfully.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Page loads without errors
        - Correct title is displayed
        - HTTP 200 status code
    """
    response = page.goto(f"{base_url}/league")
    assert response is not None
    assert response.status == 200
    expect(page).to_have_title("NHL Scrabble Analyzer - League Standings")


def test_league_navigation_exists(page: Page, base_url: str) -> None:
    """Test that League menu item exists in navigation.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - League link is visible in navigation
        - Link is clickable
        - Link navigates to correct page
    """
    page.goto(base_url)
    league_link = page.locator('nav a:has-text("League")')
    expect(league_link).to_be_visible()

    # Click and verify navigation
    league_link.click()
    expect(page).to_have_url(f"{base_url}/league")


def test_league_page_header(page: Page, base_url: str) -> None:
    """Test that page header contains correct information.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Main heading is present
        - Heading text is correct
    """
    page.goto(f"{base_url}/league")

    # Check main heading
    heading = page.locator("h3")
    expect(heading).to_contain_text("League Standings by Total Scrabble Score")


def test_league_stats_summary(page: Page, base_url: str) -> None:
    """Test that stats summary cards are displayed.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Stats summary section exists
        - All stat cards are present
        - Cards contain expected data
    """
    page.goto(f"{base_url}/league")

    # Check stats summary section
    stats_summary = page.locator(".stats-summary")
    expect(stats_summary).to_be_visible()

    # Check individual stat cards
    stat_cards = page.locator(".stat-card")
    expect(stat_cards).to_have_count(4)

    # Verify stat card labels
    expect(stat_cards.nth(0)).to_contain_text("Total Teams")
    expect(stat_cards.nth(1)).to_contain_text("Top Team")
    expect(stat_cards.nth(2)).to_contain_text("Lowest Team")
    expect(stat_cards.nth(3)).to_contain_text("Total Players")


def test_league_all_teams_displayed(page: Page, base_url: str) -> None:
    """Test that all teams are displayed in league standings.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - League card exists
        - All 32 NHL teams are displayed
        - Teams are in ordered list format
    """
    page.goto(f"{base_url}/league")

    # Check that league card exists
    league_card = page.locator(".league-card")
    expect(league_card).to_be_visible()

    # Check heading
    expect(league_card.locator("h4")).to_contain_text("National Hockey League")

    # Count team items (should be 32 NHL teams)
    team_items = page.locator(".league-card ol li")
    expect(team_items).to_have_count(32)


def test_league_team_item_structure(page: Page, base_url: str) -> None:
    """Test that team items have correct format.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Team items are in ordered list
        - Team name and score are displayed
        - Format is: "Team Name (Score)"
    """
    page.goto(f"{base_url}/league")

    # Get first team item
    first_team = page.locator(".league-card ol li").first
    expect(first_team).to_be_visible()

    # Verify format contains team name and score in parentheses
    # Should match pattern: "Team Name (Score)"
    team_text = first_team.text_content()
    assert team_text is not None
    assert "(" in team_text and ")" in team_text, "Team item should contain score in parentheses"


def test_league_info_section(page: Page, base_url: str) -> None:
    """Test that info section is present with links.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Info section exists
        - Heading is correct
        - Description text is present
        - Links to divisions and conferences pages work
    """
    page.goto(f"{base_url}/league")

    # Check info section
    info_section = page.locator(".info-section")
    expect(info_section).to_be_visible()

    # Check heading
    expect(info_section.locator("h3")).to_contain_text("About League Standings")

    # Check links
    divisions_link = info_section.locator('a:has-text("Division Standings")')
    conferences_link = info_section.locator('a:has-text("Conference Standings")')

    expect(divisions_link).to_be_visible()
    expect(conferences_link).to_be_visible()

    # Verify links point to correct pages
    expect(divisions_link).to_have_attribute("href", "/divisions?lang=en_US")
    expect(conferences_link).to_have_attribute("href", "/conferences?lang=en_US")


def test_league_info_links_navigation(page: Page, base_url: str) -> None:
    """Test that info section links navigate correctly.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Division link navigates to divisions page
        - Conference link navigates to conferences page
    """
    page.goto(f"{base_url}/league")

    # Test divisions link
    divisions_link = page.locator('a:has-text("Division Standings")')
    divisions_link.click()
    expect(page).to_have_url(f"{base_url}/divisions?lang=en_US")

    # Navigate back
    page.goto(f"{base_url}/league")

    # Test conferences link
    conferences_link = page.locator('a:has-text("Conference Standings")')
    conferences_link.click()
    expect(page).to_have_url(f"{base_url}/conferences?lang=en_US")


def test_league_responsive_design(page: Page, base_url: str) -> None:
    """Test that page is responsive on mobile devices.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Page displays correctly on mobile viewport
        - Navigation menu works on mobile
        - Content is readable
    """
    # Set mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{base_url}/league")

    # Verify page loads
    expect(page).to_have_title("NHL Scrabble Analyzer - League Standings")

    # Check that content is visible
    league_card = page.locator(".league-card")
    expect(league_card).to_be_visible()

    # Check team items are visible
    team_items = page.locator(".league-card ol li")
    expect(team_items.first).to_be_visible()


def test_league_language_selector(page: Page, base_url: str) -> None:
    """Test that language selector works on league page.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Language selector is visible
        - Changing language updates page content
        - URL parameter changes correctly
    """
    page.goto(f"{base_url}/league")

    # Check language selector exists
    language_select = page.locator("#languageSelect")
    expect(language_select).to_be_visible()

    # Change to French Canadian
    language_select.select_option("fr_CA")

    # Verify URL updated
    page.wait_for_url(f"{base_url}/league?lang=fr_CA")

    # Verify page title updated (French translation)
    heading = page.locator("h3")
    expect(heading).to_contain_text("Classement de la ligue par score Scrabble total")


@pytest.mark.parametrize(
    "locale,expected_title",
    [
        ("en_US", "League Standings by Total Scrabble Score"),
        ("en_CA", "League Standings by Total Scrabble Score"),
        ("fr_CA", "Classement de la ligue par score Scrabble total"),
        ("sv_SE", "Ligaställning efter Total Scrabble-poäng"),
    ],
)
def test_league_i18n(page: Page, base_url: str, locale: str, expected_title: str) -> None:
    """Test internationalization for different locales.

    Args:
        page: Playwright page object
        base_url: Base URL of the application
        locale: Locale code to test
        expected_title: Expected heading text in that locale

    Verifies:
        - Page loads with locale parameter
        - Heading is translated correctly
        - Other UI elements are translated
    """
    page.goto(f"{base_url}/league?lang={locale}")

    # Check heading translation
    heading = page.locator("h3")
    expect(heading).to_contain_text(expected_title)

    # Verify locale is applied
    expect(page).to_have_url(f"{base_url}/league?lang={locale}")


def test_league_navigation_order(page: Page, base_url: str) -> None:
    """Test that League appears in correct position in navigation.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - League item appears between Conferences and Playoffs
        - Navigation order is correct
    """
    page.goto(base_url)

    # Get all nav links
    nav_links = page.locator("nav ul li a")

    # Find indices
    conferences_index = -1
    league_index = -1
    playoffs_index = -1

    for i in range(nav_links.count()):
        text = nav_links.nth(i).text_content()
        if text == "Conferences":
            conferences_index = i
        elif text == "League":
            league_index = i
        elif text == "Playoffs":
            playoffs_index = i

    # Verify order
    assert conferences_index >= 0, "Conferences link not found"
    assert league_index >= 0, "League link not found"
    assert playoffs_index >= 0, "Playoffs link not found"
    assert (
        conferences_index < league_index < playoffs_index
    ), "League should be between Conferences and Playoffs"
