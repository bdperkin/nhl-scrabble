# Add diff-cover for PR Coverage Reporting

**GitHub Issue**: #124 - https://github.com/bdperkin/nhl-scrabble/issues/124

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

30-60 minutes

## Description

Add diff-cover to report test coverage only on changed lines in pull requests, making it easier to see if new code has adequate test coverage without noise from existing codebase coverage.

Currently, pytest-cov reports coverage across the entire codebase (currently ~50% overall). When reviewing a PR, it's hard to answer the key question: "Is the NEW code in this PR tested?" You have to manually compare coverage reports before and after, or rely on Codecov's PR comments.

diff-cover solves this by:

- Comparing coverage reports against git diffs
- Showing coverage ONLY for lines that changed
- Reporting percentage coverage on the diff
- Enforcing minimum coverage thresholds on new code
- Integrating with CI to fail PRs with insufficient test coverage

**Impact**: Better visibility into new code coverage, faster code reviews, enforced testing standards for changes, reduced untested code in PRs

**ROI**: Very High - minimal setup effort (30-60 min), immediate value in every PR review

## Current State

Coverage is tracked for the entire codebase using pytest-cov:

**pyproject.toml (lines 469-491)**:

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

**Current pytest-cov usage**:

```bash
$ pytest --cov=nhl_scrabble --cov-report=xml --cov-report=html

# Output:
----------- coverage: platform linux, python 3.12.0-final-0 -----------
Name                                    Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------
src/nhl_scrabble/__init__.py               3      0      0      0   100.00%
src/nhl_scrabble/api/nhl_client.py        89     45     26      2    46.36%
src/nhl_scrabble/models/player.py         15      0      2      0   100.00%
src/nhl_scrabble/scoring/scrabble.py      24      0      6      0   100.00%
... (many more files)
---------------------------------------------------------------------------
TOTAL                                   1234    620    312     15    49.93%

Coverage XML written to coverage.xml
Coverage HTML written to htmlcov/index.html
```

**Problem with whole-codebase coverage**:

When reviewing a PR that adds 50 new lines of code:

- Can't easily see coverage for just those 50 lines
- Overall coverage percentage may stay the same or even drop
- No enforcement of coverage standards on new code
- Have to manually inspect coverage reports
- Codecov helps but doesn't fail CI on low diff coverage

**Missing tool**:

- No diff-cover in dependencies
- No diff coverage reporting in CI
- No enforcement of minimum coverage on changed lines
- No easy way to see "Is this PR well-tested?"

## Proposed Solution

Add diff-cover to analyze coverage on changed lines only:

**Step 1: Add diff-cover to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "pytest-xdist>=3.5.0",
    "pytest-randomly>=3.15.0",
    "pytest-sugar>=1.0.0",
    "pytest-clarity>=1.0.1",
    "diff-cover>=8.0.0",  # Add diff coverage reporting
    "beautifulsoup4>=4.12.0",
]
```

**Step 2: Configure diff-cover** (optional, works with defaults):

```toml
# pyproject.toml (optional configuration)
[tool.diff_cover]
# Compare against main branch
compare_branch = "origin/main"

# Minimum coverage percentage required on diff
fail_under = 80.0

# Include only source files
include_paths = ["src/"]

# Exclude patterns
exclude_paths = [
    "tests/",
    "*/__main__.py",
]
```

**Step 3: Add diff-cover tox environment**:

```ini
# tox.ini
[testenv:diff-cover]
description = Check test coverage on changed lines only (diff coverage)
deps =
    pytest>=8.0.0
    pytest-cov>=4.1.0
    diff-cover>=8.0.0
commands_pre =
    diff-cover --version
commands =
    # First generate coverage
    pytest --cov=nhl_scrabble --cov-report=xml
    # Then run diff-cover against main branch
    diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
allowlist_externals =
    git
labels = quality, coverage
```

**Step 4: Add to CI workflow**:

```yaml
# .github/workflows/ci.yml
# Add to tox matrix
strategy:
  matrix:
    tox-env:
      - diff-cover  # Add diff coverage check
      # ... existing environments
