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

- [x] Screenshot tests for all pages
- [x] Component-level screenshots
- [x] Cross-browser visual tests
- [ ] Baseline images committed (pending first test run)
- [x] Visual diff reporting

## Dependencies

- **Requires**: testing/014-playwright-framework-setup.md ✅ Complete

## Implementation Notes

**Implemented**: 2026-04-28
**Branch**: testing/016-visual-regression-tests
**PR**: #432 - https://github.com/bdperkin/nhl-scrabble/pull/432
**Commits**: efacca7, 76c25e0

### Actual Implementation

Implemented comprehensive visual regression testing framework with 23 tests covering:

**Full Page Screenshots** (8 tests):
- Index page (full + viewport)
- Teams page (full + viewport)
- Divisions page
- Conferences page
- Playoffs page
- Stats page

**Component Screenshots** (11 tests):
- Navigation bar
- Page headers
- Standings tables (full table, header, rows)
- Division groups
- Conference sections
- Playoff brackets and matchups
- Page footer

**Cross-Browser & Responsive** (5 tests):
- Chromium browser tests
- Mobile viewport (375x667)
- Tablet viewport (768x1024)

### Configuration

- **Screenshot count**: 23 baseline screenshots
- **Diff threshold**: 5% (0.05 max_diff_pixel_ratio)
- **Browsers**: Chromium, Firefox, WebKit (via pytest-playwright)
- **Viewports**: Desktop (1920x1080), Mobile (375x667), Tablet (768x1024)
- **Animation handling**: Disabled via conftest.py for consistency
- **Baseline storage**: `qa/web/tests/visual/snapshots/`

### Files Created

1. `qa/web/tests/visual/test_page_screenshots.py` - Full page tests
2. `qa/web/tests/visual/test_component_screenshots.py` - Component tests
3. `qa/web/tests/visual/test_cross_browser_visual.py` - Cross-browser tests
4. `qa/web/tests/visual/conftest.py` - Visual test configuration
5. `qa/web/tests/visual/pytest.ini` - Pytest settings
6. `qa/web/tests/visual/README.md` - Comprehensive documentation
7. `qa/web/tests/visual/run_visual_tests.sh` - Helper script
8. `.github/workflows/visual-regression.yml` - CI/CD workflow

### CI/CD Integration

**GitHub Actions workflow** (`visual-regression.yml`):
- Triggers on PR/push to main when web files change
- Installs Playwright browsers (Chromium, Firefox, WebKit)
- Starts web server automatically
- Runs visual regression tests
- Uploads diff artifacts on failure
- Posts PR comment with diff summary and download links
- Baseline check job warns if baselines missing

**Workflow features**:
- Automated server startup with health check
- Artifact retention: 30 days
- PR comments with visual diff count and artifact links
- Baseline validation job

### Challenges Encountered

1. **Pytest parametrization conflict**: Initial cross-browser tests used `@pytest.mark.parametrize` which conflicted with pytest-playwright's browser fixtures. Resolved by using individual test functions per browser.

2. **Pre-commit hook formatting**: Multiple formatters (mdformat, black, docformatter) reformatted generated files. Resolved by allowing hooks to run and re-adding formatted files.

3. **YAML line length**: GitHub Actions workflow had long lines exceeding yamllint limit (100 chars). Resolved by splitting long lines and using variables.

4. **Pytest.ini config options**: Initial config included Playwright-specific options not recognized by pytest. Removed unknown options and documented correct configuration approach.

### Deviations from Plan

**Simplified cross-browser approach**: Instead of manually launching browsers with parametrization, leveraged pytest-playwright's built-in browser fixtures to avoid parameter conflicts. This provides better integration with pytest-playwright's screenshot features.

**Enhanced CI/CD**: Added comprehensive workflow beyond basic requirements:
- Automatic server startup with health checks
- PR comment notifications with diff summaries
- Baseline validation job
- Artifact upload for diff images

### Actual vs Estimated Effort

- **Estimated**: 4-6 hours
- **Actual**: ~3 hours
- **Variance**: -1 to -3 hours
- **Reason**: Strong foundation from previous Playwright framework setup (task 014) and clear page object models made implementation faster than expected. Most time spent on CI/CD workflow and comprehensive documentation.

### Testing

**Test Collection**: ✅ All 23 tests collected successfully
**Baseline Generation**: Pending (requires running web server)
**CI Validation**: Pending (will run on PR)

```bash
$ python -m pytest tests/visual/ --collect-only
========================= 23 tests collected in 0.15s ==========================
```

### Usage

**Generate baselines**:
```bash
cd qa/web
pytest tests/visual/ --update-snapshots
```

**Run visual tests**:
```bash
cd qa/web
pytest tests/visual/
```

**Helper script**:
```bash
cd qa/web/tests/visual
./run_visual_tests.sh run          # Run all tests
./run_visual_tests.sh update       # Update baselines
./run_visual_tests.sh page         # Page tests only
./run_visual_tests.sh browser      # Cross-browser only
```

### Next Steps

1. Generate baseline screenshots (requires web server running)
2. Commit baseline images to repository
3. Verify CI workflow passes on PR
4. Document baseline update workflow for team

### Related PRs

- #432 - Visual regression testing implementation

### Lessons Learned

1. **pytest-playwright integration**: Use built-in fixtures rather than manual browser instantiation to avoid parameter conflicts and get better screenshot features.

2. **Baseline management**: Critical to establish baseline update workflow early - need clear guidelines on when/how to update baselines to avoid drift.

3. **CI optimization**: Path filtering in GitHub Actions workflow prevents unnecessary visual test runs when only non-web files change, saving CI resources.

4. **Animation handling**: Disabling CSS animations via JavaScript injection in conftest ensures consistent screenshots across test runs.

5. **Pre-commit hooks**: Allow formatters to run first, then add formatted files - attempting to bypass formatters causes inconsistent code style.

### Performance Metrics

- **Test collection time**: 0.15s
- **Total test count**: 23 visual regression tests
- **Lines of code**: ~1,486 lines (tests + docs + CI)
- **Documentation**: Comprehensive 366-line README
- **CI workflow**: ~250 lines with full automation

### Test Coverage Matrix

| Page/Component | Full Page | Viewport | Component | Cross-Browser | Responsive |
|---|---|---|---|---|---|
| Index | ✅ | ✅ | ✅ (nav, footer) | ✅ | ✅ |
| Teams | ✅ | ✅ | ✅ (table) | ✅ | ✅ |
| Divisions | ✅ | - | ✅ | - | - |
| Conferences | ✅ | - | ✅ | - | - |
| Playoffs | ✅ | - | ✅ | - | - |
| Stats | ✅ | - | - | - | - |
