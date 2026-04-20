# Optimize Tox Execution with Parallel and Fail-Fast Behavior

**GitHub Issue**: #283 - https://github.com/bdperkin/nhl-scrabble/issues/283

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-5 hours

## Description

Enhance the tox configuration to support intelligent parallel execution with fail-fast behavior. Currently, tox runs environments sequentially by default, which is slow for local development and CI. This task implements parallel execution strategies with smart dependency ordering and fail-fast capabilities to improve developer productivity while maintaining test reliability.

## Current State

**Current tox Behavior:**

- Sequential execution by default (`tox`)
- Manual parallel execution with `tox -p auto` or `make tox-parallel`
- All environments run to completion even if one fails (in parallel mode)
- No dependency ordering between test environments
- ~3-5 minutes for full tox run in parallel mode
- ~10-15 minutes for sequential execution

**Current Makefile Targets:**

```makefile
# Sequential execution (default)
tox:
	tox

# Parallel execution (manual)
tox-parallel:
	tox -p auto

# Specific environment
tox-%:
	tox -e $*
```

**Current tox.ini:**

```ini
[tox]
env_list = py{310,311,312,313,314},py315,ruff-check,mypy,coverage,...
skip_missing_interpreters = true

[testenv]
# No dependencies configured
# No fail-fast configuration
```

**Pain Points:**

1. Developers must remember to use `make tox-parallel` for speed
1. Failed environments don't stop execution early (waste time)
1. No logical grouping (quality checks → tests → coverage)
1. Hard to identify which environment failed first
1. CI runs all checks even if critical ones fail early

## Proposed Solution

Implement a tiered parallel execution strategy with environment dependencies and fail-fast behavior.

### 1. Environment Dependencies

Organize environments into logical tiers using `depends`:

```ini
[tox]
env_list =
    # Tier 1: Fast quality checks (run first, fail-fast)
    ruff-check,
    ruff-format,
    flake8,
    # Tier 2: Type checking and linting (depends on tier 1)
    mypy,
    isort,
    interrogate,
    # Tier 3: Tests (depends on tier 2)
    py{310,311,312,313,314},
    py315,
    # Tier 4: Coverage and reporting (depends on tier 3)
    coverage,
    diff-cover

[testenv:mypy]
depends = ruff-check, ruff-format, flake8
description = Run type checking (mypy)
# ... rest of config

[testenv:py{310,311,312,313,314}]
depends = mypy, isort, interrogate
description = Run tests with Python {envname}
# ... rest of config

[testenv:coverage]
depends = py310, py311, py312, py313, py314
description = Run tests with coverage reporting
# ... rest of config
```

**Tier Strategy:**

- **Tier 1**: Fast formatters/linters (5-15s each) - fail immediately if code quality is bad
- **Tier 2**: Type checking and advanced linting (15-30s each) - catch type errors before running tests
- **Tier 3**: Test suites (1-2min each) - run tests in parallel across Python versions
- **Tier 4**: Coverage and reports (1-2min) - only run if all tests pass

### 2. Update Makefile for Smart Defaults

```makefile
# Default to parallel execution with fail-fast via dependencies
.PHONY: tox
tox:
	@echo "Running tox with parallel execution and fail-fast..."
	tox run-parallel --parallel-no-spinner

# Explicit parallel (keep for compatibility)
.PHONY: tox-parallel
tox-parallel:
	@echo "Running tox in parallel mode..."
	tox -p auto

# Sequential execution (when debugging)
.PHONY: tox-sequential
tox-sequential:
	@echo "Running tox sequentially..."
	tox run

# Fast fail-fast for pre-commit (critical checks only)
.PHONY: tox-quick
tox-quick:
	@echo "Running quick tox checks (fail-fast)..."
	tox -e ruff-check,ruff-format,mypy,py310
```

### 3. CI-Level Fail-Fast

Update GitHub Actions workflow to fail-fast at the matrix level:

```yaml
# .github/workflows/ci.yml
jobs:
  tox:
    name: Tox tests with UV (${{ matrix.tox-env }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true  # Stop all jobs if one fails
      matrix:
        tox-env:
          # Critical checks first
          - ruff-check
          - ruff-format
          - mypy
          # Then tests
          - py310
          - py311
          - py312
          - py313
          - py314
          # Then coverage
          - coverage
```

### 4. Add Tox Configuration Options

