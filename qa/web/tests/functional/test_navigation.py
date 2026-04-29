"""Functional tests for navigation and page structure."""

import pytest
from pages.index_page import IndexPage
from playwright.sync_api import Page, expect


@pytest.mark.functional
@pytest.mark.navigation
def test_homepage_loads(index_page: IndexPage) -> None:
    """Verify homepage loads successfully.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Wait for page to load
    index_page.wait_for_load()

    # Verify page loaded
    assert index_page.page.url.endswith("/"), "Should be on homepage"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_page_title(index_page: IndexPage) -> None:
    """Verify page title is correct.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Verify page title
    title = index_page.get_title()
    assert "NHL Scrabble" in title, "Page title should contain 'NHL Scrabble'"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_welcome_message(index_page: IndexPage) -> None:
    """Verify welcome message is displayed.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Get welcome message
    welcome = index_page.get_welcome_message()

    # Verify message exists and is not empty
    assert welcome is not None, "Welcome message should exist"  # noqa: S101
    assert len(welcome) > 0, "Welcome message should not be empty"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_page_header_elements(index_page: IndexPage) -> None:
    """Verify page header contains expected elements.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Check for header
    assert index_page.is_visible("header"), "Page should have header"  # noqa: S101

    # Check for title/logo
    assert index_page.is_visible("h1"), "Page should have h1 title"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_page_structure(index_page: IndexPage) -> None:
    """Verify page has expected structural elements.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Check for main content areas
    assert index_page.is_visible(".hero"), "Page should have hero section"  # noqa: S101
    assert index_page.is_visible(
        ".analysis-form-section",
    ), "Page should have form section"  # noqa: S101
    assert index_page.is_visible(".info-section"), "Page should have info section"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_form_elements_present(index_page: IndexPage) -> None:
    """Verify analysis form elements are present.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Check for form
    assert index_page.is_visible("#analysisForm"), "Analysis form should be present"  # noqa: S101

    # Check for form inputs
    assert index_page.is_visible("#topPlayers"), "Top players input should be present"  # noqa: S101
    assert index_page.is_visible(  # noqa: S101
        "#topTeamPlayers",
    ), "Top team players input should be present"
    assert index_page.is_visible("#useCache"), "Use cache checkbox should be present"  # noqa: S101

    # Check for submit button
    assert index_page.is_visible("#analyzeBtn"), "Analyze button should be present"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_form_default_values(page_fixture: Page) -> None:
    """Verify form has correct default values.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Check default values
    top_players = page_fixture.locator("#topPlayers").input_value()
    assert top_players == "20", "Default top players should be 20"  # noqa: S101

    top_team_players = page_fixture.locator("#topTeamPlayers").input_value()
    assert top_team_players == "5", "Default top team players should be 5"  # noqa: S101

    # Check cache checkbox is checked by default
    is_checked = page_fixture.locator("#useCache").is_checked()
    assert is_checked, "Use cache should be checked by default"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_results_container_hidden_initially(index_page: IndexPage) -> None:
    """Verify results container is hidden before analysis.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Results should be hidden initially
    assert index_page.is_hidden("#results"), "Results should be hidden initially"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_error_container_hidden_initially(index_page: IndexPage) -> None:
    """Verify error container is hidden initially.

    Args:
        index_page: IndexPage fixture
    """
    # Navigate to homepage
    index_page.navigate()

    # Error container should be hidden initially
    assert index_page.is_hidden(
        "#error",
    ), "Error container should be hidden initially"  # noqa: S101


@pytest.mark.functional
@pytest.mark.navigation
def test_info_section_content(page_fixture: Page) -> None:
    """Verify info section contains expected content.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to homepage
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Check for info section
    info_section = page_fixture.locator(".info-section")
    expect(info_section).to_be_visible()

    # Check for about heading
    about_heading = page_fixture.locator(".info-section h3")
    expect(about_heading).to_contain_text("About")

    # Check for Scrabble values
    values_heading = page_fixture.locator(".info-section h4")
    expect(values_heading).to_contain_text("Scrabble Letter Values")


@pytest.mark.functional
@pytest.mark.navigation
def test_health_endpoint(page_fixture: Page) -> None:
    """Verify health check endpoint is accessible.

    Args:
        page_fixture: Playwright page fixture
    """
    # Navigate to health endpoint
    response = page_fixture.goto("http://localhost:5000/health")

    # Should return 200 OK
    assert response is not None, "Response should not be None"  # noqa: S101
    assert response.ok, "Health endpoint should return 200 OK"  # noqa: S101
