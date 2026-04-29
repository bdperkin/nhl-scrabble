# Fix WCAG 2.1 AA Accessibility Violations in Web App

**GitHub Issue**: #440 - https://github.com/bdperkin/nhl-scrabble/issues/440

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

2-3 hours

## Description

Fix accessibility violations detected by axe-core tests to achieve WCAG 2.1 AA compliance. Currently, accessibility tests are detecting 10 violations per browser (30 total across chromium, firefox, webkit). These are real issues that affect users with disabilities and must be fixed to ensure the web application is accessible to all users.

## Current State

Accessibility tests are detecting real WCAG 2.1 AA violations in the web application:

```bash
$ cd qa/web && pytest tests/accessibility/
# 30 failures across 3 browsers (10 per browser):
#
# Chromium (10 violations):
# - 4 keyboard navigation issues
# - 6 axe-core violations (ARIA, contrast, semantics)
#
# Firefox (10 violations):
# - 4 keyboard navigation issues
# - 6 axe-core violations (ARIA, contrast, semantics)
#
# WebKit (10 violations):
# - 4 keyboard navigation issues
# - 6 axe-core violations (ARIA, contrast, semantics)
```

### Violation Categories

**1. Keyboard Navigation (4 per browser):**
- Focus indicators not visible on interactive elements
- Interactive elements not keyboard accessible (missing tabindex)
- Tab navigation not working properly (incorrect tab order)
- Shift+Tab reverse navigation broken

**2. Axe-core Violations (6 per browser):**
- Missing ARIA labels on buttons and form controls
- Semantic HTML issues (improper use of `<div>` for buttons)
- Color contrast problems (text vs background)
- Missing form labels
- Improper heading hierarchy
- Missing landmark roles

## Proposed Solution

Fix HTML/CSS issues to achieve WCAG 2.1 AA compliance:

### 1. Add Proper ARIA Labels

```html
<!-- BEFORE: Missing ARIA labels -->
<button id="analyzeBtn">Analyze</button>
<input type="number" id="topPlayers">

<!-- AFTER: With ARIA labels -->
<button id="analyzeBtn" aria-label="Analyze NHL Scrabble scores">
  Analyze
</button>
<input
  type="number"
  id="topPlayers"
  aria-label="Number of top players to display"
  aria-describedby="topPlayersHelp"
>
<small id="topPlayersHelp">Enter a number between 1 and 100</small>
```

### 2. Implement Keyboard Navigation Support

```html
<!-- BEFORE: No keyboard support -->
<div class="results-container">
  <div onclick="sortTable('name')">Name</div>
  <div onclick="sortTable('score')">Score</div>
</div>

<!-- AFTER: With keyboard support -->
<div class="results-container">
  <button
    tabindex="0"
    onclick="sortTable('name')"
    onkeypress="if(event.key==='Enter') sortTable('name')"
    aria-label="Sort by player name"
  >
    Name
  </button>
  <button
    tabindex="0"
    onclick="sortTable('score')"
    onkeypress="if(event.key==='Enter') sortTable('score')"
    aria-label="Sort by Scrabble score"
  >
    Score
  </button>
</div>
```

### 3. Add Visible Focus Indicators

```css
/* BEFORE: No focus indicators */
button, input, select {
  outline: none; /* ← REMOVE THIS */
}

/* AFTER: Visible focus indicators */
button:focus,
input:focus,
select:focus,
a:focus {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
  border-radius: 3px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  button:focus,
  input:focus {
    outline: 3px solid currentColor;
    outline-offset: 3px;
  }
}
```

### 4. Fix Color Contrast Issues

```css
/* BEFORE: Insufficient contrast (WCAG AA requires 4.5:1 for normal text) */
.secondary-text {
  color: #999999; /* Contrast ratio: 2.85:1 - FAILS */
  background: #ffffff;
}

/* AFTER: Sufficient contrast */
.secondary-text {
  color: #666666; /* Contrast ratio: 5.74:1 - PASSES */
  background: #ffffff;
}

/* Check contrast with tools:
 * - WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
 * - Chrome DevTools: Inspect element → Contrast ratio indicator
 */
```

