"""Automated accessibility scans using axe-core for WCAG 2.1 compliance.

This module contains automated accessibility tests that scan all pages
of the NHL Scrabble web application using axe-core to detect WCAG
violations.

The tests check for:
- Color contrast issues
- Missing ARIA attributes
- Form label associations
- Heading hierarchy
- Alt text for images
- Keyboard accessibility
- Screen reader compatibility

Each test scans a specific page and asserts zero critical/serious violations.
"""

import shutil

import pytest
from axe_playwright_python.sync_playwright import Axe
from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage

# Skip all tests if axe-playwright-python is not installed
pytestmark = pytest.mark.skipif(
    shutil.which("node") is None,
    reason="Node.js not found (required for axe-core engine)",
)


@pytest.mark.accessibility
def test_index_page_accessibility(index_page: IndexPage) -> None:
    """Test homepage for accessibility violations.

    Scans the homepage using axe-core and asserts no WCAG violations.
    This is a critical page that should be fully accessible.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(index_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on homepage:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_teams_page_accessibility(teams_page: TeamsPage) -> None:
    """Test teams page for accessibility violations.

    Scans the teams page using axe-core and asserts no WCAG violations.
    Tests tables, data display, and navigation elements.

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(teams_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on teams page:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_divisions_page_accessibility(divisions_page: DivisionsPage) -> None:
    """Test divisions page for accessibility violations.

    Scans the divisions page using axe-core and asserts no WCAG violations.
    Tests complex data structures and nested tables.

    Args:
        divisions_page: DivisionsPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to divisions page
    divisions_page.navigate()
    divisions_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(divisions_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on divisions page:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_conferences_page_accessibility(conferences_page: ConferencesPage) -> None:
    """Test conferences page for accessibility violations.

    Scans the conferences page using axe-core and asserts no WCAG violations.
    Tests conference standings and data presentation.

    Args:
        conferences_page: ConferencesPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to conferences page
    conferences_page.navigate()
    conferences_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(conferences_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on conferences page:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_playoffs_page_accessibility(playoffs_page: PlayoffsPage) -> None:
    """Test playoffs page for accessibility violations.

    Scans the playoffs page using axe-core and asserts no WCAG violations.
    Tests playoff brackets and tournament structure.

    Args:
        playoffs_page: PlayoffsPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to playoffs page
    playoffs_page.navigate()
    playoffs_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(playoffs_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on playoffs page:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_stats_page_accessibility(stats_page: StatsPage) -> None:
    """Test stats page for accessibility violations.

    Scans the stats page using axe-core and asserts no WCAG violations.
    Tests statistical data presentation and charts.

    Args:
        stats_page: StatsPage fixture

    Raises:
        AssertionError: If any accessibility violations are found
    """
    # Navigate to stats page
    stats_page.navigate()
    stats_page.wait_for_load()

    # Run axe accessibility scan
    axe = Axe()
    results = axe.run(stats_page.page)

    # Assert no violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} accessibility violations on stats page:\n"
        f"{results.generate_report()}"
    )


@pytest.mark.accessibility
@pytest.mark.parametrize(
    ("page_name", "page_fixture_name"),
    [
        ("index", "index_page"),
        ("teams", "teams_page"),
        ("divisions", "divisions_page"),
        ("conferences", "conferences_page"),
        ("playoffs", "playoffs_page"),
        ("stats", "stats_page"),
    ],
)
def test_all_pages_wcag_aa_compliance(
    page_name: str,
    page_fixture_name: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test all pages for WCAG 2.1 Level AA compliance.

    Parametrized test that scans all pages and specifically checks for
    WCAG 2.1 Level AA compliance. This is the target compliance level
    for the application.

    Args:
        page_name: Name of the page being tested
        page_fixture_name: Name of the pytest fixture for the page
        request: Pytest fixture request object

    Raises:
        AssertionError: If WCAG AA violations are found
    """
    # Get the page fixture dynamically
    page = request.getfixturevalue(page_fixture_name)

    # Navigate to the page
    page.navigate()
    page.wait_for_load()

    # Run axe with WCAG 2.1 Level AA rules only
    axe = Axe()
    results = axe.run(
        page.page,
        options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
            },
        },
    )

    # Assert WCAG AA compliance
    assert results.violations_count == 0, (
        f"Found {results.violations_count} WCAG 2.1 AA violations on {page_name} page:\n"
        f"{results.generate_report()}"
    )
