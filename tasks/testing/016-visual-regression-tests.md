# Visual Regression Tests

**GitHub Issue**: #317 - https://github.com/bdperkin/nhl-scrabble/issues/317

**Parent Task**: testing/012-qa-automation-framework.md

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Implement visual regression testing using Playwright's screenshot comparison to detect unintended UI changes, layout shifts, and styling errors.

## Proposed Solution

### Screenshot Tests

**Full Page Screenshots:**

```python
def test_homepage_visual(page_fixture):
    page = IndexPage(page_fixture)
    page.navigate()
    expect(page.page).to_have_screenshot("homepage.png")
```

**Component Screenshots:**

```python
def test_team_card_visual(page_fixture):
    page = TeamsPage(page_fixture)
    page.navigate()
    card = page.page.locator(".team-card").first
    expect(card).to_have_screenshot("team-card.png")
```

### Cross-Browser Visual Tests

Test visual consistency across browsers:

- Chromium
- Firefox
- WebKit

### Baseline Management

```bash
# Generate new baselines
pytest tests/visual/ --update-snapshots

# Run visual tests
pytest tests/visual/
```

## Implementation Steps

1. **Configure Visual Testing** (1h)
1. **Create Screenshot Tests** (2-3h)
1. **Generate Baselines** (1h)
1. **Cross-Browser Tests** (1-2h)

## Acceptance Criteria

- [ ] Screenshot tests for all pages
- [ ] Component-level screenshots
- [ ] Cross-browser visual tests
- [ ] Baseline images committed
- [ ] Visual diff reporting

## Dependencies

- **Requires**: testing/014-playwright-framework-setup.md

## Implementation Notes

*To be filled during implementation:*

- Screenshot count:
- Diff threshold:
