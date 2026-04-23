# Migrate from Deprecated codecov/test-results-action to codecov/codecov-action

**GitHub Issue**: #285 - https://github.com/bdperkin/nhl-scrabble/issues/285

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

30min-1h

## Description

Update GitHub Actions CI workflow to migrate from the deprecated `codecov/test-results-action@v1` to the unified `codecov/codecov-action` with `report_type: test_results`. The older action is deprecated and will be removed by Codecov, requiring migration to the consolidated action.

## Current State

The CI workflow currently uses two different Codecov actions:

**Coverage Upload (`.github/workflows/ci.yml:73-80`):**

```yaml
  - name: Upload coverage to Codecov
    uses: codecov/codecov-action@v6
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: ./coverage.xml
      flags: unittests
      name: codecov-${{ matrix.python-version }}
      fail_ci_if_error: true
      verbose: true
```

**Test Results Upload - Test Job (`.github/workflows/ci.yml:82-89`):**

```yaml
  - name: Upload test results to Codecov
    if: always()
    uses: codecov/test-results-action@v1 # DEPRECATED
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: junit-py${{ matrix.python-version }}.xml
      fail_ci_if_error: false
      verbose: true
```

**Test Results Upload - Tox Job (`.github/workflows/ci.yml:169-176`):**

```yaml
  - name: Upload test results to Codecov
    if: always()
    uses: codecov/test-results-action@v1 # DEPRECATED
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: junit*.xml
      fail_ci_if_error: false
      verbose: true
```

**Issues:**

1. Using deprecated `codecov/test-results-action@v1`
1. Inconsistent action versions (v6 for coverage, v1 for test results)
1. Deprecated action will be removed, breaking CI
1. Missing modern features from unified action

## Proposed Solution

Migrate both test results uploads to use `codecov/codecov-action@v6` (matching the coverage upload version) with `report_type: test_results` parameter.

### Updated Test Job (lines 82-89)

```yaml
  - name: Upload test results to Codecov
    if: always()
    uses: codecov/codecov-action@v6
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: junit-py${{ matrix.python-version }}.xml
      report_type: test_results
      fail_ci_if_error: false
      verbose: true
```

### Updated Tox Job (lines 169-176)

```yaml
  - name: Upload test results to Codecov
    if: always()
    uses: codecov/codecov-action@v6
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: junit*.xml
      report_type: test_results
      fail_ci_if_error: false
      verbose: true
```

### Benefits

1. **No deprecation warnings**: Uses actively maintained action
1. **Consistent action versions**: All Codecov uploads use v6
1. **Unified action**: Single action for both coverage and test results
1. **Future-proof**: Will receive updates and new features
1. **Better integration**: Improved Codecov dashboard integration
1. **Guaranteed uploads**: `if: always()` ensures upload even on test failures

## Implementation Steps

1. **Update test job test results upload** (10 min)

   - Locate `.github/workflows/ci.yml` lines 82-89
   - Replace `codecov/test-results-action@v1` with `codecov/codecov-action@v6`
   - Add `report_type: test_results` parameter
   - Verify all other parameters remain the same
   - Keep `if: always()` to ensure upload on failures

1. **Update tox job test results upload** (10 min)

   - Locate `.github/workflows/ci.yml` lines 169-176
   - Replace `codecov/test-results-action@v1` with `codecov/codecov-action@v6`
   - Add `report_type: test_results` parameter
   - Verify all other parameters remain the same
   - Keep `if: always()` to ensure upload on failures

1. **Verify workflow syntax** (5 min)

   - Run `yamllint .github/workflows/ci.yml`
   - Check for YAML syntax errors
   - Validate workflow with GitHub Actions validator

1. **Test in pull request** (10-20 min)

   - Create feature branch
   - Commit workflow changes
   - Push to GitHub
   - Create PR
   - Monitor CI run
   - Verify test results upload to Codecov
   - Check Codecov dashboard shows test results

1. **Verify Codecov dashboard** (5 min)

   - Check https://app.codecov.io/gh/bdperkin/nhl-scrabble
   - Verify test results appear in dashboard
   - Verify both coverage and test results show correctly
   - Confirm no upload errors in CI logs

1. **Update documentation if needed** (5 min)

   - Check if CLAUDE.md mentions test results action
   - Update any references to deprecated action
   - Document unified action approach

## Testing Strategy

### Pre-implementation Testing

```bash
# Validate YAML syntax
yamllint .github/workflows/ci.yml

# Check for workflow syntax errors
gh workflow view ci.yml
```

### Post-implementation Testing

