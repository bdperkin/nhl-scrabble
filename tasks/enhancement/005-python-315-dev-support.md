# Add Python 3.15-dev Development Support

**GitHub Issue**: #98 - https://github.com/bdperkin/nhl-scrabble/issues/98

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Add development/experimental support for Python 3.15-dev to enable early compatibility testing and identify potential issues before the official Python 3.15 release. This is for proactive testing only - failures on Python 3.15-dev must NOT block CI/CD pipeline or prevent other tests from passing.

**Key Constraint**: Python 3.15-dev test failures should be informational only and MUST NOT cause CI to fail if all other Python versions pass.

## Current State

The project currently supports Python 3.10-3.13 (official releases):

**pyproject.toml**:

```toml
[project]
requires-python = ">=3.10,<3.14"  # Will be <3.15 after task #97
classifiers = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
```

**CI Workflow (.github/workflows/ci.yml)**:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12", "3.13"]
```

**Tox Configuration (tox.ini)**:

```ini
env_list =
    py{313, 312, 311, 310}
```

**Issues**:

- No testing on Python 3.15-dev to catch compatibility issues early
- Cannot proactively identify breaking changes before Python 3.15 release
- May miss opportunities to provide feedback to Python core developers
- Reactive rather than proactive approach to new Python versions

## Proposed Solution

Add Python 3.15-dev support for **experimental testing only**, with explicit handling to prevent CI failures:

### 1. Update CI Workflow (Non-Blocking)

Add Python 3.15-dev to test matrix with `continue-on-error: true`:

**.github/workflows/ci.yml**:

```yaml
jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
        experimental: [false]
        include:
          - python-version: "3.15-dev"
            experimental: true

    continue-on-error: ${{ matrix.experimental }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      # ... rest of steps
```

**Key Points**:

- `continue-on-error: ${{ matrix.experimental }}` allows 3.15-dev to fail without blocking CI
- Separate matrix entry for 3.15-dev marked as experimental
- All other Python versions remain required to pass

### 2. Update Tox Configuration (Optional)

Add py315 to tox for local testing, marked as optional:

**tox.ini**:

```ini
[tox]
env_list =
    py{314, 313, 312, 311, 310}
    # py315 is optional/experimental - not in default env_list
skip_missing_interpreters = true

[testenv:py315]
description = Experimental testing on Python 3.15-dev (optional)
extras =
    test
commands_pre =
    pytest --version
commands =
    pytest {posargs:tests/}
```

**Alternatively**, add to env_list but allow failures:

```ini
env_list =
    py{315, 314, 313, 312, 311, 310}
ignore_outcome =
    py315: true
```

### 3. DO NOT Update pyproject.toml

**Important**: Do NOT update `requires-python` or add Python 3.15 classifier:

```toml
# ❌ DO NOT DO THIS:
requires-python = ">=3.10,<3.16"  # Wrong - 3.15 is not released
classifiers = [
    "Programming Language :: Python :: 3.15",  # Wrong - not official
]

# ✅ KEEP AS IS (or <3.15 after task #97):
requires-python = ">=3.10,<3.15"  # Only released versions
# No 3.15 classifier until official release
```

### 4. Update Documentation

Add note about experimental Python 3.15-dev support:

**README.md** (optional section):

```markdown
## Requirements

- **Supported**: Python 3.10, 3.11, 3.12, 3.13, 3.14
- **Experimental**: Python 3.15-dev (CI testing only, may have issues)
```

**CLAUDE.md** (CI/CD section):

```markdown
### CI/CD

The project tests on multiple Python versions:

- **Required**: Python 3.10, 3.11, 3.12, 3.13, 3.14 (must all pass)
- **Experimental**: Python 3.15-dev (`continue-on-error: true`, informational only)

Python 3.15-dev is tested for early compatibility checking but failures do not block CI.
```

### 5. Add CI Status Badge (Optional)

Add separate badge for Python 3.15-dev status:

**README.md**:

```markdown
![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)
![Python 3.15-dev](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=main&event=push&label=Python%203.15-dev)
```

## Implementation Steps

1. **Update CI Workflow**

   - Add Python 3.15-dev to test matrix with `experimental: true`
   - Add `continue-on-error: ${{ matrix.experimental }}`
   - Test that CI passes even if 3.15-dev fails

1. **Update Tox Configuration** (Optional)

   - Add `[testenv:py315]` environment
   - Mark as optional/experimental in description
   - Decide: env_list inclusion vs manual invocation

1. **Update Documentation**

   - Add note to README.md about experimental 3.15-dev support
   - Update CLAUDE.md CI/CD section
   - Add warning that 3.15-dev may have issues

1. **Local Testing** (If Python 3.15-dev available)

   - Install Python 3.15-dev (via pyenv or manual build)
   - Run `tox -e py315` to verify setup
   - Document any compatibility issues found

1. **Commit Changes**

   - Create feature branch
   - Commit CI and tox updates
   - Push to GitHub

1. **Verify CI Behavior**

   - Create PR
   - Verify Python 3.15-dev tests run
   - Verify CI passes even if 3.15-dev fails
   - Confirm other Python versions still required to pass

## Testing Strategy

### CI/CD Testing

The primary testing is automated via CI:

```yaml
# Python 3.15-dev tests run automatically
# Failures are logged but don't block CI
# Check Actions tab for 3.15-dev status
```

### Local Testing (Optional)

If Python 3.15-dev is available locally:

```bash
# Build Python 3.15-dev from source
git clone https://github.com/python/cpython.git
cd cpython
git checkout main  # or 3.15 branch when available
./configure --prefix=$HOME/.pyenv/versions/3.15-dev
make
make install

# Or use pyenv
pyenv install 3.15-dev

# Test with tox
tox -e py315

# Test directly
python3.15 -m pip install -e ".[test]"
python3.15 -m pytest
```

### Verify Non-Blocking Behavior

Test that CI passes when 3.15-dev fails:

1. Create PR with intentional 3.15-dev failure
1. Verify CI shows green checkmark overall
1. Verify 3.15-dev job shows as failed but with warning icon
1. Confirm PR can be merged despite 3.15-dev failure

## Acceptance Criteria

- [ ] Python 3.15-dev added to CI test matrix
- [ ] `continue-on-error: true` set for 3.15-dev tests
- [ ] CI passes when 3.15-dev fails but other versions pass
- [ ] CI still fails when any official Python version fails
- [ ] Tox includes py315 environment (optional or in env_list)
- [ ] `pyproject.toml` NOT updated with 3.15 (intentionally)
- [ ] Documentation notes experimental 3.15-dev support
- [ ] README.md clarifies 3.15-dev is experimental
- [ ] CLAUDE.md explains non-blocking CI behavior
- [ ] Python 3.15-dev tests run on every CI execution
- [ ] Failures are visible but informational only

## Related Files

- `.github/workflows/ci.yml` - CI/CD workflow with test matrix
- `tox.ini` - Tox environments (optional py315)
- `README.md` - User documentation (experimental support note)
- `CLAUDE.md` - Developer documentation (CI behavior)
- `pyproject.toml` - **NOT modified** (no 3.15 support yet)

## Dependencies

- **Optional Dependency**: Task #97 (Python 3.14 support)
  - If #97 is complete, builds on that work
  - If not, can be implemented independently
- **No Hard Dependencies**: This task is standalone

## Additional Notes

### Python 3.15 Timeline

- **Development**: Currently in development (as of 2026-04-17)
- **Expected Release**: October 2026 (estimated)
- **Alpha Releases**: Starting around May-June 2026
- **Beta Releases**: Starting around July-August 2026
- **RC Releases**: September 2026

### Why Test on 3.15-dev?

1. **Early Detection**: Find breaking changes before they affect users
1. **Proactive Fixes**: Address compatibility issues during development
1. **Feedback Loop**: Provide feedback to Python core developers
1. **Future-Proofing**: Be ready for 3.15 release day
1. **Best Practice**: Industry standard for library/framework projects

### Non-Blocking Strategy

The `continue-on-error: true` approach:

**Advantages**:

- CI remains green for stable Python versions
- Failures are visible but don't block development
- Can merge PRs despite 3.15-dev issues
- Gradual migration path as 3.15 stabilizes

**Disadvantages**:

- 3.15-dev failures might be ignored
- Requires manual monitoring of test results
- No enforcement until we're ready

**Mitigation**:

- Regular review of 3.15-dev test results
- Track issues in GitHub Issues when found
- Upgrade to required testing when 3.15 RC released

### Experimental vs Official Support

|                    | Experimental (3.15-dev)  | Official (3.10-3.14) |
| ------------------ | ------------------------ | -------------------- |
| CI Testing         | Yes (non-blocking)       | Yes (required)       |
| pyproject.toml     | No                       | Yes                  |
| Classifiers        | No                       | Yes                  |
| User Documentation | "Experimental, may fail" | "Fully supported"    |
| Bug Priority       | Low (nice to fix)        | High (must fix)      |
| CI Failure         | Warning only             | Blocks merge         |

### Migration Path

When Python 3.15 is officially released:

1. Update this task to change 3.15-dev → 3.15
1. Remove `continue-on-error` for 3.15
1. Update pyproject.toml with 3.15 support (new task or expand #97)
1. Add Python 3.15 classifier
1. Update documentation to list 3.15 as officially supported
1. Create new task for 3.16-dev

### Testing Frequency

Python 3.15-dev tests run:

- ✅ On every push to main
- ✅ On every pull request
- ✅ During scheduled/manual workflow runs
- ❌ Not required for merge approval

### Monitoring 3.15-dev Failures

Recommended approach:

1. **Weekly Review**: Check Actions tab for 3.15-dev status
1. **Issue Tracking**: Create issues for reproducible failures
1. **Labels**: Use `python-3.15` and `experimental` labels
1. **Prioritization**: Fix when feasible, not blocking
1. **Communication**: Note known issues in documentation

### Breaking Changes to Watch For

Python 3.15 may include:

- Changes to typing system (PEP updates)
- Deprecated features removed
- New syntax features
- Standard library changes
- Performance improvements affecting tests
- Changes to error messages (affecting test assertions)

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Python 3.15-dev availability at time of implementation
- Any immediate compatibility issues discovered
- CI configuration adjustments needed
- Whether tox env_list inclusion was used
- Monitoring strategy adopted
- First breaking changes found (if any)