```

**Step 5: Usage examples**:

```bash
# Local development - check coverage on your changes
pytest --cov=nhl_scrabble --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main

# Output:
# -------------
# Diff Coverage
# Diff: origin/main...HEAD, staged, and unstaged changes
# -------------
# src/nhl_scrabble/api/nhl_client.py (100%)
# src/nhl_scrabble/processors/team_processor.py (85%)
# -------------
# Total: 42 lines
# Missing: 3 lines
# Coverage: 92.9%
# -------------

# With fail-under enforcement
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
# Exit code 0 if >= 80%, exit code 1 if < 80%

# Via tox
tox -e diff-cover
```

**Step 6: HTML reports** (optional):

```bash
# Generate HTML diff coverage report
diff-cover coverage.xml --compare-branch=origin/main --html-report diff-cover.html

# Open in browser
open diff-cover.html

# Shows:
# - List of changed files
# - Line-by-line coverage highlighting
# - Percentage per file
# - Overall diff coverage percentage
```

**Step 7: Integration with Codecov** (complementary):

diff-cover and Codecov work together:

- Codecov: Tracks historical coverage, generates PR comments
- diff-cover: Enforces minimum coverage on PRs in CI

Both provide value!

## Implementation Steps

1. **Add diff-cover to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.test]`
   - Add `diff-cover>=8.0.0`

1. **Configure diff-cover** (optional):

   - Add `[tool.diff_cover]` section to `pyproject.toml`
   - Set `compare_branch = "origin/main"`
   - Set `fail_under = 80.0` (or desired threshold)

1. **Add tox environment**:

   - Create `[testenv:diff-cover]` in `tox.ini`
   - Configure to run pytest with coverage, then diff-cover

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Test locally**:

   - Make some code changes
   - Run `pytest --cov --cov-report=xml`
   - Run `diff-cover coverage.xml --compare-branch=origin/main`
   - Verify output shows only changed lines

1. **Add to CI**:

   - Add diff-cover to tox matrix in `.github/workflows/ci.yml`
   - Verify it runs on PRs
   - Check that it fails PRs with low diff coverage

1. **Document usage**:

   - Add to CONTRIBUTING.md
   - Explain diff coverage vs total coverage
   - Document how to generate reports locally

## Testing Strategy

**Manual Verification**:

```bash
# Step 1: Make changes to a file
echo "# Test change" >> src/nhl_scrabble/api/nhl_client.py

# Step 2: Run coverage
pytest --cov=nhl_scrabble --cov-report=xml

# Step 3: Check diff coverage
diff-cover coverage.xml --compare-branch=origin/main

# Expected output:
# Diff Coverage
# src/nhl_scrabble/api/nhl_client.py (0%)  # New line not tested
# Total: 1 line
# Missing: 1 line
# Coverage: 0.0%

# Step 4: Add test for the change
# (add test coverage)

# Step 5: Re-run
pytest --cov=nhl_scrabble --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main

# Expected output:
# Diff Coverage
# src/nhl_scrabble/api/nhl_client.py (100%)
# Total: 1 line
# Missing: 0 lines
# Coverage: 100.0%
```

**CI Integration Testing**:

```bash
# Via tox (simulates CI)
tox -e diff-cover

# Should:
# 1. Run pytest with coverage
# 2. Generate coverage.xml
# 3. Run diff-cover against origin/main
# 4. Exit 0 if coverage >= 80%, exit 1 otherwise
```

**HTML Report Testing**:

```bash
# Generate HTML report
diff-cover coverage.xml --compare-branch=origin/main --html-report diff-cover.html

# Open and verify:
# - Shows changed files
# - Highlights uncovered lines in red
# - Shows coverage percentage per file
# - Shows overall diff coverage
```

## Acceptance Criteria

- [ ] diff-cover added to `[project.optional-dependencies.test]`
- [ ] Lock file updated with diff-cover
- [ ] `[tool.diff_cover]` configuration added to `pyproject.toml`
- [ ] `fail_under = 80.0` or appropriate threshold set
- [ ] `[testenv:diff-cover]` added to `tox.ini`
- [ ] `diff-cover` added to CI tox matrix
- [ ] Running `diff-cover coverage.xml` shows coverage on changed lines only
- [ ] CI fails PRs with diff coverage < 80%
- [ ] HTML reports can be generated with `--html-report`
- [ ] Works with existing pytest-cov configuration
- [ ] Compatible with Codecov integration
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] Example workflow documented for developers

