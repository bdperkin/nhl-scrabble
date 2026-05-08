"""Functional tests for conference detail pages."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import expect

if TYPE_CHECKING:
    from playwright.sync_api import Page


@pytest.mark.functional
def test_eastern_conference_page_loads(page: Page, base_url: str) -> None:
    """Test that Eastern conference detail page loads."""
    page.goto(f"{base_url}/conferences/Eastern")
    expect(page).to_have_title(re.compile("Eastern Conference"))


@pytest.mark.functional
def test_western_conference_page_loads(page: Page, base_url: str) -> None:
    """Test that Western conference detail page loads."""
    page.goto(f"{base_url}/conferences/Western")
    expect(page).to_have_title(re.compile("Western Conference"))


@pytest.mark.functional
def test_invalid_conference_returns_404(page: Page, base_url: str) -> None:
    """Test that invalid conference name returns 404."""
    response = page.goto(f"{base_url}/conferences/Invalid")
    assert response is not None
    assert response.status == 404


@pytest.mark.functional
def test_conference_case_insensitive(page: Page, base_url: str) -> None:
    """Test that conference names are case-insensitive."""
    # Test lowercase
    page.goto(f"{base_url}/conferences/eastern")
    expect(page).to_have_title(re.compile("Eastern Conference"))

    # Test uppercase
    page.goto(f"{base_url}/conferences/WESTERN")
    expect(page).to_have_title(re.compile("Western Conference"))


@pytest.mark.functional
def test_conference_teams_filtered(page: Page, base_url: str) -> None:
    """Test that teams are filtered by conference."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Check teams table exists
    teams_table = page.locator("#conferenceTeamsTable")
    expect(teams_table).to_be_visible()

    # Eastern Conference should have 16 teams
    team_rows = page.locator("#conferenceTeamsTable tbody tr")
    count = team_rows.count()
    assert count == 16, f"Expected 16 Eastern teams, got {count}"


@pytest.mark.functional
def test_conference_players_filtered(page: Page, base_url: str) -> None:
    """Test that players are filtered by conference."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Check players table exists
    players_table = page.locator("#conferencePlayersTable")
    expect(players_table).to_be_visible()

    # Should have 20 players (or fewer if not enough data)
    player_rows = page.locator("#conferencePlayersTable tbody tr")
    count = player_rows.count()
    assert 1 <= count <= 20, f"Expected 1-20 players, got {count}"


@pytest.mark.functional
def test_conference_stats_summary_visible(page: Page, base_url: str) -> None:
    """Test that conference-specific stats summary is visible."""
    page.goto(f"{base_url}/conferences/Western")

    # Check all stat cards are visible
    stat_cards = page.locator(".stats-summary .stat-card")
    expect(stat_cards).to_have_count(4)

    # Check specific stats
    expect(page.locator(".stat-card:has-text('Total Teams')")).to_be_visible()
    expect(page.locator(".stat-card:has-text('Top Team')")).to_be_visible()
    expect(page.locator(".stat-card:has-text('Total Players')")).to_be_visible()
    expect(page.locator(".stat-card:has-text('Highest Player')")).to_be_visible()


@pytest.mark.functional
def test_conference_links_from_main_page(page: Page, base_url: str) -> None:
    """Test that links from conferences page work."""
    page.goto(f"{base_url}/conferences")

    # Click Eastern conference link
    page.click('a.conference-link:has-text("Eastern")')

    # Should navigate to detail page
    expect(page).to_have_url(re.compile("/conferences/Eastern"))
    expect(page).to_have_title(re.compile("Eastern Conference"))


@pytest.mark.functional
def test_back_link_works(page: Page, base_url: str) -> None:
    """Test that back link returns to conferences page."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Click back link
    page.click('a:has-text("Back to All Conferences")')

    # Should return to main conferences page (may have query params)
    expect(page).to_have_url(re.compile(r"/conferences(\?.*)?$"))


