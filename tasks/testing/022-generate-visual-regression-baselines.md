# Generate Visual Regression Test Baselines

**GitHub Issue**: #437 - https://github.com/bdperkin/nhl-scrabble/issues/437

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

30 minutes

## Description

Generate baseline snapshots for visual regression tests to eliminate the 15 expected failures (5 per browser). The visual regression test infrastructure is in place and working correctly, but baseline snapshots have not been generated yet.

## Current State

Visual regression tests are currently failing because baseline snapshots do not exist:

```bash
$ cd qa/web && pytest tests/visual/
# 15 failures across 3 browsers (5 per browser):
# - chromium: 5 visual tests fail (no baselines)
# - firefox: 5 visual tests fail (no baselines)
# - webkit: 5 visual tests fail (no baselines)
```

The test infrastructure uses `pytest-playwright-snapshot` for visual regression testing with Playwright. Tests compare current screenshots against baseline snapshots stored in `qa/web/tests/visual/__snapshots__/`.

## Proposed Solution

Run pytest with `--update-snapshots` flag to generate baseline images for all visual regression tests across all three browsers (chromium, firefox, webkit).

```bash
# Generate baselines for all browsers
cd qa/web

# Chromium baselines
pytest tests/visual/ --update-snapshots --browser=chromium

# Firefox baselines
pytest tests/visual/ --update-snapshots --browser=firefox

# WebKit baselines
pytest tests/visual/ --update-snapshots --browser=webkit

# Verify baselines were created
ls -lh tests/visual/__snapshots__/

# Run tests without --update-snapshots to verify they pass
pytest tests/visual/ --browser=chromium
pytest tests/visual/ --browser=firefox
pytest tests/visual/ --browser=webkit
```

## Implementation Steps

1. Navigate to qa/web directory
2. Ensure web server is running (or start it): `nhl-scrabble serve`
3. Run pytest with --update-snapshots for chromium browser
4. Run pytest with --update-snapshots for firefox browser
5. Run pytest with --update-snapshots for webkit browser
6. Verify baselines generated in `tests/visual/__snapshots__/` directory
7. Run tests without --update-snapshots to verify they pass
8. Review generated screenshots for correctness
9. Commit baseline images to git repository

## Testing Strategy

**Verification:**
- Run visual tests after baseline generation to verify 0 failures
- Test across all three browsers (chromium, firefox, webkit)
- Verify baselines are properly versioned in git
- Ensure snapshots are stored in correct directory structure

**Expected test output after baselines:**
```bash
$ pytest tests/visual/
===== test session starts =====
collected 15 items

tests/visual/test_home_page.py .....     [chromium]
tests/visual/test_home_page.py .....     [firefox]
tests/visual/test_home_page.py .....     [webkit]

===== 15 passed in 45.2s =====
```

## Acceptance Criteria

- [ ] Baseline snapshots generated for chromium browser (5 snapshots)
- [ ] Baseline snapshots generated for firefox browser (5 snapshots)
- [ ] Baseline snapshots generated for webkit browser (5 snapshots)
- [ ] Visual regression tests pass with 0 failures (was 15 failures)
- [ ] Baselines committed to repository in `qa/web/tests/visual/__snapshots__/`
- [ ] Snapshots reviewed for visual correctness
- [ ] CI QA workflow shows visual tests passing

## Related Files

- `qa/web/tests/visual/` - Visual regression test files
- `qa/web/tests/visual/__snapshots__/` - Baseline snapshot storage (to be created)
- `qa/web/conftest.py` - Pytest configuration for Playwright
- `.github/workflows/qa-automation.yml` - CI workflow running visual tests

## Dependencies

- Playwright browsers installed (`playwright install chromium firefox webkit`)
- Web server running on localhost:5000
- pytest-playwright-snapshot package installed

## Additional Notes

**Baseline Storage:**
- Snapshots are stored per-browser in separate directories
- File naming: `<test_name>-<browser>.png`
- Approximate total size: 2-5 MB (15 screenshots across 3 browsers)

**Visual Regression Detection:**
- After baselines are generated, any visual change will trigger test failure
- Use `--update-snapshots` flag to update baselines when intentional changes made
- Diff images generated automatically on failures for review

**CI Behavior:**
- CI will download baselines from repository
- Visual tests will compare against committed baselines
- Failures will upload diff images as artifacts

## Implementation Notes

*To be filled during implementation:*
- Actual baseline file structure
- Any baseline adjustments needed
- Screenshot dimensions and quality
- Total storage size
- Time taken to generate all baselines