### 5. Use Semantic HTML

```html
<!-- BEFORE: Non-semantic divs used as buttons -->
<div class="button" onclick="submit()">Submit</div>

<!-- AFTER: Proper semantic elements -->
<button type="submit" class="button" onclick="submit()">Submit</button>

<!-- Form labels -->
<label for="topPlayers">Top Players:</label>
<input type="number" id="topPlayers" name="topPlayers">

<!-- Heading hierarchy (h1 → h2 → h3, no skipping) -->
<h1>NHL Scrabble Analyzer</h1>
<h2>Configuration</h2>
<h3>Display Settings</h3>
```

### 6. Add Landmark Roles

```html
<!-- BEFORE: No landmarks -->
<div class="header">...</div>
<div class="main">...</div>
<div class="footer">...</div>

<!-- AFTER: With landmark roles -->
<header role="banner">...</header>
<main role="main">...</main>
<nav role="navigation">...</nav>
<footer role="contentinfo">...</footer>
```

## Implementation Steps

1. **Run accessibility tests locally** and capture detailed violations:
   ```bash
   cd qa/web
   pytest tests/accessibility/ --browser=chromium --verbose --tb=long > accessibility_violations.txt
   ```

2. **Categorize violations** by type:
   - Keyboard navigation (focus, tabindex, tab order)
   - ARIA labels (buttons, inputs, interactive elements)
   - Focus indicators (CSS outline styles)
   - Color contrast (text, backgrounds, borders)
   - Semantic HTML (headings, labels, roles)

3. **Fix violations** in `src/nhl_scrabble/web/` files:
   - Update `templates/index.html` for HTML structure
   - Update `static/css/style.css` for focus indicators and contrast
   - Update `static/js/app.js` for keyboard event handlers
   - Add ARIA attributes to all interactive elements

4. **Test fixes with axe-core locally** after each category:
   ```bash
   pytest tests/accessibility/test_keyboard_navigation.py --browser=chromium
   pytest tests/accessibility/test_wcag_compliance.py --browser=chromium
   ```

5. **Verify across all three browsers**:
   ```bash
   pytest tests/accessibility/ --browser=chromium
   pytest tests/accessibility/ --browser=firefox
   pytest tests/accessibility/ --browser=webkit
   ```

6. **Manual testing**:
   - Test keyboard navigation (Tab, Shift+Tab, Enter, Space, Escape)
   - Test with screen reader if possible (NVDA, JAWS, VoiceOver)
   - Test in high contrast mode
   - Test with browser zoom at 200%

7. **Document accessibility improvements** in CHANGELOG.md

## Testing Strategy

**Automated testing:**
- Run accessibility tests after each category of fixes
- Use axe-core via pytest-playwright for WCAG compliance
- Verify 0 violations reported by axe-core
- Test across all browsers (chromium, firefox, webkit)

**Manual keyboard navigation testing:**
```
Tab navigation:
1. Tab through all interactive elements in order
2. Verify visible focus indicator on each element
3. Verify tab order is logical (top to bottom, left to right)
4. Verify Shift+Tab reverses order

Keyboard activation:
1. Press Enter on buttons → should activate
2. Press Space on buttons → should activate
3. Press Enter on links → should navigate
4. Press Escape on modals → should close (if applicable)

Form controls:
1. Arrow keys to navigate radio buttons/checkboxes
2. Space to toggle checkboxes
3. Arrow keys to change select dropdowns
4. Enter to submit forms
```

**Screen reader testing (optional but recommended):**
- NVDA (Windows, free): https://www.nvaccess.org/download/
- JAWS (Windows, commercial): https://www.freedomscientific.com/products/software/jaws/
- VoiceOver (macOS, built-in): Cmd+F5 to enable

**Contrast checking:**
- Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools: Inspect element → Check contrast ratio indicator
- Verify all text meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)