1. **Create test PR**

   - Make a trivial change (e.g., comment in test file)
   - Push to feature branch
   - Create PR to trigger CI

1. **Monitor CI execution**

   - Watch test job: `gh run watch`
   - Verify test results upload step succeeds
   - Check for deprecation warnings (should be none)
   - Verify `if: always()` runs upload even if tests fail

1. **Verify Codecov integration**

   - Check PR comments from Codecov bot
   - Verify test results visible in Codecov dashboard
   - Confirm coverage report still works
   - Check both jobs upload successfully (test + tox)

### Validation Checklist

- [ ] YAML syntax valid (`yamllint` passes)
- [ ] Workflow syntax valid (GitHub Actions validates)
- [ ] Test job uploads test results successfully
- [ ] Tox job uploads test results successfully
- [ ] No deprecation warnings in CI logs
- [ ] Codecov dashboard shows test results
- [ ] Coverage upload still works (not affected)
- [ ] `if: always()` ensures upload on test failures
- [ ] All CI checks pass

## Acceptance Criteria

- [ ] `.github/workflows/ci.yml` test job (lines 82-89) uses `codecov/codecov-action@v6` with `report_type: test_results`
- [ ] `.github/workflows/ci.yml` tox job (lines 169-176) uses `codecov/codecov-action@v6` with `report_type: test_results`
- [ ] No usage of deprecated `codecov/test-results-action@v1` remains
- [ ] All Codecov uploads use consistent action version (v6)
- [ ] YAML syntax is valid (yamllint passes)
- [ ] CI workflow validates successfully
- [ ] Test results upload to Codecov in PR
- [ ] Codecov dashboard displays test results correctly
- [ ] No deprecation warnings in CI logs
- [ ] All CI checks pass in test PR

## Related Files

- `.github/workflows/ci.yml` - Main CI workflow with test results uploads

## Dependencies

None - standalone workflow update

## Additional Notes

### Why codecov-action@v6 instead of v5?

The task description mentioned v5, but the project already uses `codecov/codecov-action@v6` for coverage uploads (line 73). For consistency and to use the latest version, we'll migrate to v6 rather than v5.

### Why report_type Parameter?

The `report_type: test_results` parameter tells the unified `codecov-action` to treat the files as test result data (JUnit XML) rather than coverage data. This allows the same action to handle both:

- Coverage: `files: coverage.xml` (default report_type)
- Test results: `files: junit*.xml` with `report_type: test_results`

### Backward Compatibility

The migration is backward compatible:

- Same token authentication
- Same file upload mechanism
- Same Codecov dashboard integration
- No changes to Codecov configuration (`.codecov.yml`)

### if: always() Behavior

Both upload steps use `if: always()` to ensure test results are uploaded even if:

- Tests fail
- Linting fails
- Previous steps error

This is critical for debugging test failures in CI, as we need the JUnit XML even (especially) when tests fail.

### Fail on Error Setting

Note the different `fail_ci_if_error` values:

- **Coverage upload**: `true` - CI fails if coverage upload fails
- **Test results upload**: `false` - CI continues if test results upload fails

This is intentional: coverage is critical for merge decisions, while test results are informational. The migration preserves this behavior.

### Deprecation Timeline

According to Codecov's announcement:

- `codecov/test-results-action` is deprecated
- Will be removed in a future date (TBD)
- Migration to unified action recommended immediately
- No breaking changes expected during migration

### Performance Impact

No performance impact expected:

- Same upload mechanism
- Same API endpoints
- Unified action may be slightly faster (single implementation)

### Security Considerations

Security remains the same:

- Uses existing `CODECOV_TOKEN` secret
- Same authentication mechanism
- Same upload security
- Action maintained by Codecov (trusted source)

### Alternative Approaches Considered

**Option 1: Keep deprecated action until removed**

- ❌ Will break CI when action is removed
- ❌ May miss new features and improvements
- ❌ Deprecation warnings clutter CI logs

**Option 2: Migrate to codecov-action@v5 (as task described)**

- ⚠️ Inconsistent with existing v6 usage for coverage
- ⚠️ Would require maintaining two action versions

**Option 3: Migrate to codecov-action@v6 (SELECTED)**

- ✅ Consistent with existing coverage upload
- ✅ Latest stable version
- ✅ Single action version to maintain
- ✅ Future-proof

### Future Enhancements

After this migration, consider:

1. Consolidating coverage and test results into single step (if possible)
1. Adding test result trending/analysis
1. Configuring test failure notifications
1. Adding test timing data to Codecov

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Codecov dashboard behavior verification
