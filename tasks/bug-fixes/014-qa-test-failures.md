# Fix QA Automation Test Failures (Functional and Accessibility)

**GitHub Issue**: #454 - https://github.com/bdperkin/nhl-scrabble/issues/454

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

4-6 hours

## Description

QA Automation Tests workflow is reporting 6-7 test failures across functional and accessibility test suites. Visual regression and performance tests are passing successfully. The failures prevent achieving 100% test pass rate in CI and indicate potential functional and accessibility issues with the web interface.

**Current Failure Summary:**
- **Functional**: 2 failures (chromium/firefox), 1 failure (webkit)
- **Accessibility**: 4 failures (chromium/webkit), 5 failures (firefox)
- **Visual**: All passing (23/23 across all browsers)
- **Performance**: All passing (14/14 across all browsers)

## Current State

### Functional Test Failures

**1. test_results_replace_previous_results (chromium, firefox)**
```
playwright._impl._errors.Error: Page.wait_for_function: EvalError:
Evaluating a string as JavaScript violates the following Content Security
Policy directive because 'unsafe-eval' is not an allowed source of script:
script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net".
```

**2. test_concurrent_submissions_handled (chromium, firefox)**
```
playwright._impl._errors.Error: Page.wait_for_function: EvalError:
Evaluating a string as JavaScript violates the following Content Security
Policy directive because 'unsafe-eval' is not an allowed source of script:
script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net".
```

**Root Cause:** Tests use `page.wait_for_function("string expression")` which violates CSP by evaluating strings as JavaScript. CSP blocks `unsafe-eval` for security.

**Location:** `qa/web/tests/functional/test_error_handling.py` lines 177, 307

### Accessibility Test Failures

**1. test_enter_key_activates_links (chromium, firefox, webkit)**
```
playwright._impl._errors.TimeoutError: Locator.focus: Timeout 10000ms exceeded.
```

**2. test_focus_visible_indicators (chromium, firefox, webkit)**
```
AssertionError: Locator expected to be visible
```

**3. test_interactive_elements_keyboard_accessible (chromium, firefox, webkit)**
```
AssertionError: Page should have interactive elements
```

**4. test_landmark_regions_present[teams_page] (chromium, firefox, webkit)**
```
AssertionError: Page should have header or banner landmark
```

**Root Causes:**
- Navigation elements may not be properly keyboard-focusable
- Focus indicators may not be visible or may not exist
- Interactive elements may not be discoverable by test selectors
- Teams page may be missing proper landmark regions (header/banner)

**Location:** `qa/web/tests/accessibility/test_keyboard_navigation.py`, `qa/web/tests/accessibility/test_wcag_compliance.py`

## Proposed Solution

### Fix 1: CSP-Compliant Functional Tests

Replace string-based `wait_for_function` with function references:

**Current (CSP violation):**
```python
# test_error_handling.py:177
await page.wait_for_function(
    "document.querySelector('.results-container').style.display !== 'none'"
)
```

**Fixed:**
```python
# Use function reference instead of string
await page.wait_for_function(
    """() => {
        const container = document.querySelector('.results-container');
        return container && container.style.display !== 'none';
    }"""
)

# OR use Playwright's built-in waiters (preferred)
results_container = page.locator('.results-container')
await results_container.wait_for(state='visible')
```

**Better approach** - Use Playwright's built-in locator methods:
```python
# Instead of wait_for_function, use locator.wait_for()
results_container = page.locator('.results-container')
await results_container.wait_for(state='visible', timeout=10000)

# For checking element state changes
await expect(results_container).to_be_visible()
```

### Fix 2: Keyboard Navigation Tests

**Issue:** Tests assume navigation elements are immediately focusable

**Fix:**
```python
# qa/web/tests/accessibility/test_keyboard_navigation.py

# Add wait before focusing
await page.wait_for_load_state('networkidle')
nav_link = page.locator('nav a').first
await nav_link.wait_for(state='visible')
await nav_link.focus()
```

### Fix 3: Focus Indicators

**Issue:** Focus indicators may not be visible or tests are checking incorrectly

**Fix:**
```python
# Ensure element is focused first
focusable_element = page.locator('button, a, input').first
await focusable_element.focus()

# Check for focus styles (outline, border, etc.)
focused_styles = await focusable_element.evaluate(
    """el => {
        const styles = window.getComputedStyle(el);
        return {
            outline: styles.outline,
            outlineWidth: styles.outlineWidth,
            boxShadow: styles.boxShadow
        };
    }"""
)

assert focused_styles['outlineWidth'] != '0px' or focused_styles['boxShadow'] != 'none'
```