## Related Files

- `pyproject.toml` - Add diff-cover dependency and configuration
- `tox.ini` - Add diff-cover tox environment
- `.github/workflows/ci.yml` - Add to tox matrix
- `CONTRIBUTING.md` - Document diff coverage workflow
- `uv.lock` - Updated with diff-cover
- `coverage.xml` - Generated by pytest-cov, consumed by diff-cover

## Dependencies

**Recommended implementation order**:

- Implement after pytest-cov is working (already configured)
- Independent of other testing tasks (001-005)
- Can be implemented standalone

**No blocking dependencies** - Can be implemented independently

**Works with**:

- pytest-cov (required - generates coverage.xml)
- Codecov (complementary - both provide value)
- CI workflows (integrates seamlessly)

## Additional Notes

**Why diff-cover?**

- **Focus on what matters**: Coverage on NEW code, not existing code
- **Enforce standards**: Require X% coverage on all PRs
- **Faster reviews**: Immediately see if PR is well-tested
- **Prevent regression**: Stop untested code from entering codebase
- **Complement Codecov**: Works alongside, not instead of
- **Local feedback**: Developers can check before pushing

**How diff-cover Works**:

```
Standard pytest-cov workflow:
  1. Run pytest with --cov
  2. Generate coverage.xml (whole codebase)
  3. Show coverage for ALL files
  4. Overall percentage: 49.93%

With diff-cover enhancement:
  1. Run pytest with --cov (same as before)
  2. Generate coverage.xml (same as before)
  3. diff-cover compares coverage.xml against git diff  ← New
  4. Filter to only changed lines                        ← New
  5. Show coverage for CHANGED files only                ← New
  6. Diff coverage percentage: 92.9%                     ← New
```

**Diff Coverage vs Total Coverage**:

| Metric             | Total Coverage   | Diff Coverage      |
| ------------------ | ---------------- | ------------------ |
| **Scope**          | Entire codebase  | Changed lines only |
| **Typical value**  | 49.93% (current) | 80-100% (target)   |
| **Purpose**        | Overall health   | PR quality         |
| **Changes slowly** | Yes              | No (per PR)        |
| **Enforced in CI** | ⚠️ Optional      | ✅ Yes             |
| **Shown in PR**    | Via Codecov      | Via diff-cover     |

Both are valuable for different reasons!

**Example Scenario**:

```
Project state:
- Total coverage: 50% (620 lines uncovered out of 1234)
- This is OK for existing code

New PR adds 50 lines:
- 45 lines covered by tests
- 5 lines not covered

Total coverage: 50.4% (unchanged, maybe even drops)
Diff coverage: 90% (45/50 lines covered)

Without diff-cover:
  "Coverage is still 50%, looks fine ✅"
  But 5 new lines are untested! ❌

With diff-cover:
  "Diff coverage is 90%, passing ✅"
  Immediately visible, enforced in CI
```

**Configuration Options**:

```toml
[tool.diff_cover]
# Compare branch (default: origin/main)
compare_branch = "origin/main"

# Minimum coverage percentage (default: no minimum)
fail_under = 80.0

# Source paths to include (default: all)
include_paths = ["src/"]

# Patterns to exclude (default: none)
exclude_paths = [
    "tests/",
    "*/__main__.py",
]

# Ignore whitespace in diff (default: false)
ignore_whitespace = false
```

**CLI Options**:

```bash
# Basic usage
diff-cover coverage.xml

# Compare against specific branch
diff-cover coverage.xml --compare-branch=origin/develop

# Fail if coverage below threshold
diff-cover coverage.xml --fail-under=80

# Generate HTML report
diff-cover coverage.xml --html-report=diff-cover.html

# Markdown report (for PR comments)
diff-cover coverage.xml --markdown-report=diff-cover.md

# JSON output (for parsing)
diff-cover coverage.xml --json-report=diff-cover.json

# Quiet mode (only show summary)
diff-cover coverage.xml --quiet

# Include only specific paths
diff-cover coverage.xml --include=src/nhl_scrabble/

# Exclude paths
diff-cover coverage.xml --exclude=tests/
```

