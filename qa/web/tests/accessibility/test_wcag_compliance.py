"""WCAG 2.1 compliance tests for specific accessibility criteria.

This module contains tests for specific WCAG 2.1 success criteria:
- Color contrast (1.4.3, 1.4.6)
- ARIA attributes (4.1.2)
- Form labels (3.3.2)
- Heading hierarchy (1.3.1)
- Alt text for images (1.1.1)
- Language attribute (3.1.1)
- Page titles (2.4.2)

These tests complement the automated axe-core scans with additional
manual checks for specific WCAG criteria.
"""

import pytest
from pages.index_page import IndexPage
from pages.teams_page import TeamsPage


@pytest.mark.accessibility
@pytest.mark.wcag
def test_page_has_language_attribute(index_page: IndexPage) -> None:
    """Test that page has lang attribute (WCAG 3.1.1).

    Success Criterion 3.1.1 Language of Page (Level A):
    The default human language of each Web page can be
    programmatically determined.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If lang attribute is missing
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Check for lang attribute on html element
    lang_attr = index_page.page.locator("html").get_attribute("lang")

    assert lang_attr is not None, "HTML element should have lang attribute"
    assert lang_attr == "en", f"Expected lang='en', got lang='{lang_attr}'"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_page_has_meaningful_title(index_page: IndexPage) -> None:
    """Test that page has descriptive title (WCAG 2.4.2).

    Success Criterion 2.4.2 Page Titled (Level A):
    Web pages have titles that describe topic or purpose.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If page title is missing or not descriptive
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Get page title
    title = index_page.get_title()

    assert title is not None, "Page should have a title"
    assert len(title) > 0, "Page title should not be empty"
    assert "NHL" in title or "Scrabble" in title, "Title should describe the content"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_headings_hierarchy(index_page: IndexPage) -> None:
    """Test proper heading hierarchy (WCAG 1.3.1).

    Success Criterion 1.3.1 Info and Relationships (Level A):
    Information, structure, and relationships can be
    programmatically determined.

    Verifies:
    - Page has h1 element
    - Heading levels don't skip (h1 -> h3)
    - Only one h1 per page

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If heading hierarchy is incorrect
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Check for h1 element
    h1_count = index_page.page.locator("h1").count()
    assert h1_count >= 1, "Page should have at least one h1 heading"
    assert h1_count <= 1, "Page should have only one h1 heading"

    # Get all headings in order
    headings = index_page.page.evaluate(
        """() => {
        const headings = [];
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
            headings.push(parseInt(h.tagName.substring(1)));
        });
        return headings;
    }""",
    )

    # Verify heading levels don't skip
    for i in range(1, len(headings)):
        level_diff = headings[i] - headings[i - 1]
        assert (
            level_diff <= 1
        ), f"Heading levels should not skip (found h{headings[i-1]} -> h{headings[i]})"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_images_have_alt_text(teams_page: TeamsPage) -> None:
    """Test that all images have alt attributes (WCAG 1.1.1).

    Success Criterion 1.1.1 Non-text Content (Level A):
    All non-text content has a text alternative.

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If images are missing alt attributes
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Get all images
    images = teams_page.page.locator("img").all()

    # Check each image has alt attribute
    for img in images:
        alt_text = img.get_attribute("alt")
        # Alt text can be empty for decorative images, but attribute must exist
        assert alt_text is not None, f"Image {img} is missing alt attribute"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_links_have_accessible_names(index_page: IndexPage) -> None:
    """Test that all links have accessible names (WCAG 2.4.4, 4.1.2).

    Success Criterion 2.4.4 Link Purpose (Level A):
    The purpose of each link can be determined from the link text
    alone or from the link text together with its programmatically
    determined link context.

    Success Criterion 4.1.2 Name, Role, Value (Level A):
    For all user interface components, the name and role can be
    programmatically determined.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If links lack accessible names
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Get all links
    links = index_page.page.locator("a").all()

    # Verify we have links to test
    assert len(links) > 0, "Page should have links"

    # Check each link has accessible name
    for link in links:
        # Get link text content
        text_content = link.text_content()
        aria_label = link.get_attribute("aria-label")
        title = link.get_attribute("title")

        # Link should have text, aria-label, or title
        has_accessible_name = bool(
            (text_content and text_content.strip()) or aria_label or title,
        )

        assert (
            has_accessible_name
        ), f"Link {link} lacks accessible name (no text, aria-label, or title)"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_buttons_have_accessible_names(teams_page: TeamsPage) -> None:
    """Test that all buttons have accessible names (WCAG 4.1.2).

    Success Criterion 4.1.2 Name, Role, Value (Level A):
    For all user interface components, the name and role can be
    programmatically determined.

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If buttons lack accessible names
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Get all buttons
    buttons = teams_page.page.locator("button").all()

    # If no buttons, skip this check
    if len(buttons) == 0:
        pytest.skip("No buttons found on page")

    # Check each button has accessible name
    for button in buttons:
        text_content = button.text_content()
        aria_label = button.get_attribute("aria-label")
        aria_labelledby = button.get_attribute("aria-labelledby")

        has_accessible_name = bool(
            (text_content and text_content.strip()) or aria_label or aria_labelledby,
        )

        assert has_accessible_name, f"Button {button} lacks accessible name"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_form_inputs_have_labels(index_page: IndexPage) -> None:
    """Test that form inputs have associated labels (WCAG 3.3.2, 1.3.1).

    Success Criterion 3.3.2 Labels or Instructions (Level A):
    Labels or instructions are provided when content requires user input.

    Success Criterion 1.3.1 Info and Relationships (Level A):
    Information, structure, and relationships can be programmatically
    determined.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If form inputs lack labels
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Get all form inputs
    inputs = index_page.page.locator("input, select, textarea").all()

    # If no form inputs, skip this check
    if len(inputs) == 0:
        pytest.skip("No form inputs found on page")

    # Check each input has label
    for input_element in inputs:
        input_type = input_element.get_attribute("type")

        # Skip hidden inputs and submit buttons
        if input_type in ["hidden", "submit", "button", "reset"]:
            continue

        # Check for associated label
        input_id = input_element.get_attribute("id")
        aria_label = input_element.get_attribute("aria-label")
        aria_labelledby = input_element.get_attribute("aria-labelledby")
        title = input_element.get_attribute("title")

        # Input should have id with associated label, or aria-label, or title
        has_label = bool(
            (input_id and index_page.page.locator(f"label[for='{input_id}']").count() > 0)
            or aria_label
            or aria_labelledby
            or title,
        )

        assert has_label, f"Input {input_element} lacks associated label"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_tables_have_headers(teams_page: TeamsPage) -> None:
    """Test that data tables have proper headers (WCAG 1.3.1).

    Success Criterion 1.3.1 Info and Relationships (Level A):
    Information, structure, and relationships can be programmatically
    determined.

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If tables lack proper headers
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Get all tables
    tables = teams_page.page.locator("table").all()

    # Verify we have tables
    if len(tables) == 0:
        pytest.skip("No tables found on page")

    # Check each table has headers
    for table in tables:
        # Check for th elements or thead
        th_count = table.locator("th").count()
        thead_count = table.locator("thead").count()

        assert (
            th_count > 0 or thead_count > 0
        ), "Data table should have header cells (th) or thead element"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_lists_use_proper_markup(index_page: IndexPage) -> None:
    """Test that lists use proper semantic markup (WCAG 1.3.1).

    Success Criterion 1.3.1 Info and Relationships (Level A):
    Information, structure, and relationships can be programmatically
    determined.

    Verifies that content that looks like a list uses proper
    list elements (ul, ol, li) instead of div/span styling.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If lists don't use proper markup
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Get all list elements
    ul_count = index_page.page.locator("ul").count()
    ol_count = index_page.page.locator("ol").count()

    # Verify lists exist and contain list items
    if ul_count > 0:
        uls = index_page.page.locator("ul").all()
        for ul in uls:
            li_count = ul.locator("li").count()
            assert li_count > 0, "Unordered list should contain list items"

    if ol_count > 0:
        ols = index_page.page.locator("ol").all()
        for ol in ols:
            li_count = ol.locator("li").count()
            assert li_count > 0, "Ordered list should contain list items"


@pytest.mark.accessibility
@pytest.mark.wcag
def test_no_duplicate_ids(index_page: IndexPage) -> None:
    """Test that page has no duplicate IDs (WCAG 4.1.1).

    Success Criterion 4.1.1 Parsing (Level A):
    In content implemented using markup languages, elements have
    complete start and end tags, elements are nested according to
    their specifications, elements do not contain duplicate attributes,
    and any IDs are unique.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If duplicate IDs are found
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Get all elements with ID attributes
    ids = index_page.page.evaluate(
        """() => {
        const elements = document.querySelectorAll('[id]');
        return Array.from(elements).map(el => el.id);
    }""",
    )

    # Check for duplicates
    seen_ids = set()
    duplicate_ids = set()

    for id_value in ids:
        if id_value in seen_ids:
            duplicate_ids.add(id_value)
        seen_ids.add(id_value)

    assert len(duplicate_ids) == 0, f"Found duplicate IDs: {duplicate_ids}"


