# Accessibility Tests

This directory contains automated accessibility tests for the NHL Scrabble web application to ensure WCAG 2.1 Level AA compliance and usability for all users.

## Overview

The accessibility test suite validates:

- **WCAG 2.1 Level AA compliance** using axe-core automated scans
- **Keyboard navigation** functionality for users who cannot use a mouse
- **Screen reader compatibility** through semantic HTML and ARIA attributes
- **Color contrast** ratios for visual accessibility
- **Form labels and ARIA attributes** for assistive technologies
- **Heading hierarchy** for proper document structure
- **Alt text for images** for non-visual users

## Test Organization

### test_axe_scans.py

Automated accessibility scans using axe-playwright-python (axe-core engine):

- **Individual page scans** - Tests each page (index, teams, divisions, conferences, playoffs, stats)
- **WCAG AA compliance** - Parametrized test for all pages checking WCAG 2.1 Level AA rules
- **Zero violations policy** - All tests assert zero accessibility violations

**Key Features:**

- Comprehensive axe-core rule coverage
- Detailed violation reports
- WCAG 2.1 tag filtering

**Example:**

```python
@pytest.mark.accessibility
def test_index_page_accessibility(index_page: IndexPage) -> None:
    """Test homepage for accessibility violations."""
    index_page.navigate()
    index_page.wait_for_load()

    axe = Axe()
    results = axe.run(index_page.page)

    assert results.violations_count == 0
```

### test_keyboard_navigation.py

Keyboard accessibility tests for users who navigate without a mouse:

- **Tab navigation** - Verify Tab key moves focus correctly
- **Shift+Tab reverse navigation** - Verify backward navigation works
- **Enter/Space activation** - Verify keyboard activation of interactive elements
- **No keyboard traps** - Ensure users can Tab through all elements without getting stuck
- **Focus indicators** - Verify visible focus indicators (outline, border, etc.)
- **Logical focus order** - Verify Tab order follows visual layout
- **Standard keyboard shortcuts** - Test common keyboard shortcuts work

**Example:**

```python
@pytest.mark.accessibility
@pytest.mark.keyboard
def test_keyboard_tab_navigation(index_page: IndexPage) -> None:
    """Test keyboard Tab navigation."""
    index_page.navigate()
    index_page.page.keyboard.press("Tab")

    focused_element = index_page.page.locator(":focus")
    expect(focused_element).to_be_visible()
```

### test_wcag_compliance.py

Specific WCAG 2.1 success criteria tests:

- **3.1.1 Language of Page** - HTML lang attribute present
- **2.4.2 Page Titled** - Descriptive page titles
- **1.3.1 Info and Relationships** - Proper heading hierarchy, semantic markup, landmarks
- **1.1.1 Non-text Content** - Alt text for images
- **2.4.4 Link Purpose** - Accessible link names
- **4.1.2 Name, Role, Value** - Accessible names for buttons and form controls
- **3.3.2 Labels or Instructions** - Form input labels
- **4.1.1 Parsing** - No duplicate IDs

**Example:**

```python
@pytest.mark.accessibility
@pytest.mark.wcag
def test_page_has_language_attribute(index_page: IndexPage) -> None:
    """Test lang attribute (WCAG 3.1.1)."""
    index_page.navigate()
    lang_attr = index_page.page.locator("html").get_attribute("lang")

    assert lang_attr == "en"
```

## Running Tests

### Run All Accessibility Tests

```bash
cd qa/web
pytest tests/accessibility/ -v
```

### Run Specific Test Files

```bash
# Axe scans only
pytest tests/accessibility/test_axe_scans.py -v

# Keyboard navigation only
pytest tests/accessibility/test_keyboard_navigation.py -v

# WCAG compliance only
pytest tests/accessibility/test_wcag_compliance.py -v
```

### Run Tests by Marker