```ini
[tox]
# Parallel execution configuration
parallel_show_output = true  # Show output during parallel runs
skip_missing_interpreters = true

# Labels for logical grouping
labels =
    critical = ruff-check, ruff-format, flake8
    quality = mypy, isort, interrogate, pydocstyle
    test = py{310,311,312,313,314}
    coverage = coverage, diff-cover

[testenv]
# Fail fast on first error
setenv =
    PYTEST_ADDOPTS = -x  # Stop pytest on first failure
```

### 5. Document New Behavior

Update documentation to explain the new execution model:

**CONTRIBUTING.md:**

````markdown
## Testing with Tox

The project uses tox with intelligent parallel execution and fail-fast behavior:

### Default Behavior

```bash
make tox  # Parallel execution with tier-based dependencies
````

Execution tiers:

1. **Fast quality checks** (ruff, flake8) - fail immediately if code quality issues
1. **Type checking** (mypy, isort) - only runs if tier 1 passes
1. **Tests** (py310-314) - parallel across Python versions, only if tier 2 passes
1. **Coverage** - only runs if all tests pass

### Execution Modes

```bash
make tox              # Default: parallel with fail-fast dependencies
make tox-parallel     # Pure parallel (all environments)
make tox-sequential   # Sequential (for debugging)
make tox-quick        # Critical checks only (fast fail-fast)

# Run specific tier
tox -m critical       # Fast quality checks only
tox -m test          # Just tests
```

### Fail-Fast Behavior

- **Local**: Dependencies ensure tier-based fail-fast
- **CI**: GitHub Actions fail-fast stops all jobs if one fails
- **Debugging**: Use `make tox-sequential` to see all failures

````

## Implementation Steps

1. **Update tox.ini with dependencies** (1-2h)

   - Add `depends` to testenv configurations
   - Organize environments into logical tiers
   - Add `labels` for grouping
   - Configure `parallel_show_output` and other options
   - Test dependency ordering: `tox --showconfig`

2. **Update Makefile targets** (30min)

   - Change default `tox` target to use parallel execution
   - Add `tox-sequential` for debugging
   - Add `tox-quick` for fast fail-fast
   - Update target documentation
   - Test all new targets

3. **Update CI workflow** (30min)

   - Add `fail-fast: true` to tox matrix strategy
   - Reorder matrix to put critical checks first
   - Test workflow changes (may need to push to branch)

4. **Update documentation** (1h)

   - Update CONTRIBUTING.md with new tox behavior
   - Update CLAUDE.md with execution model
   - Update README.md if needed
   - Document all Makefile targets in reference docs

5. **Testing and validation** (1h)

   - Test `make tox` works correctly
   - Verify tier-based execution order
   - Test fail-fast behavior (introduce intentional failure)
   - Verify sequential mode still works
   - Test in CI (create test PR)

6. **Update related documentation** (30min)

   - Update docs/how-to/run-tests.md
   - Update docs/reference/makefile.md
   - Add troubleshooting section for tox issues

## Testing Strategy

### Manual Testing

1. **Test Tier Dependencies**

   ```bash
   # Introduce a ruff error
   echo "bad syntax" > src/nhl_scrabble/test_bad.py

   # Should fail in tier 1 and skip remaining tiers
   make tox

   # Clean up
   rm src/nhl_scrabble/test_bad.py
````

2. **Test Parallel Execution**

   ```bash
   # Should run all tiers in parallel (within tier constraints)
   time make tox

   # Compare to sequential
   time make tox-sequential
   ```

1. **Test Quick Mode**

   ```bash
   # Should only run critical checks
   make tox-quick
   ```

1. **Test Labels**

   ```bash
   tox -m critical  # Should run ruff-check, ruff-format, flake8
   tox -m test     # Should run py310-314
   ```

### Automated Testing

- Verify tox configuration is valid: `tox --showconfig`
- Run full tox suite: `make tox`
- Test CI workflow in PR
- Verify all Makefile targets work

### Performance Validation

Compare execution times:

- **Before** (sequential): ~10-15 minutes
- **Before** (manual parallel): ~3-5 minutes
- **After** (smart parallel): ~3-5 minutes (same speed, better fail-fast)
- **After** (quick mode): ~30-60 seconds (critical checks only)

### Validation Checklist