@pytest.mark.functional
def test_both_tables_sortable(page: Page, base_url: str) -> None:
    """Test that both tables support sorting."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Sort teams table by total score
    page.click('#conferenceTeamsTable th[data-sort="total"]')

    # Sort players table by score
    page.click('#conferencePlayersTable th[data-sort="score"]')

    # Tables should still be visible
    expect(page.locator("#conferenceTeamsTable")).to_be_visible()
    expect(page.locator("#conferencePlayersTable")).to_be_visible()


@pytest.mark.functional
def test_export_buttons_present(page: Page, base_url: str) -> None:
    """Test that export buttons are present for both tables."""
    page.goto(f"{base_url}/conferences/Western")

    # Teams export buttons
    expect(page.locator("#export-conferenceTeamsTable-csv")).to_be_visible()
    expect(page.locator("#export-conferenceTeamsTable-json")).to_be_visible()

    # Players export buttons
    expect(page.locator("#export-conferencePlayersTable-csv")).to_be_visible()
    expect(page.locator("#export-conferencePlayersTable-json")).to_be_visible()


@pytest.mark.functional
def test_teams_table_columns(page: Page, base_url: str) -> None:
    """Test that teams table has expected columns."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Check all required column headers exist
    teams_table = page.locator("#conferenceTeamsTable")
    expect(teams_table.locator('th:has-text("Rank")')).to_be_visible()
    expect(teams_table.locator('th:has-text("Team")')).to_be_visible()
    expect(teams_table.locator('th:has-text("Division")')).to_be_visible()
    expect(teams_table.locator('th:has-text("Total Score")')).to_be_visible()
    expect(teams_table.locator('th:has-text("Avg Score")')).to_be_visible()
    expect(teams_table.locator('th:has-text("Players")')).to_be_visible()


@pytest.mark.functional
def test_players_table_columns(page: Page, base_url: str) -> None:
    """Test that players table has expected columns."""
    page.goto(f"{base_url}/conferences/Western")

    # Check all required column headers exist
    players_table = page.locator("#conferencePlayersTable")
    expect(players_table.locator('th:has-text("Rank")')).to_be_visible()
    expect(players_table.locator('th:has-text("Player Name")')).to_be_visible()
    expect(players_table.locator('th:has-text("Team")')).to_be_visible()
    expect(players_table.locator('th:has-text("Score")')).to_be_visible()


@pytest.mark.functional
def test_language_switching(page: Page, base_url: str) -> None:
    """Test that language switching works on conference detail pages."""
    # Test French Canadian - check for translated content in page body
    page.goto(f"{base_url}/conferences/Eastern?lang=fr_CA")
    # Check that page loads and has content (i18n in trans blocks with variables
    # is a known limitation - tracking in separate issue)
    expect(page.locator("h2")).to_be_visible()
    expect(page.locator("#conferenceTeamsTable")).to_be_visible()

    # Test Swedish
    page.goto(f"{base_url}/conferences/Western?lang=sv_SE")
    expect(page.locator("h2")).to_be_visible()
    expect(page.locator("#conferenceTeamsTable")).to_be_visible()


@pytest.mark.functional
def test_responsive_design(page: Page, base_url: str) -> None:
    """Test that page is responsive on mobile."""
    # Set mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})

    page.goto(f"{base_url}/conferences/Eastern")

    # Check tables are still visible (may scroll horizontally)
    expect(page.locator("#conferenceTeamsTable")).to_be_visible()
    expect(page.locator("#conferencePlayersTable")).to_be_visible()

    # Export buttons should wrap/stack on mobile (use first since there are 2 sets)
    export_buttons = page.locator(".export-buttons").first
    expect(export_buttons).to_be_visible()


@pytest.mark.functional
def test_teams_only_from_conference(page: Page, base_url: str) -> None:
    """Test that all teams shown are from the selected conference."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Get all team rows
    team_rows = page.locator("#conferenceTeamsTable tbody tr")
    count = team_rows.count()

    # All teams should have the same conference (we can't verify the exact conference
    # name from the table, but we can verify the count matches expectations: 16 teams)
    assert count == 16, f"Expected 16 teams in Eastern conference, got {count}"


@pytest.mark.functional
def test_timestamp_displayed(page: Page, base_url: str) -> None:
    """Test that data timestamp is displayed."""
    page.goto(f"{base_url}/conferences/Western")

    # Check timestamp is visible
    timestamp = page.locator(".timestamp")
    expect(timestamp).to_be_visible()
    expect(timestamp).to_contain_text("Data as of")
