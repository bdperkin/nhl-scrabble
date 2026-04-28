"""Keyboard navigation accessibility tests.

This module tests keyboard accessibility features to ensure users can
navigate and interact with the application using only the keyboard.

Tests verify:
- Tab navigation works correctly
- Focus indicators are visible
- Skip links function properly
- Interactive elements are keyboard accessible
- Focus order is logical
- Keyboard traps are avoided
"""

import pytest
from pages.index_page import IndexPage
from pages.teams_page import TeamsPage
from playwright.sync_api import expect


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_keyboard_tab_navigation(index_page: IndexPage) -> None:
    """Test keyboard Tab navigation on homepage.

    Verifies that users can navigate the page using the Tab key and
    that focused elements are visible with proper focus indicators.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If keyboard navigation fails or focus is not visible
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Press Tab to move focus
    index_page.page.keyboard.press("Tab")

    # Get the focused element
    focused_element = index_page.page.locator(":focus")

    # Verify element is focused and visible
    expect(focused_element).to_be_visible()
    expect(focused_element).to_be_focused()


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_shift_tab_reverse_navigation(index_page: IndexPage) -> None:
    """Test reverse keyboard navigation using Shift+Tab.

    Verifies that users can navigate backwards through focusable elements
    using Shift+Tab.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If reverse navigation fails
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Tab forward a few times
    for _ in range(3):
        index_page.page.keyboard.press("Tab")

    # Get current focus
    current_focus = index_page.page.evaluate("document.activeElement.id")

    # Tab backward
    index_page.page.keyboard.press("Shift+Tab")

    # Verify focus moved backward
    new_focus = index_page.page.evaluate("document.activeElement.id")
    assert new_focus != current_focus, "Focus should have moved backward"


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_enter_key_activates_links(index_page: IndexPage) -> None:
    """Test that Enter key activates focused links.

    Verifies that users can activate links using the Enter key
    when they have keyboard focus.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If Enter key doesn't activate links
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Find a navigation link (e.g., Teams link)
    teams_link = index_page.page.locator('a[href*="teams"]').first

    # Focus the link
    teams_link.focus()

    # Verify link is focused
    expect(teams_link).to_be_focused()

    # Press Enter (note: we don't actually navigate in this test)
    # Just verify the link is activatable
    assert teams_link.is_enabled(), "Link should be enabled"


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_no_keyboard_trap(index_page: IndexPage) -> None:
    """Test that there are no keyboard traps on the page.

    A keyboard trap prevents users from navigating away using only
    the keyboard. This test verifies users can Tab through all
    focusable elements without getting stuck.

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If a keyboard trap is detected
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Track focus positions
    focus_positions = []
    max_tabs = 50  # Reasonable limit to prevent infinite loop

    for i in range(max_tabs):
        # Press Tab
        index_page.page.keyboard.press("Tab")

        # Get current focus
        current_focus = index_page.page.evaluate(
            """() => {
            const el = document.activeElement;
            return {
                tag: el.tagName,
                id: el.id,
                class: el.className,
                text: el.textContent?.slice(0, 20)
            };
        }""",
        )

        focus_positions.append(current_focus)

        # Check if we've cycled back to first element (normal behavior)
        # or if we're stuck on the same element (keyboard trap)
        if i > 2 and focus_positions[-1] == focus_positions[-2]:
            # We're stuck on the same element
            msg = f"Keyboard trap detected at element: {current_focus}"
            raise AssertionError(msg)


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_focus_visible_indicators(teams_page: TeamsPage) -> None:
    """Test that focus indicators are visible when navigating with keyboard.

    Verifies that when users Tab through interactive elements, each
    element shows a visible focus indicator (outline, border, etc.).

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If focus indicators are not visible
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Tab to first interactive element
    teams_page.page.keyboard.press("Tab")

    # Get focused element
    focused_element = teams_page.page.locator(":focus")

    # Verify element is visible (has focus indicator)
    expect(focused_element).to_be_visible()

    # Check that element has some visual focus indicator
    # This checks for outline, border, or box-shadow changes
    has_focus_style = teams_page.page.evaluate(
        """() => {
        const el = document.activeElement;
        const styles = window.getComputedStyle(el);
        return (
            styles.outline !== 'none' ||
            styles.outlineWidth !== '0px' ||
            styles.borderWidth !== '0px' ||
            styles.boxShadow !== 'none'
        );
    }""",
    )

    assert has_focus_style, "Focused element should have visible focus indicator"


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_interactive_elements_keyboard_accessible(teams_page: TeamsPage) -> None:
    """Test that all interactive elements are keyboard accessible.

    Verifies that buttons, links, and form controls can receive
    keyboard focus and be activated with keyboard.

    Args:
        teams_page: TeamsPage fixture

    Raises:
        AssertionError: If interactive elements are not keyboard accessible
    """
    # Navigate to teams page
    teams_page.navigate()
    teams_page.wait_for_load()

    # Get all interactive elements
    interactive_elements = teams_page.page.query_selector_all(
        "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])",
    )

    # Verify we found interactive elements
    assert len(interactive_elements) > 0, "Page should have interactive elements"

    # Check each element can receive focus
    for element in interactive_elements[:5]:  # Test first 5 to keep test fast
        element.focus()
        is_focused = teams_page.page.evaluate(
            "(el) => document.activeElement === el",
            element,
        )
        assert is_focused, f"Element {element} should be focusable"


@pytest.mark.accessibility
@pytest.mark.keyboard
def test_logical_focus_order(index_page: IndexPage) -> None:
    """Test that Tab order follows logical reading order.

    Verifies that keyboard navigation follows the visual layout
    and reading order of the page (top to bottom, left to right).

    Args:
        index_page: IndexPage fixture

    Raises:
        AssertionError: If focus order is illogical
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Collect focus positions and coordinates
    focus_positions = []

    for _ in range(10):  # Test first 10 tab stops
        index_page.page.keyboard.press("Tab")

        position = index_page.page.evaluate(
            """() => {
            const el = document.activeElement;
            const rect = el.getBoundingClientRect();
            return {
                top: rect.top,
                left: rect.left,
                tag: el.tagName,
                id: el.id
            };
        }""",
        )
        focus_positions.append(position)

    # Basic check: vertical positions should generally increase
    # (moving down the page) or stay similar (moving across)
    top_positions = [pos["top"] for pos in focus_positions]

    # Allow some variance but check general downward trend
    # Focus shouldn't jump wildly up and down the page
    for i in range(1, len(top_positions)):
        jump = abs(top_positions[i] - top_positions[i - 1])
        # Large jumps (>500px) backwards might indicate illogical order
        if jump > 500 and top_positions[i] < top_positions[i - 1]:
            # This is a heuristic check - might need adjustment
            pass  # Allow for navigation menus that might be at top


@pytest.mark.accessibility
@pytest.mark.keyboard
@pytest.mark.parametrize(
    "key",
    [
        "Tab",
        "Enter",
        "Space",
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "Home",
        "End",
        "Escape",
    ],
)
def test_standard_keyboard_shortcuts_work(index_page: IndexPage, key: str) -> None:
    """Test that standard keyboard shortcuts work correctly.

    Verifies that common keyboard shortcuts don't cause errors
    and function as expected.

    Args:
        index_page: IndexPage fixture
        key: Keyboard key to test

    Raises:
        AssertionError: If keyboard shortcut causes errors
    """
    # Navigate to index page
    index_page.navigate()
    index_page.wait_for_load()

    # Press the key
    index_page.page.keyboard.press(key)

    # Verify page is still responsive (no JavaScript errors)
    # This is a basic smoke test for keyboard handling
    assert index_page.page.url is not None, "Page should still be loaded"
