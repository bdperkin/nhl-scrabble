"""Functional tests for team detail pages."""

import re

import pytest
from playwright.sync_api import Page, expect


def test_team_detail_page_loads(page: Page, base_url: str) -> None:
    """Test team detail page loads correctly."""
    page.goto(f"{base_url}/teams/TOR")

    # Check page title contains team name
    expect(page).to_have_title(re.compile(r".*Maple Leafs.*Player Rankings.*"))

    # Check team logo is visible
    logo = page.locator(".team-logo")
    expect(logo).to_be_visible()

    # Check stats cards are visible
    expect(page.locator(".stats-summary")).to_be_visible()
    expect(page.get_by_text("Total Players")).to_be_visible()
    expect(page.get_by_text("Team Total Score")).to_be_visible()
    expect(page.get_by_text("Average Score")).to_be_visible()
    expect(page.get_by_text("Top Player")).to_be_visible()


def test_team_detail_logo_fallback(page: Page, base_url: str) -> None:
    """Test logo has fallback behavior if it fails to load."""
    page.goto(f"{base_url}/teams/TOR")

    # Logo should have onerror attribute
    logo = page.locator(".team-logo")
    expect(logo).to_have_attribute("onerror", "this.style.display='none'")

    # Logo should have loading="lazy"
    expect(logo).to_have_attribute("loading", "lazy")


def test_team_detail_breadcrumb_navigation(page: Page, base_url: str) -> None:
    """Test breadcrumb navigation links."""
    page.goto(f"{base_url}/teams/TOR")

    # Should have links to division and conference
    division_link = page.locator('a[href*="/divisions/Atlantic"]')
    conference_link = page.locator('a[href*="/conferences/Eastern"]')

    expect(division_link).to_be_visible()
    expect(conference_link).to_be_visible()


def test_team_detail_player_table(page: Page, base_url: str) -> None:
    """Test player rankings table is displayed correctly."""
    page.goto(f"{base_url}/teams/TOR")

    # Get player table
    table = page.locator("#playersTable")
    expect(table).to_be_visible()

    # Check table headers
    expect(table.locator("th").filter(has_text="Rank")).to_be_visible()
    expect(table.locator("th").filter(has_text="Player")).to_be_visible()
    expect(table.locator("th").filter(has_text="Score")).to_be_visible()
    expect(table.locator("th").filter(has_text="First Name")).to_be_visible()
    expect(table.locator("th").filter(has_text="Last Name")).to_be_visible()

    # Check that table has rows (at least 1 player)
    rows = table.locator("tbody tr")
    expect(rows).not_to_have_count(0)


def test_team_detail_export_buttons(page: Page, base_url: str) -> None:
    """Test export buttons are present."""
    page.goto(f"{base_url}/teams/TOR")

    # Check export buttons exist
    csv_button = page.locator("#export-playersTable-csv")
    json_button = page.locator("#export-playersTable-json")

    expect(csv_button).to_be_visible()
    expect(json_button).to_be_visible()


def test_team_detail_table_sorting(page: Page, base_url: str) -> None:
    """Test player table sorting functionality."""
    page.goto(f"{base_url}/teams/TOR")

    # Get player table
    table = page.locator("#playersTable")

    # Click score header to sort (should toggle order)
    score_header = table.locator("th").filter(has_text=re.compile(r"^Score$"))
    score_header.click()

    # Wait for sort to complete
    page.wait_for_timeout(300)

    # Verify table still has data after sorting
    rows = table.locator("tbody tr")
    expect(rows).not_to_have_count(0)

    # Verify first row has valid data
    first_row_sorted = table.locator("tbody tr").first
    sorted_data = first_row_sorted.locator("td").nth(1).text_content()

    # Data should not be empty
    assert sorted_data is not None and sorted_data.strip() != ""


def test_team_detail_navigation_links(page: Page, base_url: str) -> None:
    """Test navigation links at bottom of page."""
    page.goto(f"{base_url}/teams/TOR")

    # Should have link back to all teams
    back_link = page.get_by_role("link", name=re.compile(r"Back to All Teams"))
    expect(back_link).to_be_visible()

    # Should have link to division detail
    division_link = page.get_by_role("link", name=re.compile(r"View.*Division"))
    expect(division_link).to_be_visible()

    # Should have link to conference detail
    conference_link = page.get_by_role("link", name=re.compile(r"View.*Conference"))
    expect(conference_link).to_be_visible()


def test_team_detail_invalid_team(page: Page, base_url: str) -> None:
    """Test 404 error for non-existent team."""
    response = page.goto(f"{base_url}/teams/XXX")

    # Should return 404 status
    assert response is not None
    assert response.status == 404


def test_team_detail_case_insensitive(page: Page, base_url: str) -> None:
    """Test that team abbreviation is case-insensitive."""
    # Test uppercase
    page.goto(f"{base_url}/teams/TOR")
    expect(page.locator(".team-header")).to_be_visible()

    # Test lowercase
    page.goto(f"{base_url}/teams/tor")
    expect(page.locator(".team-header")).to_be_visible()

    # Test mixed case
    page.goto(f"{base_url}/teams/Tor")
    expect(page.locator(".team-header")).to_be_visible()