```bash
# All accessibility tests
pytest -m accessibility -v

# Keyboard tests only
pytest -m keyboard -v

# WCAG specific tests only
pytest -m wcag -v
```

### Generate HTML Report

```bash
pytest tests/accessibility/ --html=reports/accessibility-report.html --self-contained-html
```

### Run in Headed Mode (Visible Browser)

```bash
pytest tests/accessibility/ --headed
```

### Run with Specific Browser

```bash
pytest tests/accessibility/ --browser chromium
pytest tests/accessibility/ --browser firefox
pytest tests/accessibility/ --browser webkit
```

## WCAG 2.1 Level AA Compliance

The test suite targets **WCAG 2.1 Level AA** compliance, which includes:

### Level A (Basic)

- 1.1.1 Non-text Content
- 1.3.1 Info and Relationships
- 2.4.2 Page Titled
- 2.4.4 Link Purpose
- 3.1.1 Language of Page
- 3.3.2 Labels or Instructions
- 4.1.1 Parsing
- 4.1.2 Name, Role, Value

### Level AA (Enhanced)

- 1.4.3 Contrast (Minimum)
- 1.4.5 Images of Text
- 2.4.6 Headings and Labels
- 2.4.7 Focus Visible
- 3.1.2 Language of Parts

## Dependencies

### Required

- **axe-playwright-python** (>=0.1.7) - axe-core accessibility testing engine
- **playwright** (>=1.58) - Browser automation
- **pytest-playwright** (>=0.7.2) - Pytest integration for Playwright

### Installation

```bash
cd qa/web
pip install -e .
playwright install  # Install browser binaries
```

Or using UV (faster):

```bash
cd qa/web
uv pip install -e .
playwright install
```

## Writing Accessibility Tests

### Best Practices

1. **Test all pages** - Every page should have accessibility tests
1. **Use axe-core first** - Start with automated scans, then add manual tests
1. **Test keyboard navigation** - Verify all features work with keyboard only
1. **Test focus indicators** - Ensure focused elements are visually distinct
1. **Test semantic HTML** - Use proper elements (headings, lists, tables, landmarks)
1. **Test ARIA attributes** - Only use ARIA when semantic HTML isn't sufficient
1. **Descriptive test names** - Include WCAG criterion number in docstring

### Test Template

```python
import pytest
from axe_playwright_python.sync_playwright import Axe
from pages.example_page import ExamplePage


@pytest.mark.accessibility
def test_example_page_accessibility(example_page: ExamplePage) -> None:
    """Test example page for accessibility violations (WCAG 2.1).

    Scans page with axe-core and verifies:
    - No color contrast issues
    - Proper ARIA attributes
    - Semantic HTML structure
    - Keyboard accessibility

    Args:
        example_page: ExamplePage fixture

    Raises:
        AssertionError: If accessibility violations found
    """
    # Navigate to page
    example_page.navigate()
    example_page.wait_for_load()

    # Run axe scan
    axe = Axe()
    results = axe.run(example_page.page)

    # Assert zero violations
    assert results.violations_count == 0, (
        f"Found {results.violations_count} violations:\n" f"{results.generate_report()}"
    )
```

## Common Issues and Fixes

### Missing Alt Text

**Issue:** Images missing alt attributes

**Fix:**

```html
<!-- Before -->
<img src="team-logo.png"/>
<!-- After -->
<img alt="Team Logo" src="team-logo.png"/>
<!-- Decorative image -->
<img alt="" src="decoration.png"/>
```

### Color Contrast

**Issue:** Text doesn't meet 4.5:1 contrast ratio

**Fix:**

- Use darker text colors
- Use lighter background colors
- Test with Chrome DevTools Lighthouse
- Use contrast checker tools

### Missing Form Labels

**Issue:** Input fields without labels

**Fix:**

```html
<!-- Before -->
<input name="search" type="text"/>
<!-- After -->
<label for="search">
 Search:
</label>
<input id="search" name="search" type="text"/>
<!-- Or with aria-label -->
<input aria-label="Search teams" name="search" type="text"/>
```

