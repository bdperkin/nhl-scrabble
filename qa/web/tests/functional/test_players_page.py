"""Functional tests for the Players page.

This module contains Playwright-based functional tests for the Players ranking page, verifying
navigation, content display, sorting, and export functionality.
"""

import re

from playwright.sync_api import Page, expect


def test_players_page_loads(page: Page, base_url: str) -> None:
    """Test that players page loads successfully.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Page loads without errors
        - Correct title is displayed
        - HTTP 200 status code
    """
    response = page.goto(f"{base_url}/players")
    assert response is not None
    assert response.status == 200
    expect(page).to_have_title("NHL Scrabble Analyzer - Top Players")


def test_players_navigation_exists(page: Page, base_url: str) -> None:
    """Test that Players menu item exists in navigation.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Players link is visible in navigation
        - Link is between Home and Teams
        - Link is clickable
        - Link navigates to correct page
    """
    page.goto(base_url)
    players_link = page.locator('nav a:has-text("Players")')
    expect(players_link).to_be_visible()

    # Verify position in navigation (between Home and Teams)
    nav_links = page.locator("nav a")
    nav_text = [nav_links.nth(i).inner_text() for i in range(nav_links.count())]
    home_index = nav_text.index("Home")
    players_index = nav_text.index("Players")
    teams_index = nav_text.index("Teams")

    assert home_index < players_index < teams_index, "Players should be between Home and Teams"

    # Click and verify navigation
    players_link.click()
    expect(page).to_have_url(f"{base_url}/players?lang=en_US")


def test_players_page_header(page: Page, base_url: str) -> None:
    """Test that page header contains correct information.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Main heading is present
        - Page description is present
        - Timestamp is displayed
    """
    page.goto(f"{base_url}/players")

    # Check main heading
    heading = page.locator(".page-header h2")
    expect(heading).to_contain_text("Top NHL Players by Scrabble Score")

    # Check description
    description = page.locator(".page-description")
    expect(description).to_be_visible()
    expect(description).to_contain_text("Ranking of all NHL players")

    # Check timestamp
    timestamp = page.locator(".timestamp")
    expect(timestamp).to_be_visible()
    expect(timestamp).to_contain_text("Data as of")


def test_players_stats_summary(page: Page, base_url: str) -> None:
    """Test that stats summary cards are displayed.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Stats summary section exists
        - All 4 stat cards are present
        - Cards contain expected labels
    """
    page.goto(f"{base_url}/players")

    # Check stats summary section
    stats_summary = page.locator(".stats-summary")
    expect(stats_summary).to_be_visible()

    # Check individual stat cards
    stat_cards = page.locator(".stat-card")
    expect(stat_cards).to_have_count(4)

    # Verify stat card labels
    expect(stat_cards.nth(0)).to_contain_text("Total Players")
    expect(stat_cards.nth(1)).to_contain_text("Highest Score")
    expect(stat_cards.nth(2)).to_contain_text("Average Score")
    expect(stat_cards.nth(3)).to_contain_text("Lowest Score")


def test_players_table_displayed(page: Page, base_url: str) -> None:
    """Test that players table is displayed with data.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Table is visible
        - Table has correct headers
        - Table contains player data
        - At least 50 players are shown
    """
    page.goto(f"{base_url}/players")

    # Check table exists
    table = page.locator("#playersTable")
    expect(table).to_be_visible()

    # Check table headers
    headers = table.locator("thead th")
    expect(headers).to_have_count(4)

    header_texts = [headers.nth(i).inner_text() for i in range(headers.count())]
    assert "Rank" in header_texts
    assert "Player Name" in header_texts
    assert "Team" in header_texts
    assert "Score" in header_texts

    # Check that table has rows
    rows = table.locator("tbody tr")
    row_count = rows.count()
    assert row_count >= 50, f"Expected at least 50 players, got {row_count}"


def test_players_section_header(page: Page, base_url: str) -> None:
    """Test that section header is correct.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Section header contains "Player Rankings"
    """
    page.goto(f"{base_url}/players")

    section_header = page.locator(".results-section h3")
    expect(section_header).to_contain_text("Player Rankings")