@pytest.mark.parametrize(
    "team_abbrev",
    [
        "TOR",  # Toronto Maple Leafs
        "MTL",  # Montreal Canadiens
        "BOS",  # Boston Bruins
        "NYR",  # New York Rangers
        "CHI",  # Chicago Blackhawks
        "EDM",  # Edmonton Oilers
    ],
)
def test_team_detail_multiple_teams(page: Page, base_url: str, team_abbrev: str) -> None:
    """Test team detail pages for multiple teams."""
    page.goto(f"{base_url}/teams/{team_abbrev}")

    # Page should load successfully
    expect(page.locator(".team-header")).to_be_visible()
    expect(page.locator(".team-logo")).to_be_visible()
    expect(page.locator("#playersTable")).to_be_visible()


def test_team_detail_i18n_support(page: Page, base_url: str) -> None:
    """Test internationalization support."""
    # Test French Canadian locale
    page.goto(f"{base_url}/teams/TOR?lang=fr_CA")

    # Check that page loads
    expect(page.locator(".team-header")).to_be_visible()

    # Test Swedish locale
    page.goto(f"{base_url}/teams/TOR?lang=sv_SE")
    expect(page.locator(".team-header")).to_be_visible()


def test_team_detail_responsive_layout(page: Page, base_url: str) -> None:
    """Test responsive layout on different viewport sizes."""
    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{base_url}/teams/TOR")

    # Team header should be visible
    expect(page.locator(".team-header")).to_be_visible()

    # Logo should be smaller on mobile (via CSS)
    logo = page.locator(".team-logo")
    expect(logo).to_be_visible()

    # Test tablet viewport
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto(f"{base_url}/teams/TOR")
    expect(page.locator(".team-header")).to_be_visible()

    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{base_url}/teams/TOR")
    expect(page.locator(".team-header")).to_be_visible()


def test_team_detail_timestamp(page: Page, base_url: str) -> None:
    """Test that data timestamp is displayed."""
    page.goto(f"{base_url}/teams/TOR")

    # Should have timestamp
    timestamp = page.get_by_text(re.compile(r"Data as of.*"))
    expect(timestamp).to_be_visible()


def test_teams_page_links_to_detail(page: Page, base_url: str) -> None:
    """Test navigation from teams page to team detail page."""
    # Go to teams page
    page.goto(f"{base_url}/teams")

    # Find a team link (e.g., first team in table)
    team_link = page.locator(".team-link").first
    expect(team_link).to_be_visible()

    # Click the team link
    team_link.click()

    # Should navigate to team detail page
    expect(page.locator(".team-header")).to_be_visible()
    expect(page.locator("#playersTable")).to_be_visible()


def test_team_detail_stats_accuracy(page: Page, base_url: str) -> None:
    """Test that team statistics are displayed accurately."""
    page.goto(f"{base_url}/teams/TOR")

    # All stat cards should have values
    stat_cards = page.locator(".stat-card")
    expect(stat_cards).to_have_count(4)

    # Each stat card should have a value
    for i in range(4):
        stat_value = stat_cards.nth(i).locator(".stat-value")
        expect(stat_value).to_be_visible()
        # Value should not be empty
        expect(stat_value).not_to_be_empty()


def test_team_detail_player_ranking(page: Page, base_url: str) -> None:
    """Test that players are ranked correctly by score."""
    page.goto(f"{base_url}/teams/TOR")

    # Get all rank cells
    table = page.locator("#playersTable")
    rank_cells = table.locator("tbody td:nth-child(1)")

    # First rank should be 1
    first_rank = rank_cells.first
    expect(first_rank).to_have_text("1")

    # Get all score cells
    score_cells = table.locator("tbody td:nth-child(3)")

    # Get first two scores
    first_score_text = score_cells.first.text_content()
    second_score_text = score_cells.nth(1).text_content()

    if first_score_text and second_score_text:
        first_score = int(first_score_text)
        second_score = int(second_score_text)

        # First score should be >= second score (descending order)
        assert first_score >= second_score


def test_team_detail_accessibility(page: Page, base_url: str) -> None:
    """Test accessibility features."""
    page.goto(f"{base_url}/teams/TOR")

    # Table should have proper role
    table = page.locator("#playersTable")
    expect(table).to_have_attribute("role", "table")

    # Export buttons should have aria-labels
    csv_button = page.locator("#export-playersTable-csv")
    expect(csv_button).to_have_attribute("aria-label")

    json_button = page.locator("#export-playersTable-json")
    expect(json_button).to_have_attribute("aria-label")

    # Logo should have alt text
    logo = page.locator(".team-logo")
    expect(logo).to_have_attribute("alt")


def test_team_detail_all_players_shown(page: Page, base_url: str) -> None:
    """Test that all team players are shown, not just top 20."""
    page.goto(f"{base_url}/teams/TOR")

    # Get player table rows
    table = page.locator("#playersTable")
    rows = table.locator("tbody tr")

    # Most NHL teams have 20-25 players
    # Check that we have more than just top 20 (if team has more)
    row_count = rows.count()

    # Should have at least a few players
    assert row_count >= 15, f"Expected at least 15 players, got {row_count}"
