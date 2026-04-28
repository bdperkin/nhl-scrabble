"""Visual regression tests for component-level screenshots.

Tests capture individual UI components (tables, cards, headers, etc.) to detect:
- Component-specific styling changes
- Layout shifts within components
- Typography and color changes
- Spacing and alignment issues
"""

from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.teams_page import TeamsPage
from playwright.sync_api import expect


def test_navigation_bar_visual(index_page: IndexPage) -> None:
    """Test screenshot of the navigation bar component.

    Captures the navigation bar to detect:
    - Menu item changes
    - Link styling
    - Logo modifications
    - Spacing changes

    Args:
        index_page: IndexPage fixture instance
    """
    index_page.navigate()
    index_page.wait_for_load()

    # Navigation bar component screenshot
    nav_bar = index_page.page.locator("nav, header nav, .navbar")
    if nav_bar.count() > 0:
        expect(nav_bar.first).to_have_screenshot("component-nav-bar.png")


def test_page_header_visual(teams_page: TeamsPage) -> None:
    """Test screenshot of page header component.

    Captures the page title and header section to detect:
    - Title styling changes
    - Header layout modifications
    - Breadcrumb changes
    - Action button styling

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Page header component screenshot
    header = teams_page.page.locator("h1, .page-header, header.page-title")
    if header.count() > 0:
        expect(header.first).to_have_screenshot("component-page-header.png")


def test_standings_table_visual(teams_page: TeamsPage) -> None:
    """Test screenshot of standings table component.

    Captures the standings table to detect:
    - Table styling changes
    - Column width adjustments
    - Row striping modifications
    - Border and spacing changes

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Standings table component screenshot
    table = teams_page.page.locator("table")
    if table.count() > 0:
        expect(table.first).to_have_screenshot("component-standings-table.png")


def test_table_header_visual(teams_page: TeamsPage) -> None:
    """Test screenshot of table header component.

    Captures the table header to detect:
    - Header cell styling
    - Sort indicator changes
    - Column header text changes
    - Background and border modifications

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Table header component screenshot
    thead = teams_page.page.locator("table thead")
    if thead.count() > 0:
        expect(thead.first).to_have_screenshot("component-table-header.png")


def test_table_row_visual(teams_page: TeamsPage) -> None:
    """Test screenshot of first table row component.

    Captures a single table row to detect:
    - Cell alignment changes
    - Text styling modifications
    - Padding and spacing changes
    - Border styling

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # First table row component screenshot
    first_row = teams_page.page.locator("table tbody tr").first
    if first_row.count() > 0:
        expect(first_row).to_have_screenshot("component-table-row.png")


def test_division_group_visual(divisions_page: DivisionsPage) -> None:
    """Test screenshot of division group component.

    Captures a single division group to detect:
    - Division header styling
    - Team list layout
    - Group container styling
    - Spacing between divisions

    Args:
        divisions_page: DivisionsPage fixture instance
    """
    divisions_page.navigate()
    divisions_page.wait_for_load()

    # Division group component screenshot
    division_group = divisions_page.page.locator(".division, .division-group, section.division")
    if division_group.count() > 0:
        expect(division_group.first).to_have_screenshot("component-division-group.png")


def test_conference_section_visual(conferences_page: ConferencesPage) -> None:
    """Test screenshot of conference section component.

    Captures a single conference section to detect:
    - Conference header styling
    - Team standings layout
    - Section container styling
    - Spacing between conferences

    Args:
        conferences_page: ConferencesPage fixture instance
    """
    conferences_page.navigate()
    conferences_page.wait_for_load()

    # Conference section component screenshot
    conference_section = conferences_page.page.locator(
        ".conference, .conference-group, section.conference",
    )
    if conference_section.count() > 0:
        expect(conference_section.first).to_have_screenshot("component-conference-section.png")


def test_playoff_bracket_visual(playoffs_page: PlayoffsPage) -> None:
    """Test screenshot of playoff bracket component.

    Captures the playoff bracket structure to detect:
    - Bracket layout changes
    - Matchup positioning
    - Connector line styling
    - Team placement

    Args:
        playoffs_page: PlayoffsPage fixture instance
    """
    playoffs_page.navigate()
    playoffs_page.wait_for_load()

    # Playoff bracket component screenshot
    bracket = playoffs_page.page.locator(".playoff-bracket, .bracket, section.playoffs")
    if bracket.count() > 0:
        expect(bracket.first).to_have_screenshot("component-playoff-bracket.png")


def test_playoff_matchup_visual(playoffs_page: PlayoffsPage) -> None:
    """Test screenshot of single playoff matchup component.

    Captures a single matchup to detect:
    - Matchup card styling
    - Team name display
    - Seed number formatting
    - Connector styling

    Args:
        playoffs_page: PlayoffsPage fixture instance
    """
    playoffs_page.navigate()
    playoffs_page.wait_for_load()

    # Single playoff matchup component screenshot
    matchup = playoffs_page.page.locator(".matchup, .playoff-matchup")
    if matchup.count() > 0:
        expect(matchup.first).to_have_screenshot("component-playoff-matchup.png")


def test_footer_visual(index_page: IndexPage) -> None:
    """Test screenshot of page footer component.

    Captures the footer to detect:
    - Footer layout changes
    - Link styling modifications
    - Copyright text changes
    - Social media icon updates

    Args:
        index_page: IndexPage fixture instance
    """
    index_page.navigate()
    index_page.wait_for_load()

    # Footer component screenshot
    footer = index_page.page.locator("footer, .footer, .page-footer")
    if footer.count() > 0:
        expect(footer.first).to_have_screenshot("component-footer.png")