**Integration with Code Review**:

```yaml
# .github/workflows/ci.yml
- name: Run diff coverage
  run: tox -e diff-cover

- name: Comment on PR with diff coverage
  if: github.event_name == 'pull_request'
  run: |
    diff-cover coverage.xml --markdown-report=diff-cover.md
    gh pr comment ${{ github.event.pull_request.number }} --body-file=diff-cover.md
```

**Threshold Guidelines**:

| Threshold | Meaning                    | Recommendation     |
| --------- | -------------------------- | ------------------ |
| **100%**  | All new code tested        | Ideal but strict   |
| **90%**   | Nearly all new code tested | Excellent          |
| **80%**   | Most new code tested       | Good baseline      |
| **70%**   | Some new code tested       | Minimum acceptable |
| **\<70%** | Insufficient testing       | Should not merge   |

Recommended: Start with 70%, increase to 80% over time.

**Example Output**:

```bash
$ diff-cover coverage.xml --compare-branch=origin/main --fail-under=80

-------------
Diff Coverage
Diff: origin/main...HEAD, staged, and unstaged changes
-------------
src/nhl_scrabble/api/nhl_client.py (100.0%)
src/nhl_scrabble/processors/team_processor.py (85.7%)
src/nhl_scrabble/models/player.py (100.0%)
tests/integration/test_new_feature.py (100.0%)
-------------
Total: 42 lines
Missing: 3 lines
Coverage: 92.9%
-------------

✅ Diff coverage: 92.9% >= 80.0% (threshold)
```

**HTML Report Features**:

- File-by-file breakdown
- Line numbers highlighted
- Red for uncovered, green for covered
- Clickable file navigation
- Overall summary at top
- Can be saved as artifact in CI

**Compatibility Matrix**:

✅ **Works with**:

- pytest-cov (required)
- coverage.py XML output
- Git (required for diff)
- Codecov (complementary)
- GitHub Actions, GitLab CI, etc.
- All CI systems

⚠️ **Limitations**:

- Requires git (not standalone)
- Requires coverage.xml (must run pytest-cov first)
- Only shows diff, not total coverage (by design)

**Common Questions**:

**Q: Does this replace pytest-cov?**
A: No, it complements pytest-cov. You still need pytest-cov to generate coverage.xml.

**Q: Does this replace Codecov?**
A: No, it complements Codecov. Both provide value in different ways.

**Q: What if my diff coverage is low but total coverage is high?**
A: That's OK! Diff coverage focuses on NEW code. Existing uncovered code is tracked separately.

**Q: Can I use this locally?**
A: Yes! Run `diff-cover coverage.xml --compare-branch=origin/main` after running tests.

**Q: Will this block all my PRs?**
A: Only if diff coverage < threshold (e.g., 80%). Write tests for new code and it passes.

**Q: What about generated files?**
A: Exclude them with `exclude_paths` in configuration.

**Best Practices**:

```bash
# ✅ Good: Check diff coverage before pushing
pytest --cov --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
# Fix any gaps, then push

# ✅ Good: Use HTML reports for detailed review
diff-cover coverage.xml --html-report=diff-cover.html
open diff-cover.html
# See exactly which lines need tests

# ✅ Good: Enforce in CI
# Set fail_under in pyproject.toml
# PRs with low coverage fail CI

# ❌ Bad: Ignoring diff coverage failures
# If CI fails, add tests - don't lower threshold

# ❌ Bad: Setting threshold too low (<70%)
# Defeats the purpose of enforcing coverage

# ❌ Bad: Only checking total coverage
# Misses untested new code
```

## Implementation Notes

*To be filled during implementation:*

- Threshold value chosen (70%, 80%, 90%?)
- Average diff coverage observed in PRs
- Number of PRs that failed diff coverage initially
- Developer feedback on enforcement
- CI integration details
- Any configuration adjustments needed