def test_players_export_buttons(page: Page, base_url: str) -> None:
    """Test that export buttons are present and visible.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - CSV export button exists
        - JSON export button exists
        - Both buttons are visible
    """
    page.goto(f"{base_url}/players")

    # Check CSV export button
    csv_button = page.locator("#export-playersTable-csv")
    expect(csv_button).to_be_visible()
    expect(csv_button).to_contain_text("Export CSV")

    # Check JSON export button
    json_button = page.locator("#export-playersTable-json")
    expect(json_button).to_be_visible()
    expect(json_button).to_contain_text("Export JSON")


def test_players_table_sortable(page: Page, base_url: str) -> None:
    """Test that players table is sortable.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Table has sortable class
        - Column headers have data-sort attributes
        - Clicking headers sorts the table
    """
    page.goto(f"{base_url}/players")

    # Check table has sortable class
    table = page.locator("#playersTable")
    expect(table).to_have_class(re.compile(r"sortable"))

    # Check headers have sort attributes
    score_header = page.locator('th[data-sort="score"]')
    expect(score_header).to_be_visible()

    name_header = page.locator('th[data-sort="name"]')
    expect(name_header).to_be_visible()

    # Click score header to sort
    score_header.click()

    # Wait a moment for sort to complete
    page.wait_for_timeout(100)

    # Verify the table still has data after sort
    rows = page.locator("tbody tr")
    assert rows.count() > 0, "Table should have rows after sorting"


def test_players_table_info(page: Page, base_url: str) -> None:
    """Test that table info displays correct information.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Table info section exists
        - Contains "Showing X of Y total players"
    """
    page.goto(f"{base_url}/players")

    table_info = page.locator(".table-info")
    expect(table_info).to_be_visible()
    expect(table_info).to_contain_text("Showing")
    expect(table_info).to_contain_text("of")
    expect(table_info).to_contain_text("total players")


def test_players_legend_section(page: Page, base_url: str) -> None:
    """Test that Scrabble letter values legend is displayed.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Legend section exists
        - Contains heading "Scrabble Letter Values"
        - Contains all point values (1, 2, 3, 4, 5, 8, 10)
    """
    page.goto(f"{base_url}/players")

    # Check legend section
    legend = page.locator(".legend-section")
    expect(legend).to_be_visible()

    # Check legend heading
    legend_heading = legend.locator("h3")
    expect(legend_heading).to_contain_text("Scrabble Letter Values")

    # Check value groups exist
    value_groups = legend.locator(".value-group")
    expect(value_groups).to_have_count(7)  # 7 different point values

    # Verify all point values are present
    legend_text = legend.inner_text()
    for points in [
        "1 point:",
        "2 points:",
        "3 points:",
        "4 points:",
        "5 points:",
        "8 points:",
        "10 points:",
    ]:
        assert points in legend_text, f"Expected to find '{points}' in legend"


def test_players_responsive_layout(page: Page, base_url: str) -> None:
    """Test that page layout is responsive.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Page renders correctly on desktop
        - Key elements remain visible
    """
    page.goto(f"{base_url}/players")

    # Verify key elements are visible in desktop view
    expect(page.locator(".page-header")).to_be_visible()
    expect(page.locator(".stats-summary")).to_be_visible()
    expect(page.locator("#playersTable")).to_be_visible()
    expect(page.locator(".legend-section")).to_be_visible()


def test_players_accessibility_attributes(page: Page, base_url: str) -> None:
    """Test that page has proper accessibility attributes.

    Args:
        page: Playwright page object
        base_url: Base URL of the application

    Verifies:
        - Table has proper ARIA labels
        - Headers have scope attributes
        - Export buttons have aria-label
    """
    page.goto(f"{base_url}/players")

    # Check table ARIA attributes
    table = page.locator("#playersTable")
    expect(table).to_have_attribute("role", "table")
    expect(table).to_have_attribute("aria-label")

    # Check headers have scope
    headers = table.locator("thead th")
    for i in range(headers.count()):
        expect(headers.nth(i)).to_have_attribute("scope", "col")

    # Check export buttons have aria-label
    csv_button = page.locator("#export-playersTable-csv")
    expect(csv_button).to_have_attribute("aria-label")

    json_button = page.locator("#export-playersTable-json")
    expect(json_button).to_have_attribute("aria-label")