### Heading Hierarchy

**Issue:** Skipping heading levels (h1 -> h3)

**Fix:**

```html
<!-- Before -->
<h1>
 Page Title
</h1>
<h3>
 Subsection
</h3>
<!-- After -->
<h1>
 Page Title
</h1>
<h2>
 Subsection
</h2>
```

### Keyboard Focus

**Issue:** Interactive elements not keyboard accessible

**Fix:**

```html
<!-- Before -->
<div onclick="handleClick()">
 Click me
</div>
<!-- After -->
<button onclick="handleClick()">
 Click me
</button>
<!-- Or make div keyboard accessible -->
<div onclick="handleClick()" onkeypress="handleClick()" role="button" tabindex="0">
 Click me
</div>
```

## Manual Testing

While automated tests catch many issues, some accessibility testing requires manual verification:

### Screen Reader Testing

**Tools:**

- **NVDA** (Windows, free)
- **JAWS** (Windows, commercial)
- **VoiceOver** (macOS, built-in)

**Test:**

1. Start screen reader
1. Navigate page with Tab key
1. Verify all content is announced
1. Verify labels and descriptions are clear
1. Verify page structure is logical

### Keyboard-Only Testing

**Test:**

1. Unplug mouse or don't use mouse
1. Navigate entire application with keyboard only
1. Verify all features are accessible
1. Check Tab order is logical
1. Verify focus indicators are visible
1. Test common shortcuts (Enter, Space, Escape, Arrow keys)

### Visual Testing

**Test:**

1. Increase zoom to 200%
1. Verify layout doesn't break
1. Test with different color schemes (dark mode, high contrast)
1. Test color blindness modes
1. Reduce color contrast settings

## CI/CD Integration

Accessibility tests run automatically in CI/CD pipeline:

```yaml
# .github/workflows/qa.yml
- name: Run accessibility tests
  run: |
    cd qa/web
    pytest tests/accessibility/ -v --html=reports/a11y-report.html
```

**Enforcement:**

- All accessibility tests must pass before merge
- Zero violations policy
- Accessibility reports uploaded as artifacts

## Resources

### WCAG 2.1 Guidelines

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Understanding WCAG 2.1](https://www.w3.org/WAI/WCAG21/Understanding/)
- [How to Meet WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools

- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [axe-playwright-python](https://github.com/pamelafox/axe-playwright-python)
- [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Learning

- [Web Accessibility Initiative (WAI)](https://www.w3.org/WAI/)
- [A11Y Project](https://www.a11yproject.com/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Troubleshooting

### axe-playwright-python Import Error

**Error:** `ModuleNotFoundError: No module named 'axe_playwright_python'`

**Fix:**

```bash
cd qa/web
pip install axe-playwright-python
```

### Node.js Not Found

**Error:** `Node.js not found (required for axe-core engine)`

**Fix:**

```bash
# Install Node.js
# Ubuntu/Debian
sudo apt install nodejs

# macOS
brew install node

# Or download from https://nodejs.org/
```

### Playwright Browsers Not Installed

**Error:** `Executable doesn't exist at /path/to/browser`

**Fix:**

```bash
playwright install
```

## Contributing

When adding new pages or features:

1. **Add accessibility tests** for new pages
1. **Run axe scan** on new components
1. **Test keyboard navigation** for interactive elements
1. **Verify WCAG compliance** before submitting PR
1. **Update this README** if adding new test patterns

## Metrics

Current accessibility test coverage:

- **6 pages** fully tested with axe-core
- **WCAG 2.1 Level AA** compliance target
- **Zero violations** policy
- **~30+ tests** covering keyboard navigation and specific WCAG criteria

______________________________________________________________________

**Note:** Accessibility is an ongoing commitment. These automated tests catch many issues, but manual testing with screen readers and keyboard-only navigation is also essential.
