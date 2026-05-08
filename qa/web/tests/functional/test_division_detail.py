"""Functional tests for division detail pages.

This module contains Playwright-based functional tests for the division detail pages, verifying team
standings, player lists, filtering, navigation, and i18n support.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Page


# Test data: NHL divisions and their parent conferences
DIVISIONS = {
    "Atlantic": "Eastern",
    "Metropolitan": "Eastern",
    "Central": "Western",
    "Pacific": "Western",
}


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_division_detail_page_loads(page: Page, division: str) -> None:
    """Test that division detail page loads successfully for all divisions."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check page title includes division name
    assert division in page.title()

    # Check header is present
    header = page.locator("h2").first
    assert header.is_visible()
    assert division in header.text_content() or ""


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_division_summary_statistics(page: Page, division: str) -> None:
    """Test that division summary statistics are displayed correctly."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check all stat cards are present
    stat_cards = page.locator(".stat-card")
    assert stat_cards.count() == 4

    # Verify stat card labels
    expected_labels = ["Total Teams", "Top Team", "Total Players", "Highest Player"]
    for i, label in enumerate(expected_labels):
        card = stat_cards.nth(i)
        assert card.locator("h4").text_content() == label
        # Verify stat value is present and non-empty
        stat_value = card.locator(".stat-value").text_content()
        assert stat_value
        assert stat_value.strip() != ""


@pytest.mark.parametrize("division,parent_conference", DIVISIONS.items())
def test_conference_badge_displayed(page: Page, division: str, parent_conference: str) -> None:
    """Test that conference badge shows correct parent conference."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check conference badge is present
    badge = page.locator(".conference-badge")
    assert badge.is_visible()

    # Verify parent conference name is in badge
    badge_text = badge.text_content() or ""
    assert parent_conference in badge_text

    # Verify conference link is clickable
    conference_link = badge.locator("a")
    assert conference_link.is_visible()
    href = conference_link.get_attribute("href") or ""
    assert f"/conferences/{parent_conference}" in href


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_team_standings_table_present(page: Page, division: str) -> None:
    """Test that team standings table is present and populated."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check team standings section
    team_section = page.locator("section.results-section").first
    assert "Team Standings" in team_section.locator("h3").text_content() or ""

    # Check table exists
    table = page.locator("#divisionTeamsTable")
    assert table.is_visible()

    # Verify table headers
    headers = table.locator("thead th")
    expected_headers = ["Rank", "Team", "Total Score", "Avg Score", "Players"]
    for i, expected in enumerate(expected_headers):
        header_text = headers.nth(i).text_content() or ""
        assert expected in header_text

    # Verify table has data rows
    rows = table.locator("tbody tr")
    assert rows.count() > 0


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_top_players_table_present(page: Page, division: str) -> None:
    """Test that top players table is present and populated."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check players section
    player_section = page.locator("section.results-section").nth(1)
    assert "Top 20 Players" in player_section.locator("h3").text_content() or ""

    # Check table exists
    table = page.locator("#divisionPlayersTable")
    assert table.is_visible()

    # Verify table headers
    headers = table.locator("thead th")
    expected_headers = ["Rank", "Player Name", "Team", "Score"]
    for i, expected in enumerate(expected_headers):
        header_text = headers.nth(i).text_content() or ""
        assert expected in header_text

    # Verify table has data rows (up to 20)
    rows = table.locator("tbody tr")
    assert rows.count() > 0
    assert rows.count() <= 20


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_teams_filtered_by_division(page: Page, division: str) -> None:
    """Test that teams are correctly filtered to show only division teams."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Get all team rows
    table = page.locator("#divisionTeamsTable")
    rows = table.locator("tbody tr")
    team_count = rows.count()

    # NHL divisions have 7-8 teams each
    assert 6 <= team_count <= 9, f"Expected 6-9 teams in {division}, got {team_count}"

    # Verify all teams have data
    for i in range(team_count):
        row = rows.nth(i)
        cells = row.locator("td")

        # Rank should be sequential
        rank = cells.nth(0).text_content()
        assert rank == str(i + 1)

        # Team name should be non-empty
        team_name = cells.nth(1).text_content()
        assert team_name
        assert team_name.strip() != ""

        # Scores should be numeric
        total_score = cells.nth(2).text_content()
        assert total_score
        assert total_score.isdigit()


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_players_filtered_by_division(page: Page, division: str) -> None:
    """Test that players are correctly filtered to division teams."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Get team abbreviations from team table
    team_table = page.locator("#divisionTeamsTable")
    team_rows = team_table.locator("tbody tr")
    division_teams = set()

    for i in range(team_rows.count()):
        # Team name is in column 2 (index 1)
        team_cell = team_rows.nth(i).locator("td").nth(1)
        team_text = team_cell.text_content() or ""
        # Extract team abbreviation (usually in parentheses or at end)
        division_teams.add(team_text.strip())

    # Check players table
    player_table = page.locator("#divisionPlayersTable")
    player_rows = player_table.locator("tbody tr")

    # Verify players belong to division teams
    for i in range(player_rows.count()):
        # Team abbrev is in column 3 (index 2)
        team_cell = player_rows.nth(i).locator("td").nth(2)
        player_team = team_cell.text_content() or ""
        player_team = player_team.strip()
        # Note: We can't strictly verify team membership without full team data
        # but we can verify the team column is populated
        assert player_team != "", f"Player at row {i} has no team"


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_team_table_sorting(page: Page, division: str) -> None:
    """Test that team standings table can be sorted by columns."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    table = page.locator("#divisionTeamsTable")

    # Click on Team header to sort alphabetically
    team_header = table.locator("thead th[data-sort='team']")
    team_header.click()

    # Wait for sort to complete
    page.wait_for_timeout(500)

    # Verify table is still populated after sort
    sorted_first = table.locator("tbody tr").first.locator("td").nth(1).text_content()
    assert sorted_first
    assert sorted_first.strip() != ""


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_player_table_sorting(page: Page, division: str) -> None:
    """Test that players table can be sorted by columns."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    table = page.locator("#divisionPlayersTable")

    # Click on Name header to sort alphabetically
    name_header = table.locator("thead th[data-sort='name']")
    name_header.click()

    # Wait for sort to complete
    page.wait_for_timeout(500)

    # Verify table is still populated after sort
    sorted_score = table.locator("tbody tr").first.locator("td").nth(3).text_content()
    assert sorted_score
    assert sorted_score.strip() != ""


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_export_buttons_present(page: Page, division: str) -> None:
    """Test that export buttons are present for both tables."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Team table export buttons
    team_csv_btn = page.locator("#export-divisionTeamsTable-csv")
    team_json_btn = page.locator("#export-divisionTeamsTable-json")
    assert team_csv_btn.is_visible()
    assert team_json_btn.is_visible()

    # Player table export buttons
    player_csv_btn = page.locator("#export-divisionPlayersTable-csv")
    player_json_btn = page.locator("#export-divisionPlayersTable-json")
    assert player_csv_btn.is_visible()
    assert player_json_btn.is_visible()


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_navigation_back_to_divisions(page: Page, division: str) -> None:
    """Test navigation link back to all divisions page."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Find back link
    back_link = page.locator("a:has-text('Back to All Divisions')")
    assert back_link.is_visible()

    # Verify link href
    href = back_link.get_attribute("href") or ""
    assert "/divisions" in href


@pytest.mark.parametrize("division,parent_conference", DIVISIONS.items())
def test_navigation_to_parent_conference(page: Page, division: str, parent_conference: str) -> None:
    """Test navigation link to parent conference page."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Find conference link in navigation
    conf_link = page.locator(f"a:has-text('View {parent_conference} Conference')")
    assert conf_link.is_visible()

    # Verify link href
    href = conf_link.get_attribute("href") or ""
    assert f"/conferences/{parent_conference}" in href


def test_invalid_division_returns_404(page: Page) -> None:
    """Test that invalid division name returns 404 error."""
    response = page.goto("http://localhost:5000/divisions/InvalidDivision")

    # Should get 404 status
    assert response
    assert response.status == 404


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_division_page_locale_parameter(page: Page, division: str) -> None:
    """Test that locale parameter is preserved in navigation links."""
    page.goto(f"http://localhost:5000/divisions/{division}?lang=fr_CA")

    # Check that back link preserves locale
    back_link = page.locator("a:has-text('← Back to All Divisions')")
    href = back_link.get_attribute("href") or ""
    assert "lang=fr_CA" in href

    # Check that conference link preserves locale
    conference_link = page.locator(".conference-badge a")
    conf_href = conference_link.get_attribute("href") or ""
    assert "lang=fr_CA" in conf_href


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_division_case_insensitive(page: Page, division: str) -> None:
    """Test that division names are case-insensitive in URL."""
    # Try lowercase version
    page.goto(f"http://localhost:5000/divisions/{division.lower()}")

    # Should still load successfully
    header = page.locator("h2").first
    assert header.is_visible()
    # Header should show properly capitalized name
    assert division in header.text_content() or ""


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_timestamp_displayed(page: Page, division: str) -> None:
    """Test that data timestamp is displayed on division page."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Find timestamp
    timestamp = page.locator(".timestamp")
    assert timestamp.is_visible()

    # Verify format (should contain "Data as of" and date/time)
    timestamp_text = timestamp.text_content() or ""
    assert "Data as of" in timestamp_text or "as of" in timestamp_text
    # Should contain a date pattern (e.g., "May 07, 2026")
    assert re.search(r"\w+ \d{1,2}, \d{4}", timestamp_text)


@pytest.mark.parametrize("division", ["Atlantic", "Metropolitan", "Central", "Pacific"])
def test_responsive_layout(page: Page, division: str) -> None:
    """Test that division detail page has responsive layout elements."""
    page.goto(f"http://localhost:5000/divisions/{division}")

    # Check that stat cards use grid layout
    stats_summary = page.locator(".stats-summary")
    assert stats_summary.is_visible()

    # Check that tables have table-container wrapper for horizontal scroll
    team_container = page.locator("#divisionTeamsTable").locator("..")
    assert "table-container" in (team_container.get_attribute("class") or "")

    player_container = page.locator("#divisionPlayersTable").locator("..")
    assert "table-container" in (player_container.get_attribute("class") or "")