### Fix 4: Interactive Elements Discovery

**Issue:** Test selectors may not match actual interactive elements

**Fix:**
```python
# Use more robust selectors
interactive_elements = page.locator(
    'button, a[href], input, select, textarea, '
    '[role="button"], [role="link"], [tabindex]:not([tabindex="-1"])'
)

count = await interactive_elements.count()
assert count > 0, f"Expected interactive elements, found {count}"
```

### Fix 5: Landmark Regions

**Issue:** Teams page missing header/banner landmark

**Fix in web application:**
```html
<!-- src/nhl_scrabble/web/templates/base.html or teams page -->
<header role="banner">
    <nav role="navigation">
        <!-- Navigation content -->
    </nav>
</header>

<main role="main">
    <!-- Main content -->
</main>
```

**Fix in test:**
```python
# Verify landmarks with more specific checks
header = page.locator('header, [role="banner"]')
await expect(header).to_be_visible()

main = page.locator('main, [role="main"]')
await expect(main).to_be_visible()
```

## Implementation Steps

1. **Fix CSP violations in functional tests**
   - Update `qa/web/tests/functional/test_error_handling.py:177`
   - Update `qa/web/tests/functional/test_error_handling.py:307`
   - Replace `wait_for_function("string")` with locator-based waits
   - Test locally with all three browsers

2. **Fix keyboard navigation test**
   - Update `test_enter_key_activates_links` to wait for elements
   - Add proper wait conditions before focusing
   - Verify navigation elements are keyboard-accessible

3. **Fix focus indicator test**
   - Update `test_focus_visible_indicators` to properly check focus styles
   - Ensure elements are focused before checking visibility
   - Add fallback checks for different focus indicator methods

4. **Fix interactive elements test**
   - Update `test_interactive_elements_keyboard_accessible` with robust selectors
   - Ensure all interactive elements are discoverable
   - Add debugging output if no elements found

5. **Fix landmark regions**
   - **Option A:** Update web application templates to include proper landmarks
   - **Option B:** Update test expectations if landmarks are not required
   - Verify teams page has header/banner landmark
   - Check all pages for proper landmark structure

6. **Run full test suite locally**
   ```bash
   ./scripts/pytest-playwright qa/web/tests/functional/ --browser=chromium
   ./scripts/pytest-playwright qa/web/tests/functional/ --browser=firefox
   ./scripts/pytest-playwright qa/web/tests/functional/ --browser=webkit
   ./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=chromium
   ./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=firefox
   ./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=webkit
   ```

7. **Commit changes and push**
   ```bash
   git add qa/web/tests/
   git commit -m "fix(qa): Resolve functional and accessibility test failures

   - Replace CSP-violating wait_for_function with locator waits
   - Fix keyboard navigation tests with proper wait conditions
   - Update focus indicator checks for cross-browser compatibility
   - Improve interactive element discovery with robust selectors
   - Add/verify landmark regions on all pages

   Fixes functional tests:
   - test_results_replace_previous_results
   - test_concurrent_submissions_handled

   Fixes accessibility tests:
   - test_enter_key_activates_links
   - test_focus_visible_indicators
   - test_interactive_elements_keyboard_accessible
   - test_landmark_regions_present[teams_page]

   Task: tasks/bug-fixes/001-qa-test-failures.md
   Issue: #TBD"

   git push
   ```

8. **Verify CI passes**
   - Monitor QA Automation Tests workflow
   - Confirm all functional tests pass (59/59)
   - Confirm all accessibility tests pass (41/41)
   - Verify visual and performance tests remain passing

## Testing Strategy

### Local Testing

**Functional Tests:**
```bash
# Test specific failing tests
./scripts/pytest-playwright qa/web/tests/functional/test_error_handling.py::test_results_replace_previous_results --browser=chromium
./scripts/pytest-playwright qa/web/tests/functional/test_error_handling.py::test_concurrent_submissions_handled --browser=firefox

# Full functional suite
./scripts/pytest-playwright qa/web/tests/functional/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/functional/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/functional/ --browser=webkit
```

**Accessibility Tests:**
```bash
# Test specific failing tests
./scripts/pytest-playwright qa/web/tests/accessibility/test_keyboard_navigation.py::test_enter_key_activates_links --browser=chromium
./scripts/pytest-playwright qa/web/tests/accessibility/test_keyboard_navigation.py::test_focus_visible_indicators --browser=firefox
./scripts/pytest-playwright qa/web/tests/accessibility/test_keyboard_navigation.py::test_interactive_elements_keyboard_accessible --browser=webkit
./scripts/pytest-playwright qa/web/tests/accessibility/test_wcag_compliance.py::test_landmark_regions_present --browser=chromium

# Full accessibility suite
./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/accessibility/ --browser=webkit
```

**All Tests:**
```bash
# Full QA suite (all test types, all browsers)
./scripts/pytest-playwright qa/web/tests/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/ --browser=webkit
```

### Manual Testing

1. **Keyboard Navigation:**
   - Start web server: `nhl-scrabble serve --host 0.0.0.0 --port 5000`
   - Navigate to http://localhost:5000
   - Press Tab to navigate through interactive elements
   - Verify focus indicators are visible on all browsers
   - Press Enter on navigation links to verify activation
   - Press Shift+Tab to reverse navigation

2. **Form Interactions:**
   - Submit form multiple times
   - Verify results replace previous results (not append)
   - Verify concurrent submissions are handled gracefully
   - Check that loading states are shown correctly

3. **Landmark Regions:**
   - Inspect page with browser DevTools
   - Verify `<header>` or `role="banner"` exists
   - Verify `<main>` or `role="main"` exists
   - Verify `<nav>` or `role="navigation"` exists
   - Check teams page specifically

### CI Testing

- Push to feature branch
- Monitor `.github/workflows/qa-automation.yml` workflow
- Verify all 59 functional tests pass
- Verify all 41 accessibility tests pass
- Confirm visual (23) and performance (14) tests remain passing

## Acceptance Criteria

- [ ] All functional tests pass (59/59) across chromium, firefox, webkit
- [ ] All accessibility tests pass (41/41) across chromium, firefox, webkit
- [ ] Visual regression tests remain passing (23/23)
- [ ] Performance tests remain passing (14/14)
- [ ] No CSP violations in test code
- [ ] Keyboard navigation works correctly in manual testing
- [ ] Focus indicators are visible on all interactive elements
- [ ] All pages have proper landmark regions (header, main, nav)
- [ ] CI QA Automation workflow passes completely
- [ ] No new test failures introduced
- [ ] Test code follows Playwright best practices (locators over wait_for_function)

## Related Files

- `qa/web/tests/functional/test_error_handling.py` - Functional test failures (CSP violations)
- `qa/web/tests/accessibility/test_keyboard_navigation.py` - Keyboard navigation failures
- `qa/web/tests/accessibility/test_wcag_compliance.py` - Landmark region failures
- `src/nhl_scrabble/web/templates/base.html` - Base template for landmark regions (if needed)
- `.github/workflows/qa-automation.yml` - CI workflow that runs tests

## Dependencies

None - This task can be implemented independently.

## Additional Notes

### Performance Considerations

- Replacing `wait_for_function` with `locator.wait_for()` is more performant
- Locator-based waits are Playwright's recommended approach
- Auto-waiting built into locators reduces flakiness

### Security Considerations

- CSP violations are security concerns, even in tests
- Using string evaluation in JavaScript is discouraged
- Modern approach: use function references or built-in Playwright waiters

### Breaking Changes

None - This is purely fixing broken tests, not changing application behavior.

### Migration Requirements

None - Test-only changes.

### Cross-Browser Compatibility

- CSP behavior is consistent across browsers
- Keyboard focus behavior may vary slightly between browsers
- Focus indicators may render differently (outline vs box-shadow)
- Landmark regions are standard HTML5/ARIA

### Best Practices Applied

1. **Use Playwright locators** - More robust than string-based selectors
2. **Avoid CSP violations** - Never use string evaluation in modern apps
3. **Proper ARIA landmarks** - Essential for accessibility compliance
4. **Visible focus indicators** - Required for WCAG 2.1 AA compliance
5. **Keyboard accessibility** - All interactive elements must be keyboard-operable

### Reference Documentation

- [Playwright Locators](https://playwright.dev/python/docs/locators)
- [Playwright Auto-waiting](https://playwright.dev/python/docs/actionability)
- [CSP: script-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src)
- [WCAG 2.1 Landmarks](https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships.html)
- [WCAG 2.1 Focus Visible](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html)
- [WCAG 2.1 Keyboard](https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html)

## Implementation Notes

*To be filled during implementation:*
- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated (4-6h)
- Root causes of each failure (detailed analysis)
- Any additional test improvements made
- Browser-specific quirks discovered
