# Debug Functional Test Failures in QA Suite

**GitHub Issue**: #438 - https://github.com/bdperkin/nhl-scrabble/issues/438

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Investigate and fix 1-2 functional test failures per browser related to API endpoint validation and form submission timing. These failures are intermittent and appear to be timing-related or state management issues.

## Current State

Some functional tests are intermittently failing across browsers:

```bash
$ cd qa/web && pytest tests/functional/
# Failures (approximately 1-2 per browser, 3-6 total):

# All browsers:
# - test_api_endpoint_with_invalid_parameters
#   Location: tests/functional/test_error_handling.py::test_api_endpoint_with_invalid_parameters
#   Issue: API returning unexpected status code
#   Expected: 200, 400, or 422
#   Actual: Unknown (needs investigation)

# Firefox only:
# - test_concurrent_submissions_handled
#   Location: tests/functional/test_error_handling.py::test_concurrent_submissions_handled
#   Issue: Second submission not returning expected number of results
#   Expected: Results visible
#   Actual: Timing issue or state management problem
```

## Proposed Solution

1. **Analyze test failure logs** to identify exact failing tests
2. **Debug API endpoint validation logic** in application code
3. **Fix form submission timing/race conditions** in tests or application
4. **Add proper wait conditions** where needed in tests
5. **Ensure tests are properly isolated** (no shared state)

### API Endpoint Validation Fix

```python
# src/nhl_scrabble/web/routes.py
@app.get("/api/analyze")
async def api_analyze(top_players: int = Query(default=20, ge=1, le=100)):
    """Analyze NHL Scrabble scores via API.

    Validates input parameters and returns 400 on invalid values.
    """
    # FastAPI automatically validates with Query(ge=1, le=100)
    # Returns 422 on validation failure
    ...
```

### Form Submission Test Fix

```python
# qa/web/tests/functional/test_error_handling.py
def test_concurrent_submissions_handled(page_fixture: Page) -> None:
    """Verify concurrent form submissions are handled properly."""
    page_fixture.goto("http://localhost:5000/")
    page_fixture.wait_for_load_state("networkidle")

    # Disable cache for testing
    page_fixture.locator("#useCache").uncheck()

    # Start first submission
    page_fixture.fill("#topPlayers", "10")
    page_fixture.click("#analyzeBtn")

    # Wait for FIRST request to complete
    page_fixture.wait_for_selector("#results", state="visible", timeout=30000)

    # Clear previous results explicitly
    # Then start second submission
    page_fixture.fill("#topPlayers", "20")
    page_fixture.click("#analyzeBtn")

    # Wait for results to update (with proper wait condition)
    page_fixture.wait_for_function(
        "document.querySelectorAll('#playersTable tbody tr').length === 20",
        timeout=30000
    )

    results = page_fixture.locator("#results")
    expect(results).to_be_visible()
```

## Implementation Steps

1. **Review latest QA test run logs** for functional failures
   - Download artifacts from GitHub Actions run
   - Extract failure messages and stack traces
   - Categorize by failure type
2. **Identify specific failing tests** by name and browser
   - Create matrix: test_name × browser × failure_reason
   - Identify patterns (all browsers vs specific browsers)
3. **Run failing tests locally** with --verbose
   ```bash
   cd qa/web
   pytest tests/functional/test_error_handling.py::test_api_endpoint_with_invalid_parameters \
     --browser=chromium --verbose --tb=long
   ```
4. **Debug root causes:**
   - API endpoint validation edge cases
   - Form submission async timing
   - Element state transitions
   - Network request handling
5. **Implement fixes** in test code or application code as needed
   - Update test wait conditions
   - Fix application API validation
   - Improve state management
6. **Add explicit waits** if timing-related
   - Use `wait_for_selector` instead of `wait_for_timeout`
   - Use `wait_for_function` for complex conditions
   - Use `wait_for_load_state("networkidle")` for network requests
7. **Verify fixes across all three browsers**
   ```bash
   pytest tests/functional/ --browser=chromium
   pytest tests/functional/ --browser=firefox
   pytest tests/functional/ --browser=webkit
   ```

## Testing Strategy

**Verification:**
- Run functional tests multiple times to verify stability (5+ runs)
- Test across all browsers (chromium, firefox, webkit)
- Verify no regressions in other functional tests
- Run in CI environment to verify not just local fixes

**Stability testing:**
```bash
# Run functional tests 5 times to check for flakiness
for i in {1..5}; do
  echo "Run $i/5"
  pytest tests/functional/ --browser=chromium -v || echo "FAIL on run $i"
done
```

## Acceptance Criteria

- [ ] All functional test failures identified and categorized by type
- [ ] API endpoint validation issues fixed (if application bug)
- [ ] Form submission timing issues fixed (if application bug)
- [ ] Test wait conditions improved (if test infrastructure issue)
- [ ] Functional tests pass consistently with 0 failures
- [ ] Tests verified across all three browsers (chromium, firefox, webkit)
- [ ] No new test failures introduced
- [ ] Tests run 5+ times without failures (stability verified)

## Related Files

- `qa/web/tests/functional/test_error_handling.py` - Error handling functional tests
- `qa/web/tests/functional/test_form_submission.py` - Form submission tests
- `src/nhl_scrabble/web/routes.py` - API endpoint handlers
- `src/nhl_scrabble/web/static/js/app.js` - Frontend JavaScript
- `qa/web/conftest.py` - Pytest fixtures and configuration

## Dependencies

- Web server running (nhl-scrabble serve)
- Playwright browsers installed
- pytest-playwright package
- Access to GitHub Actions logs for failure analysis

## Additional Notes

**Common Playwright Timing Issues:**
- **Problem**: Tests fail intermittently due to timing
- **Solution**: Use built-in Playwright auto-waiting, not `sleep()`
- **Best practice**: `wait_for_selector()` > `wait_for_timeout()`

**API Validation:**
- FastAPI Query validation happens before route handler
- Returns 422 for validation errors (not 400)
- Test should accept both 400 and 422 as valid error responses

**Form Submission State:**
- Frontend may cache results from first submission
- Need to verify JavaScript clears previous results properly
- Test should wait for specific DOM changes, not just element visibility

**Browser-Specific Failures:**
- Firefox has stricter timing requirements than Chromium
- WebKit has different JavaScript execution timing
- Use `wait_for_function()` for cross-browser consistency

## Implementation Notes

*To be filled during implementation:*
- Exact failing tests and failure modes
- Root cause analysis for each failure
- Application code changes vs test code changes
- Timing adjustments made
- Stability test results
- Any remaining edge cases