- [ ] `make tox` runs in parallel with dependencies
- [ ] Tier 1 failure prevents Tier 2 from running
- [ ] Test failures prevent coverage from running
- [ ] `make tox-quick` runs only critical checks
- [ ] Labels work correctly (`tox -m critical`)
- [ ] CI fail-fast stops on first failure
- [ ] Documentation is accurate
- [ ] All Makefile targets documented

## Acceptance Criteria

- [ ] `tox.ini` includes environment dependencies organized in tiers
- [ ] Default `make tox` uses parallel execution with smart fail-fast
- [ ] `make tox-quick` runs critical checks only (fast fail-fast)
- [ ] `make tox-sequential` available for debugging
- [ ] Tox labels configured for logical grouping
- [ ] CI workflow uses `fail-fast: true`
- [ ] CONTRIBUTING.md documents new tox behavior
- [ ] Makefile targets documented in docs/reference/makefile.md
- [ ] Tier-based execution order verified
- [ ] Performance is maintained or improved
- [ ] Fail-fast behavior works as expected
- [ ] All tests pass

## Related Files

- `tox.ini` - Add dependencies and labels
- `Makefile` - Update tox targets
- `.github/workflows/ci.yml` - Add fail-fast strategy
- `CONTRIBUTING.md` - Document new behavior
- `CLAUDE.md` - Update testing section
- `docs/how-to/run-tests.md` - Update testing guide
- `docs/reference/makefile.md` - Document new targets

## Dependencies

None - this is a configuration enhancement

## Additional Notes

### Why Tier-Based Dependencies?

**Benefits:**

- **Fail-fast**: Stop early when quality checks fail (no point running tests if code doesn't lint)
- **Logical ordering**: Quality → Types → Tests → Coverage
- **Better feedback**: See what failed first, not buried in test output
- **Resource efficiency**: Don't waste time/CPU on tests if code won't merge anyway

**Trade-offs:**

- Slightly more complex tox.ini
- Need to understand tier concept
- May not catch all failures in one run (by design)

### Execution Time Analysis

**Current Sequential** (~10-15 min):

```
ruff-check (15s) → ruff-format (15s) → flake8 (20s) → mypy (30s) →
py310 (90s) → py311 (90s) → ... → coverage (90s)
```

**Current Parallel** (~3-5 min):

```
All environments run simultaneously
Finishes when slowest completes (py314 ~2min)
```

**Proposed Tiered Parallel** (~3-5 min):

```
Tier 1 (parallel): ruff-check, ruff-format, flake8 → 20s
↓ (if pass)
Tier 2 (parallel): mypy, isort, interrogate → 30s
↓ (if pass)
Tier 3 (parallel): py310, py311, py312, py313, py314 → 2min
↓ (if pass)
Tier 4: coverage, diff-cover → 90s

Total: ~3min 20s (same as current parallel, but fail-fast)
```

**Quick Mode** (~30-60s):

```
Tier 1 (critical): ruff-check, ruff-format, mypy, py310 → 60s
Skip everything else
```

### Tox Label Examples

```bash
# Run only critical quality checks
tox -m critical

# Run all tests
tox -m test

# Run coverage and reports
tox -m coverage

# Run multiple labels
tox -m critical -m quality
```

### CI Fail-Fast Impact

**Without fail-fast** (current):

- All 44 jobs run even if ruff-check fails immediately
- Wastes ~5 minutes of CI time
- Hard to identify root cause in sea of failures

**With fail-fast**:

- ruff-check fails → all other jobs cancelled immediately
- Saves CI resources
- Clear feedback on what broke

### Migration Notes

**Breaking Changes**: None

- Default behavior changes from sequential to parallel
- Users can use `make tox-sequential` if they prefer old behavior
- CI behavior more aggressive (fail-fast) but faster feedback

**Backwards Compatibility**:

- All existing `tox -e <env>` commands still work
- All existing Makefile targets preserved
- New targets added, none removed

### Performance Implications

**Benefits:**

- Same or better performance as current parallel
- Fail-fast saves time on failures
- Quick mode for rapid iteration

**Considerations:**

- Dependencies create serialization (tier 1 → tier 2 → tier 3)
- But tiers are fast, so minimal impact
- Parallel execution within tiers maintains performance

### Security Considerations

No security impact - configuration change only.

### Future Enhancements

- Add more granular labels (e.g., `fast`, `slow`, `required`, `optional`)
- Environment-specific pytest options (e.g., faster tests in quick mode)
- Auto-detect which tier failed and suggest fixes
- Integration with pre-commit hooks (run quick mode automatically)
