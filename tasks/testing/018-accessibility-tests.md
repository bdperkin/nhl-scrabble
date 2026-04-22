# Accessibility Tests

**GitHub Issue**: #318 - https://github.com/bdperkin/nhl-scrabble/issues/318

**Parent Task**: testing/012-qa-automation-framework.md

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-4 hours

## Description

Implement automated accessibility testing to ensure WCAG 2.1 compliance and usability for all users.

## Proposed Solution

### Axe-core Integration

```python
from axe_playwright import Axe

def test_homepage_accessibility(page_fixture):
    page = IndexPage(page_fixture)
    page.navigate()

    axe = Axe(page.page)
    results = axe.run()

    assert len(results.violations) == 0, \
        f"Found {len(results.violations)} violations"
```

### WCAG Compliance Checks

- Color contrast
- Keyboard navigation
- ARIA attributes
- Form labels
- Alt text for images
- Heading hierarchy

### Manual Keyboard Tests

```python
def test_keyboard_navigation(page_fixture):
    page = IndexPage(page_fixture)
    page.navigate()

    page.page.keyboard.press("Tab")
    focused = page.page.locator(":focus")
    assert focused.is_visible()
```

## Implementation Steps

1. **Install Axe-core** (30min)
1. **Automated Scans** (1-2h)
1. **Keyboard Tests** (1h)
1. **Screen Reader Tests** (30min-1h)

## Acceptance Criteria

- [ ] Axe-core integrated
- [ ] All pages scanned
- [ ] Zero violations on critical pages
- [ ] Keyboard navigation tested
- [ ] WCAG 2.1 AA compliance

## Dependencies

- **Requires**: testing/014-playwright-framework-setup.md

## Implementation Notes

*To be filled during implementation:*

- Violations found:
- Compliance level:
