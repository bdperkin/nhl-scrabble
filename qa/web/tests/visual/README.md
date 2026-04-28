# Visual Regression Tests

Visual regression tests for the NHL Scrabble web application using Playwright screenshot capture and pytest-playwright-snapshot for comparison.

## Overview

Visual regression testing captures screenshots of UI components and pages, then compares them against baseline images to detect unintended visual changes, layout shifts, and styling errors.

**Technology Stack:**

- **Playwright**: Browser automation and screenshot capture
- **pytest-playwright-snapshot**: Snapshot comparison with pixelmatch
- **pixelmatch**: Pixel-level image comparison with configurable threshold

## Test Structure

```
visual/
├── conftest.py                     # Visual test configuration
├── pytest.ini                      # Pytest settings for visual tests
├── README.md                       # This file
├── test_page_screenshots.py        # Full page screenshot tests
├── test_component_screenshots.py   # Component-level screenshot tests
├── test_cross_browser_visual.py    # Cross-browser visual tests
└── __snapshots__/                  # Baseline screenshot images (generated)
    └── chromium/                   # Browser-specific snapshots
        └── linux/                  # Platform-specific snapshots
            ├── index-page-full.png
            ├── teams-page-full.png
            └── ...
```

## Test Coverage

### Full Page Screenshots

- **Index Page**: Home page layout and content
- **Teams Page**: Team standings table
- **Divisions Page**: Division groupings
- **Conferences Page**: Conference standings
- **Playoffs Page**: Playoff bracket layout
- **Stats Page**: Statistics and charts

### Component Screenshots

- **Navigation Bar**: Header navigation
- **Page Headers**: Page titles and breadcrumbs
- **Standings Tables**: Team standings tables
- **Table Components**: Headers, rows, cells
- **Division Groups**: Division sections
- **Conference Sections**: Conference groupings
- **Playoff Brackets**: Bracket structure
- **Playoff Matchups**: Individual matchups
- **Footer**: Page footer

### Cross-Browser Tests

All tests run across:

- **Chromium** (Chrome, Edge)
- **Firefox**
- **WebKit** (Safari)

Additional responsive tests:

- **Mobile**: 375x667 viewport (iPhone)
- **Tablet**: 768x1024 viewport (iPad)

## Usage

### Prerequisites

1. **Install dependencies**:

   ```bash
   cd qa/web
   pip install -e .
   playwright install
   ```

1. **Start the web application**:

   ```bash
   # From project root
   nhl-scrabble serve
   # Or your preferred method to start on http://localhost:5000
   ```

### Running Tests

**Run all visual tests**:

```bash
pytest tests/visual/
```

**Run specific test file**:

```bash
pytest tests/visual/test_page_screenshots.py
pytest tests/visual/test_component_screenshots.py
pytest tests/visual/test_cross_browser_visual.py
```

**Run specific test**:

```bash
pytest tests/visual/test_page_screenshots.py::test_index_page_visual
```

**Run cross-browser tests only**:

```bash
pytest tests/visual/test_cross_browser_visual.py
```

### Baseline Management

#### Generate New Baselines

When running tests for the first time or when intentional UI changes are made:

```bash
# Generate baselines for all visual tests
pytest tests/visual/ --update-snapshots

# Generate baselines for specific test file
pytest tests/visual/test_page_screenshots.py --update-snapshots
```

**Important**: Only update baselines when you've verified the UI changes are intentional!

#### Update Specific Baselines

```bash
# Update single test baseline
pytest tests/visual/test_page_screenshots.py::test_index_page_visual --update-snapshots
```

#### Review Baseline Changes

Before committing updated baselines:

1. **Review diffs**:

   ```bash
   git diff qa/web/tests/visual/__snapshots__/
   ```

1. **Visually inspect new screenshots**:

   - Located in `qa/web/tests/visual/__snapshots__/`
   - Organized by browser name and platform
   - PNG format

1. **Commit baselines**:

   ```bash
   git add qa/web/tests/visual/__snapshots__/
   git commit -m "test(visual): Update baselines for <reason>"
   ```

### Visual Diff Reports

When tests fail due to visual differences:

1. **Playwright generates diff images**:

   - `<test-name>-actual.png` - Current screenshot
   - `<test-name>-expected.png` - Baseline screenshot
   - `<test-name>-diff.png` - Highlighted differences

1. **Review diffs**:

   ```bash
   # Diffs are in test-results/
   ls -la test-results/
   ```

1. **HTML report** (if configured):

   ```bash
   pytest tests/visual/ --html=report.html --self-contained-html
   ```