## Acceptance Criteria

- [ ] All keyboard navigation issues fixed
  - [ ] Visible focus indicators on all interactive elements
  - [ ] Proper tab order (logical flow)
  - [ ] Shift+Tab reverse navigation working
  - [ ] All elements keyboard accessible (no mouse-only)
- [ ] All ARIA label violations fixed
  - [ ] All buttons have aria-label or visible text
  - [ ] All inputs have aria-label or associated label
  - [ ] All interactive elements have ARIA attributes
- [ ] All focus indicator issues fixed
  - [ ] CSS focus styles defined (outline, border, or box-shadow)
  - [ ] Focus indicators visible and meet 3:1 contrast ratio
  - [ ] Focus indicators not removed with outline: none
- [ ] All color contrast violations fixed
  - [ ] Normal text: ≥4.5:1 contrast ratio
  - [ ] Large text (18pt+): ≥3:1 contrast ratio
  - [ ] UI components: ≥3:1 contrast ratio
- [ ] All semantic HTML issues fixed
  - [ ] Buttons use `<button>`, not `<div onclick>`
  - [ ] Forms have proper `<label>` elements
  - [ ] Headings follow hierarchy (h1 → h2 → h3)
  - [ ] Landmark roles added (header, main, nav, footer)
- [ ] Accessibility tests pass (0/30 failures)
- [ ] Manual keyboard navigation verified
- [ ] Changes tested across all three browsers
- [ ] axe-core reports 0 violations

## Related Files

**Templates:**
- `src/nhl_scrabble/web/templates/index.html` - Main HTML structure, ARIA labels, semantic elements

**Styles:**
- `src/nhl_scrabble/web/static/css/style.css` - Focus indicators, color contrast

**JavaScript:**
- `src/nhl_scrabble/web/static/js/app.js` - Keyboard event handlers

**Tests:**
- `qa/web/tests/accessibility/test_keyboard_navigation.py` - Keyboard tests
- `qa/web/tests/accessibility/test_wcag_compliance.py` - WCAG tests

**Documentation:**
- `CHANGELOG.md` - Document accessibility improvements

## Dependencies

- axe-playwright-python package (already installed)
- pytest-playwright for browser automation
- WebAIM Contrast Checker for manual verification
- Screen reader software for manual testing (optional)

## Additional Notes

**WCAG 2.1 AA Requirements:**
- **1.3.1 Info and Relationships**: Semantic HTML and ARIA
- **1.4.3 Contrast (Minimum)**: 4.5:1 for normal text, 3:1 for large text
- **2.1.1 Keyboard**: All functionality via keyboard
- **2.4.7 Focus Visible**: Visible keyboard focus indicator
- **4.1.2 Name, Role, Value**: Proper ARIA labels and roles

**Common Mistakes to Avoid:**
- ❌ Using `outline: none` without providing alternative focus indicator
- ❌ Using `<div>` with `onclick` instead of `<button>`
- ❌ Missing labels on form inputs
- ❌ Insufficient color contrast (especially grays)
- ❌ Skipping heading levels (h1 → h3, skipping h2)
- ❌ Mouse-only interactions (no keyboard equivalent)

**Testing Tools:**
- Axe DevTools browser extension (free): https://www.deque.com/axe/devtools/
- WAVE browser extension (free): https://wave.webaim.org/extension/
- Lighthouse (Chrome DevTools): Built-in accessibility audit

**Resources:**
- WCAG 2.1 Quick Reference: https://www.w3.org/WAI/WCAG21/quickref/
- WebAIM: https://webaim.org/
- MDN Accessibility: https://developer.mozilla.org/en-US/docs/Web/Accessibility

## Implementation Notes

*To be filled during implementation:*
- Exact violations found and their solutions
- Files modified with line numbers
- Color contrast ratios before/after
- Manual testing results
- Screen reader testing notes (if performed)
- Time taken per violation category
- Any challenging fixes or workarounds
