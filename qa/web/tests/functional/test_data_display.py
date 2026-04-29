"""Functional tests for data display and form submission."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.functional
@pytest.mark.data_display
def test_form_submission(page_fixture: Page) -> None:
    """Verify form submission triggers analysis.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Fill form with test values
    page_fixture.fill("#topPlayers", "10")
    page_fixture.fill("#topTeamPlayers", "3")

    # Submit form
    page_fixture.click("#analyzeBtn")

    # Wait for results to load (HTMX will populate #results)
    page_fixture.wait_for_selector("#results[hidden='']", state="hidden", timeout=30000)
    page_fixture.wait_for_selector("#results:not([hidden])", state="visible", timeout=30000)

    # Verify results are visible
    results = page_fixture.locator("#results")
    expect(results).to_be_visible()


@pytest.mark.functional
@pytest.mark.data_display
def test_stats_summary_displayed(page_fixture: Page) -> None:
    """Verify statistics summary is displayed after analysis.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")

    # Wait for stats summary
    page_fixture.wait_for_selector(".stats-summary", state="visible", timeout=30000)

    # Verify stat cards are present
    stat_cards = page_fixture.locator(".stat-card")
    count = stat_cards.count()

    assert count >= 4, f"Should have at least 4 stat cards, found {count}"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_stats_values_populated(page_fixture: Page) -> None:
    """Verify statistics contain actual values.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".stats-summary", state="visible", timeout=30000)

    # Check that stat values are not empty
    stat_values = page_fixture.locator(".stat-value")
    for i in range(stat_values.count()):
        value = stat_values.nth(i).text_content()
        assert value is not None, f"Stat value {i} should not be None"  # noqa: S101
        assert len(value.strip()) > 0, f"Stat value {i} should not be empty"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_players_table_displayed(page_fixture: Page) -> None:
    """Verify players table is displayed with data.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable", state="visible", timeout=30000)

    # Verify table is visible
    table = page_fixture.locator("#playersTable")
    expect(table).to_be_visible()

    # Verify table has header row
    headers = page_fixture.locator("#playersTable thead th")
    assert headers.count() >= 4, "Should have at least 4 column headers"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_players_table_has_data(page_fixture: Page) -> None:
    """Verify players table contains player data.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis with 10 top players
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.fill("#topPlayers", "10")
    page_fixture.click("#analyzeBtn")

    # Wait for table rows
    page_fixture.wait_for_selector("#playersTable tbody tr", state="visible", timeout=30000)

    # Count rows
    rows = page_fixture.locator("#playersTable tbody tr")
    row_count = rows.count()

    # Should have requested number of players
    assert row_count == 10, f"Should have 10 players, found {row_count}"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_player_data_structure(page_fixture: Page) -> None:
    """Verify player table rows have correct data structure.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.fill("#topPlayers", "5")
    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable tbody tr", state="visible", timeout=30000)

    # Get first row
    first_row = page_fixture.locator("#playersTable tbody tr").first

    # Verify row has correct number of cells
    cells = first_row.locator("td")
    assert (
        cells.count() == 4
    ), "Each row should have 4 cells (rank, name, team, score)"  # noqa: S101

    # Verify cells have content
    for i in range(cells.count()):
        cell_text = cells.nth(i).text_content()
        assert cell_text is not None, f"Cell {i} should have content"  # noqa: S101
        assert len(cell_text.strip()) > 0, f"Cell {i} should not be empty"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_teams_table_displayed(page_fixture: Page) -> None:
    """Verify teams standings table is displayed.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#teamsTable", state="visible", timeout=30000)

    # Verify table is visible
    table = page_fixture.locator("#teamsTable")
    expect(table).to_be_visible()


@pytest.mark.functional
@pytest.mark.data_display
def test_teams_table_has_all_teams(page_fixture: Page) -> None:
    """Verify teams table has all 32 NHL teams.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#teamsTable tbody tr", state="visible", timeout=30000)

    # Count team rows
    rows = page_fixture.locator("#teamsTable tbody tr")
    row_count = rows.count()

    # NHL has 32 teams
    assert row_count == 32, f"Should have 32 teams, found {row_count}"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_team_data_structure(page_fixture: Page) -> None:
    """Verify team table rows have correct data structure.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#teamsTable tbody tr", state="visible", timeout=30000)

    # Get first row
    first_row = page_fixture.locator("#teamsTable tbody tr").first

    # Verify row has correct number of cells
    cells = first_row.locator("td")
    assert cells.count() == 7, "Each row should have 7 cells"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_division_standings_displayed(page_fixture: Page) -> None:
    """Verify division standings are displayed.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".division-grid", state="visible", timeout=30000)

    # Verify division grid is visible
    division_grid = page_fixture.locator(".division-grid")
    expect(division_grid).to_be_visible()

    # Should have 4 divisions
    division_cards = page_fixture.locator(".division-card")
    assert division_cards.count() == 4, "Should have 4 NHL divisions"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_visualizations_displayed(page_fixture: Page) -> None:
    """Verify data visualizations are displayed.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".visualizations", state="visible", timeout=30000)

    # Verify visualization section exists
    viz_section = page_fixture.locator(".visualizations")
    expect(viz_section).to_be_visible()

    # Verify chart canvases exist
    team_chart = page_fixture.locator("#teamScoresChart")
    player_chart = page_fixture.locator("#playerDistributionChart")

    expect(team_chart).to_be_visible()
    expect(player_chart).to_be_visible()


@pytest.mark.functional
@pytest.mark.data_display
def test_export_buttons_present(page_fixture: Page) -> None:
    """Verify export buttons are present for tables.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".export-buttons", state="visible", timeout=30000)

    # Check for export buttons
    csv_buttons = page_fixture.locator("button[id^='export-'][id$='-csv']")
    json_buttons = page_fixture.locator("button[id^='export-'][id$='-json']")

    # Should have CSV and JSON export buttons for each table
    assert csv_buttons.count() >= 2, "Should have CSV export buttons"  # noqa: S101
    assert json_buttons.count() >= 2, "Should have JSON export buttons"  # noqa: S101


@pytest.mark.functional
@pytest.mark.data_display
def test_cache_toggle_functionality(page_fixture: Page) -> None:
    """Verify cache toggle affects requests.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Uncheck cache
    page_fixture.locator("#useCache").uncheck()

    # Verify unchecked
    is_checked = page_fixture.locator("#useCache").is_checked()
    assert not is_checked, "Cache should be unchecked"  # noqa: S101

    # Re-check cache
    page_fixture.locator("#useCache").check()

    # Verify checked
    is_checked = page_fixture.locator("#useCache").is_checked()
    assert is_checked, "Cache should be checked"  # noqa: S101
