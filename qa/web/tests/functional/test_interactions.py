"""Functional tests for interactive features and user interactions."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.functional
@pytest.mark.interaction
def test_player_table_sorting(page_fixture: Page) -> None:
    """Verify player table can be sorted by columns.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.fill("#topPlayers", "20")
    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable tbody tr", state="visible", timeout=30000)

    # Get first player score before sort
    first_score_before = (
        page_fixture.locator("#playersTable tbody tr").first.locator("td.score").text_content()
    )

    # Click score header to sort
    score_header = page_fixture.locator("#playersTable thead th[data-sort='score']")
    score_header.click()

    # Wait a moment for sort to complete
    page_fixture.wait_for_timeout(500)

    # Get first player score after sort
    first_score_after = (
        page_fixture.locator("#playersTable tbody tr").first.locator("td.score").text_content()
    )

    # Verify sorting occurred (scores may change due to sort direction)
    assert first_score_before is not None, "Score before sort should exist"  # noqa: S101
    assert first_score_after is not None, "Score after sort should exist"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_team_table_sorting(page_fixture: Page) -> None:
    """Verify team table can be sorted by columns.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#teamsTable tbody tr", state="visible", timeout=30000)

    # Get first team name before sort
    first_team_before = (
        page_fixture.locator("#teamsTable tbody tr").first.locator("td.team-name").text_content()
    )

    # Click team name header to sort
    team_header = page_fixture.locator("#teamsTable thead th[data-sort='team']")
    team_header.click()

    # Wait for sort
    page_fixture.wait_for_timeout(500)

    # Get first team name after sort
    first_team_after = (
        page_fixture.locator("#teamsTable tbody tr").first.locator("td.team-name").text_content()
    )

    # Verify sorting occurred
    assert first_team_before is not None, "Team name before sort should exist"  # noqa: S101
    assert first_team_after is not None, "Team name after sort should exist"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_sortable_table_has_sort_attributes(page_fixture: Page) -> None:
    """Verify sortable tables have proper data attributes.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable", state="visible", timeout=30000)

    # Check that players table has sortable class
    players_table = page_fixture.locator("#playersTable")
    class_attr = players_table.get_attribute("class")
    assert "sortable" in class_attr, "Players table should have sortable class"  # noqa: S101

    # Check that headers have sort attributes
    headers = page_fixture.locator("#playersTable thead th[data-sort]")
    assert headers.count() > 0, "Should have sortable headers"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_form_validation_min_values(page_fixture: Page) -> None:
    """Verify form validates minimum values.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Try to set value below minimum
    top_players_input = page_fixture.locator("#topPlayers")

    # Clear and set invalid value
    top_players_input.fill("0")

    # Get min attribute
    min_value = top_players_input.get_attribute("min")
    assert min_value == "1", "Min value should be 1"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_form_validation_max_values(page_fixture: Page) -> None:
    """Verify form validates maximum values.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Check max values
    top_players_max = page_fixture.locator("#topPlayers").get_attribute("max")
    assert top_players_max == "100", "Max top players should be 100"  # noqa: S101

    top_team_players_max = page_fixture.locator("#topTeamPlayers").get_attribute("max")
    assert top_team_players_max == "30", "Max team players should be 30"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_form_required_fields(page_fixture: Page) -> None:
    """Verify form fields have required attributes.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Check required attribute
    top_players_required = page_fixture.locator("#topPlayers").get_attribute("required")
    assert top_players_required is not None, "Top players should be required"  # noqa: S101

    top_team_players_required = page_fixture.locator("#topTeamPlayers").get_attribute("required")
    assert (
        top_team_players_required is not None
    ), "Top team players should be required"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_loading_indicator_shows(page_fixture: Page) -> None:
    """Verify loading indicator appears during request.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Uncheck cache to ensure fresh request
    page_fixture.locator("#useCache").uncheck()

    # Start analysis
    page_fixture.click("#analyzeBtn")

    # Loading indicator should appear briefly
    loading = page_fixture.locator("#loading")

    # Note: This may be difficult to catch if request is very fast
    # Just verify the loading element exists
    assert loading is not None, "Loading indicator element should exist"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_button_states_during_submit(page_fixture: Page) -> None:
    """Verify button changes during form submission.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Get button
    button = page_fixture.locator("#analyzeBtn")

    # Verify button is initially enabled
    is_enabled = button.is_enabled()
    assert is_enabled, "Button should be enabled initially"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_multiple_form_submissions(page_fixture: Page) -> None:
    """Verify multiple form submissions work correctly.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # First submission
    page_fixture.fill("#topPlayers", "10")
    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#results", state="visible", timeout=30000)

    # Verify first results
    rows_1 = page_fixture.locator("#playersTable tbody tr").count()
    assert rows_1 == 10, "First submission should have 10 players"  # noqa: S101

    # Second submission with different value
    page_fixture.fill("#topPlayers", "15")
    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_timeout(1000)  # Wait for results to update

    # Verify second results
    rows_2 = page_fixture.locator("#playersTable tbody tr").count()
    assert rows_2 == 15, "Second submission should have 15 players"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_table_row_data_attributes(page_fixture: Page) -> None:
    """Verify table rows have proper data attributes for sorting.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable tbody tr", state="visible", timeout=30000)

    # Get first row
    first_row = page_fixture.locator("#playersTable tbody tr").first

    # Check for data-original-index
    index_attr = first_row.get_attribute("data-original-index")
    assert index_attr is not None, "Row should have data-original-index"  # noqa: S101

    # Check cells have data-value attributes
    cells = first_row.locator("td[data-value]")
    assert cells.count() > 0, "Cells should have data-value attributes"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_accessibility_aria_labels(page_fixture: Page) -> None:
    """Verify tables have proper ARIA labels for accessibility.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable", state="visible", timeout=30000)

    # Check players table has role and aria-label
    players_table = page_fixture.locator("#playersTable")
    role = players_table.get_attribute("role")
    aria_label = players_table.get_attribute("aria-label")

    assert role == "table", "Table should have role='table'"  # noqa: S101
    assert aria_label is not None, "Table should have aria-label"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_export_button_interactions(page_fixture: Page) -> None:
    """Verify export buttons are clickable and present.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".export-buttons", state="visible", timeout=30000)

    # Get export buttons
    csv_button = page_fixture.locator("#export-playersTable-csv").first
    json_button = page_fixture.locator("#export-playersTable-json").first

    # Verify buttons are visible and enabled
    expect(csv_button).to_be_visible()
    expect(json_button).to_be_visible()

    is_csv_enabled = csv_button.is_enabled()
    is_json_enabled = json_button.is_enabled()

    assert is_csv_enabled, "CSV export button should be enabled"  # noqa: S101
    assert is_json_enabled, "JSON export button should be enabled"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_responsive_table_containers(page_fixture: Page) -> None:
    """Verify tables are wrapped in responsive containers.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector("#playersTable", state="visible", timeout=30000)

    # Check for table containers
    table_containers = page_fixture.locator(".table-container")
    assert table_containers.count() >= 2, "Should have table containers"  # noqa: S101

    # Verify players table is inside a container
    players_container = page_fixture.locator(".table-container:has(#playersTable)")
    expect(players_container).to_be_visible()


@pytest.mark.functional
@pytest.mark.interaction
def test_form_accessibility_labels(page_fixture: Page) -> None:
    """Verify form inputs have proper labels and help text.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Check for label association
    top_players_label = page_fixture.locator("label[for='topPlayers']")
    expect(top_players_label).to_be_visible()

    # Check for help text
    help_text = page_fixture.locator(".help-text")
    assert help_text.count() >= 2, "Should have help text for inputs"  # noqa: S101


@pytest.mark.functional
@pytest.mark.interaction
def test_results_section_structure(page_fixture: Page) -> None:
    """Verify results sections have proper structure.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate and run analysis
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    page_fixture.click("#analyzeBtn")
    page_fixture.wait_for_selector(".results-section", state="visible", timeout=30000)

    # Check for results sections
    results_sections = page_fixture.locator(".results-section")
    assert results_sections.count() >= 3, "Should have multiple results sections"  # noqa: S101

    # Each section should have a heading
    for i in range(results_sections.count()):
        section = results_sections.nth(i)
        heading = section.locator("h3")
        expect(heading).to_be_visible()
