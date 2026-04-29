# Make QA Workflow Blocking After All Tests Pass

**GitHub Issue**: #439 - https://github.com/bdperkin/nhl-scrabble/issues/439

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

15 minutes

## Description

Remove `continue-on-error` flags from QA automation workflow to make it blocking once all test issues are resolved. Currently, the workflow runs tests but reports failures as warnings instead of failing CI, allowing PRs to be merged even with failing QA tests.

## Current State

QA automation workflow is currently non-blocking to allow infrastructure merge while application issues are being fixed:

```.github/workflows/qa-automation.yml (current state)
```yaml
- name: Run functional tests
  id: functional-tests
  run: |
    cd qa/web
    pytest tests/functional/ --browser=${{ matrix.browser }} ...
  continue-on-error: true  # ← Makes tests non-blocking

- name: Check test results
  if: always()
  continue-on-error: true  # ← Makes failures non-blocking
  run: |
    # Report results
    if [[ $TOTAL -gt 0 ]]; then
      echo "::warning::QA tests: $TOTAL failures"  # ← Warning, not error
      # NO exit 1 - workflow continues
    fi
```

**Workflow behavior:**
- Tests run on every PR
- Failures reported as GitHub warnings (⚠️)
- CI status: ✅ (green check even with failures)
- PRs can be merged with failing tests

## Proposed Solution

Once all QA test issues are resolved (visual baselines generated, accessibility violations fixed, functional tests debugged):

1. Remove `continue-on-error: true` from test steps
2. Change `::warning::` annotations back to `exit 1` failures
3. Make workflow block PR merges on test failures
4. Update workflow documentation to reflect "enforcing" status

### Changes to `.github/workflows/qa-automation.yml`

```yaml
# BEFORE (non-blocking):
- name: Run functional tests
  id: functional-tests
  run: |
    cd qa/web
    pytest tests/functional/ --browser=${{ matrix.browser }}
  continue-on-error: true  # ← REMOVE THIS

- name: Check test results
  if: always()
  continue-on-error: true  # ← REMOVE THIS
  run: |
    if [[ $TOTAL -gt 0 ]]; then
      echo "::warning::QA tests: $TOTAL failures"  # ← CHANGE TO exit 1
    fi

# AFTER (blocking):
- name: Run functional tests
  id: functional-tests
  run: |
    cd qa/web
    pytest tests/functional/ --browser=${{ matrix.browser }}
  # No continue-on-error - pytest failures will fail the workflow

- name: Check test results
  if: always()
  run: |
    if [[ $TOTAL -gt 0 ]]; then
      echo "::error::QA tests failed: $TOTAL failures"  # Changed to ::error::
      exit 1  # ← FAIL THE WORKFLOW
    fi
```

### Update workflow header comments

```yaml
# BEFORE:
# Current Status (Initial Implementation):
# - ✅ Functional tests: Mostly passing (1-2 known failures)
# - ⚠️  Visual tests: Expected failures (baselines not yet generated)
# - ⚠️  Accessibility tests: Real WCAG violations to fix
#
# Tests run as warnings (non-blocking) until issues are resolved.

