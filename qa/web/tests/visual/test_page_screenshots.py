"""Visual regression tests for full page screenshots.

Tests capture full-page screenshots across all main pages and compare them against baseline images
to detect unintended visual changes, layout shifts, and styling errors.
"""

from pages.conferences_page import ConferencesPage
from pages.divisions_page import DivisionsPage
from pages.index_page import IndexPage
from pages.playoffs_page import PlayoffsPage
from pages.stats_page import StatsPage
from pages.teams_page import TeamsPage
from playwright.sync_api import expect


def test_index_page_visual(index_page: IndexPage) -> None:
    """Test full page screenshot of the index/home page.

    Captures the entire home page to detect:
    - Layout changes
    - Content shifts
    - Style modifications
    - Header/footer changes

    Args:
        index_page: IndexPage fixture instance
    """
    index_page.navigate()
    index_page.wait_for_load()

    # Full page screenshot comparison
    expect(index_page.page).to_have_screenshot(
        "index-page-full.png",
        full_page=True,
    )


def test_teams_page_visual(teams_page: TeamsPage) -> None:
    """Test full page screenshot of the teams page.

    Captures the entire teams standings page to detect:
    - Table layout changes
    - Column width adjustments
    - Sorting indicator changes
    - Score display modifications

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Full page screenshot comparison
    expect(teams_page.page).to_have_screenshot(
        "teams-page-full.png",
        full_page=True,
    )


def test_divisions_page_visual(divisions_page: DivisionsPage) -> None:
    """Test full page screenshot of the divisions page.

    Captures the entire divisions page to detect:
    - Division grouping layout
    - Team listing changes
    - Header styling
    - Division indicator changes

    Args:
        divisions_page: DivisionsPage fixture instance
    """
    divisions_page.navigate()
    divisions_page.wait_for_load()

    # Full page screenshot comparison
    expect(divisions_page.page).to_have_screenshot(
        "divisions-page-full.png",
        full_page=True,
    )


def test_conferences_page_visual(conferences_page: ConferencesPage) -> None:
    """Test full page screenshot of the conferences page.

    Captures the entire conferences page to detect:
    - Conference grouping layout
    - Team listing within conferences
    - Standings table changes
    - Conference header styling

    Args:
        conferences_page: ConferencesPage fixture instance
    """
    conferences_page.navigate()
    conferences_page.wait_for_load()

    # Full page screenshot comparison
    expect(conferences_page.page).to_have_screenshot(
        "conferences-page-full.png",
        full_page=True,
    )


def test_playoffs_page_visual(playoffs_page: PlayoffsPage) -> None:
    """Test full page screenshot of the playoffs page.

    Captures the entire playoffs bracket page to detect:
    - Bracket layout changes
    - Matchup positioning
    - Team placement
    - Playoff indicator changes

    Args:
        playoffs_page: PlayoffsPage fixture instance
    """
    playoffs_page.navigate()
    playoffs_page.wait_for_load()

    # Full page screenshot comparison
    expect(playoffs_page.page).to_have_screenshot(
        "playoffs-page-full.png",
        full_page=True,
    )


def test_stats_page_visual(stats_page: StatsPage) -> None:
    """Test full page screenshot of the stats page.

    Captures the entire stats page to detect:
    - Statistics table layout
    - Chart rendering changes
    - Data visualization modifications
    - Legend and label changes

    Args:
        stats_page: StatsPage fixture instance
    """
    stats_page.navigate()
    stats_page.wait_for_load()

    # Full page screenshot comparison
    expect(stats_page.page).to_have_screenshot(
        "stats-page-full.png",
        full_page=True,
    )


def test_index_page_viewport_visual(index_page: IndexPage) -> None:
    """Test viewport-only screenshot of the index page.

    Captures only the visible viewport (no scrolling) to detect:
    - Above-the-fold content changes
    - Hero section modifications
    - Navigation bar changes

    Args:
        index_page: IndexPage fixture instance
    """
    index_page.navigate()
    index_page.wait_for_load()

    # Viewport-only screenshot comparison
    expect(index_page.page).to_have_screenshot(
        "index-page-viewport.png",
        full_page=False,
    )


def test_teams_page_viewport_visual(teams_page: TeamsPage) -> None:
    """Test viewport-only screenshot of the teams page.

    Captures only the visible viewport to detect:
    - Table header changes
    - First few rows modifications
    - Filter/search bar changes

    Args:
        teams_page: TeamsPage fixture instance
    """
    teams_page.navigate()
    teams_page.wait_for_load()

    # Viewport-only screenshot comparison
    expect(teams_page.page).to_have_screenshot(
        "teams-page-viewport.png",
        full_page=False,
    )