## Configuration

### Screenshot Comparison Settings

Configured in `pytest.ini`:

```ini
# Maximum allowed difference (0.0-1.0)
# 0.0 = pixel-perfect match
# 0.05 = allow 5% difference
playwright_max_diff_pixel_ratio = 0.05

# Timeout for expect assertions
playwright_expect_timeout = 10000
```

### Browser Context Settings

Configured in `conftest.py`:

```python
{
    "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 1,
    "locale": "en-US",
    "timezone_id": "America/New_York",
}
```

### Visual Test Optimizations

Tests are optimized for consistency:

- **Animations disabled**: No CSS animations or transitions
- **Fixed viewport**: Consistent 1920x1080 resolution
- **Fixed locale**: en-US
- **Fixed timezone**: America/New_York
- **Font loading**: Waits for web fonts

## Best Practices

### When to Update Baselines

✅ **DO update baselines when**:

- Intentional UI/UX changes are made
- Design system updates are implemented
- Component library is updated
- Layout improvements are added

❌ **DON'T update baselines when**:

- Tests are failing for unknown reasons
- You haven't reviewed the visual diffs
- Changes are unintended side effects
- CI is failing (investigate first!)

### Baseline Commit Guidelines

1. **Review all diffs** before committing
1. **Include reason** in commit message
1. **Link to PR/issue** that caused the change
1. **Test locally first** before pushing
1. **Regenerate all baselines** if major changes

### Debugging Failed Tests

1. **Check application is running**:

   ```bash
   curl http://localhost:5000
   ```

1. **Run single test with verbose output**:

   ```bash
   pytest tests/visual/test_page_screenshots.py::test_index_page_visual -vv
   ```

1. **Examine diff images**:

   ```bash
   # Look for *-diff.png files
   find test-results/ -name "*-diff.png"
   ```

1. **Check for environment differences**:

   - Font rendering differences (different OS)
   - Screen DPI differences
   - Browser version differences

1. **Regenerate problematic baseline**:

   ```bash
   pytest tests/visual/test_page_screenshots.py::test_index_page_visual --update-snapshots
   ```

## CI/CD Integration

### GitHub Actions

Visual tests can run in CI with headless browsers:

```yaml
- name: Install Playwright browsers
  run: playwright install --with-deps

- name: Run visual regression tests
  run: |
    cd qa/web
    pytest tests/visual/ --headed=false
```

### Baseline Storage

- **Baselines committed to git**: Tracked in version control
- **Diff artifacts**: Uploaded on test failure
- **Retention**: Keep diffs for 30 days

### Failure Handling

On visual test failure in CI:

1. **Review diff artifacts** in CI logs
1. **Download diff images** from artifacts
1. **Investigate locally** before updating baselines
1. **Update baselines** only after verification

## Troubleshooting

### Tests Pass Locally But Fail in CI

**Cause**: Font rendering or browser version differences

**Solution**:

1. Use exact browser versions in CI and locally
1. Install system fonts in CI environment
1. Adjust `playwright_max_diff_pixel_ratio` threshold
1. Generate baselines in CI environment

### Screenshots Are Blank

**Cause**: Application not running or not accessible

**Solution**:

1. Verify app is running: `curl http://localhost:5000`
1. Check base_url in fixtures
1. Increase page load timeout
1. Check for JavaScript errors

### Flaky Visual Tests

**Cause**: Dynamic content, animations, or loading states

**Solution**:

1. Wait for content to load: `page.wait_for_load_state("networkidle")`
1. Disable animations in conftest.py
1. Mock dynamic content (timestamps, random data)
1. Use `wait_for_selector()` for dynamic elements

### Too Many False Positives

**Cause**: Threshold too strict

**Solution**:

1. Increase `playwright_max_diff_pixel_ratio` (e.g., 0.05 → 0.10)
1. Use component screenshots instead of full page
1. Exclude dynamic content areas
1. Stabilize test data

## Resources

- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [Playwright Screenshot API](https://playwright.dev/docs/api/class-page#page-screenshot)
- [Visual Regression Testing Best Practices](https://playwright.dev/docs/best-practices#visual-comparisons)

## Metrics

- **Full Page Screenshots**: 8 tests
- **Component Screenshots**: 11 tests
- **Cross-Browser Tests**: 5 tests × 3 browsers = 15 tests
- **Total Screenshot Comparisons**: 34+ screenshots
- **Browsers Covered**: Chromium, Firefox, WebKit
- **Viewports Tested**: Desktop (1920x1080), Mobile (375x667), Tablet (768x1024)