# AFTER:
# QA Automation Status: ✅ ENFORCING
# All test suites passing and blocking PR merges on failures.
#
# Test Suites:
# - ✅ Functional tests: All passing
# - ✅ Visual regression: All passing
# - ✅ Accessibility: WCAG 2.1 AA compliant
# - ✅ Performance: Meeting benchmarks
```

## Implementation Steps

1. **Verify all QA test suites passing** (prerequisite check):
   ```bash
   cd qa/web

   # Functional: 0 failures
   pytest tests/functional/ --browser=chromium --browser=firefox --browser=webkit

   # Visual: 0 failures (baselines exist)
   pytest tests/visual/ --browser=chromium --browser=firefox --browser=webkit

   # Performance: 0 failures
   pytest tests/performance/ --browser=chromium --browser=firefox --browser=webkit

   # Accessibility: 0 failures
   pytest tests/accessibility/ --browser=chromium --browser=firefox --browser=webkit
   ```

2. **Edit `.github/workflows/qa-automation.yml`**:
   - Remove all `continue-on-error: true` lines
   - Change `::warning::` to `::error::`
   - Add `exit 1` on test failures
   - Update header comments to reflect enforcing status

3. **Update documentation**:
   - Update `CHANGELOG.md` with "QA tests now blocking"
   - Update `CLAUDE.md` CI/CD section to reflect enforcing status

4. **Create test PR** to verify blocking behavior:
   - Create branch with intentional test failure
   - Open PR and verify CI fails (red X)
   - Verify PR merge button disabled
   - Close test PR

5. **Push changes to main**

## Testing Strategy

**Pre-implementation verification:**
- ✅ All visual baselines generated (task 022 complete)
- ✅ All accessibility violations fixed (task 013 complete)
- ✅ All functional tests debugged (task 012 complete)
- ✅ Full test suite passes locally
- ✅ Full test suite passes in CI on a test branch

**Test blocking behavior:**
1. Create test branch: `test/qa-blocking-verification`
2. Intentionally break a test:
   ```python
   # qa/web/tests/functional/test_basic.py
   def test_intentional_failure():
       assert False, "Testing QA workflow blocking"
   ```
3. Push and create PR
4. Verify CI shows failed status (red X)
5. Verify PR cannot be merged (merge button disabled or shows "Checks must pass")
6. Verify error message shows in PR checks
7. Close test PR without merging

**Expected CI behavior:**
- ❌ Status check fails
- 🚫 PR merge blocked
- 📝 Detailed error in workflow log
- 💬 GitHub shows "Some checks were not successful"

## Acceptance Criteria

- [ ] All QA test suites consistently passing (0 failures)
- [ ] `continue-on-error` flags removed from all test steps
- [ ] Failure exit codes restored (`exit 1` on failures)
- [ ] `::error::` annotations used instead of `::warning::`
- [ ] Workflow header comments updated to reflect enforcing status
- [ ] `CHANGELOG.md` updated with QA enforcement change
- [ ] `CLAUDE.md` updated with QA enforcement status
- [ ] Workflow blocks PR merge on test failures
- [ ] Tested and verified with intentional test failure PR
- [ ] Test PR closed without merging

## Related Files

- `.github/workflows/qa-automation.yml` - QA automation workflow (main changes)
- `CHANGELOG.md` - Document QA enforcement
- `CLAUDE.md` - Update CI/CD section
- `tasks/testing/022-generate-visual-regression-baselines.md` - Dependency
- `tasks/bug-fixes/012-debug-functional-test-failures.md` - Dependency
- `tasks/bug-fixes/013-fix-wcag-accessibility-violations.md` - Dependency

## Dependencies

**Blocking dependencies (must be complete first):**
- ✅ Task 022: Generate visual regression baselines
- ✅ Task 012: Debug functional test failures
- ✅ Task 013: Fix WCAG 2.1 AA accessibility violations

**Verification:**
- All tests passing in CI (0 failures across all browsers)
- No known flaky tests
- Test infrastructure stable

## Additional Notes

**Why non-blocking initially:**
- Allowed QA infrastructure to be merged while app issues were fixed
- Provided visibility into test failures without blocking development
- Enabled iterative improvement of test suite

**Why make blocking now:**
- All known test issues resolved
- Test suite stable and reliable
- Ready to enforce quality standards on all PRs

**Rollback plan:**
- If tests become flaky after making blocking, can temporarily re-add `continue-on-error: true`
- Investigate and fix flakiness
- Re-enable blocking once stable

**Best practices:**
- Only make blocking when test suite is 100% stable
- Monitor first few PRs after making blocking for any issues
- Be prepared to quickly fix any new failures
- Consider notification to team before enabling

## Implementation Notes

*To be filled during implementation:*
- Date tests made blocking
- Any issues encountered during transition
- Number of lines changed in workflow file
- Test PR number used for verification
- Team communication approach