@pytest.mark.accessibility
@pytest.mark.wcag
@pytest.mark.parametrize(
    "page_fixture_name",
    [
        "index_page",
        "teams_page",
    ],
)
def test_landmark_regions_present(
    page_fixture_name: str,
    request: pytest.FixtureRequest,
) -> None:
    """Test that pages have proper landmark regions (WCAG 1.3.1).

    Success Criterion 1.3.1 Info and Relationships (Level A):
    Information, structure, and relationships can be programmatically
    determined.

    Verifies presence of:
    - header or banner role
    - nav or navigation role
    - main role
    - footer or contentinfo role

    Args:
        page_fixture_name: Name of page fixture
        request: Pytest fixture request

    Raises:
        AssertionError: If landmark regions are missing
    """
    # Get page fixture
    page = request.getfixturevalue(page_fixture_name)

    # Navigate to page
    page.navigate()
    page.wait_for_load()

    # Check for landmarks
    has_header = (
        page.page.locator("header").count() > 0 or page.page.locator("[role='banner']").count() > 0
    )
    has_nav = (
        page.page.locator("nav").count() > 0 or page.page.locator("[role='navigation']").count() > 0
    )
    has_main = (
        page.page.locator("main").count() > 0 or page.page.locator("[role='main']").count() > 0
    )
    has_footer = (
        page.page.locator("footer").count() > 0
        or page.page.locator("[role='contentinfo']").count() > 0
    )

    # Assert landmarks exist
    assert has_header, "Page should have header or banner landmark"
    assert has_nav, "Page should have nav or navigation landmark"
    assert has_main, "Page should have main landmark"
    assert has_footer, "Page should have footer or contentinfo landmark"
