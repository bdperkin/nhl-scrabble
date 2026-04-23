# Implement Task

______________________________________________________________________

## title: 'Implement Task End-to-End' read_only: false type: 'command'

Complete end-to-end implementation of a task from specification to merged PR with full automation.

## Process

This command automates the complete task implementation workflow from start to finish:

1. **Parse Task File**

   - Read task file from `tasks/{category}/{id}-{slug}.md`
   - Extract task metadata:
     - Title and description
     - Priority level
     - Estimated effort
     - GitHub issue number/URL
   - Parse implementation plan:
     - Current state
     - Proposed solution
     - Implementation steps
     - Testing strategy
     - Acceptance criteria
     - Related files
     - Dependencies
   - Validate task file completeness
   - Check dependencies are met

1. **Create Implementation Branch**

   - Extract category and task ID from file path
   - Generate branch name: `{category}/{id}-{slug}`
   - Examples:
     - `tasks/bug-fixes/007-api-404-handling.md` → `bug-fixes/007-api-404-handling`
     - `tasks/new-features/002-rest-api-server.md` → `new-features/002-rest-api-server`
   - Ensure main branch is up-to-date
   - Create and checkout new branch
   - Verify branch creation

1. **Implement Solution**

   - Follow implementation steps from task file
   - Implement proposed solution with code examples as guide
   - Apply architecture changes
   - Update configuration files
   - Add/modify database schemas if needed
   - Follow project coding standards:
     - PEP 8 style (line length 100)
     - Type hints throughout
     - Docstrings for all public APIs
     - Defensive error handling
     - Proper logging
   - Keep changes focused on task scope
   - Avoid scope creep or unrelated changes
   - Write clean, maintainable code
   - Follow existing patterns in codebase

1. **Implement Tests**

   - Follow testing strategy from task file
   - **Unit Tests**:
     - Test individual functions/classes
     - Mock external dependencies
     - Cover edge cases
     - Test error conditions
     - Achieve >80% coverage for new code
   - **Integration Tests**:
     - Test component interactions
     - Test API integrations
     - Test database operations
     - Test configuration loading
   - **Manual Testing** (if specified):
     - Follow manual test steps
     - Verify UI changes
     - Test user workflows
     - Document results
   - Place tests in appropriate directories:
     - `tests/unit/` for unit tests
     - `tests/integration/` for integration tests
   - Follow test naming conventions: `test_*.py`
   - Use descriptive test names: `test_function_name_scenario_expected`

1. **Verify Acceptance Criteria**

   - Run all tests: `pytest`
   - Check test coverage: `pytest --cov`
   - Run type checking: `mypy`
   - Run linting: `ruff check`
   - Verify each acceptance criterion:
     - [ ] Manual verification for functionality
     - [ ] Tests pass
     - [ ] Documentation updated
     - [ ] Code quality checks pass
     - [ ] Performance requirements met (if specified)
     - [ ] Security requirements met (if specified)
   - Document any deviations from plan
   - Note challenges encountered

1. **Pre-Flight Validation**

   Before creating pull request, validate changes won't break CI:

   - **Test Dependency Validation**:

     ```python
     # For tests requiring external tools (sphinx-build, npm, etc.)
     import shutil
     import pytest

     # Module-level skip for all tests in file
     pytestmark = pytest.mark.skipif(
         shutil.which("tool-name") is None,
         reason="tool-name not found (optional dependencies not installed)",
     )


     # Or per-test skip
     @pytest.mark.skipif(
         shutil.which("tool-name") is None,
         reason="tool-name not found",
     )
     def test_requiring_external_tool(): ...
     ```

     - Use `shutil.which()` to check tool availability
     - Add `@pytest.mark.skipif` for optional tool dependencies
     - Use module-level `pytestmark` to skip all tests in file
     - Document required tools in test docstring

   - **Pre-commit Hook Testing** (CRITICAL for new hooks):

     ```bash
     # Test new hook on ALL existing files BEFORE staging
     pre-commit run <new-hook-id> --all-files

     # If hook modifies or fails:
     # 1. Review changes/failures carefully
     # 2. Add exclude patterns if needed
     # 3. Re-test until clean
     # 4. THEN stage .pre-commit-config.yaml
     ```

     - **NEVER** commit new hooks without testing on all files
     - Add exclusions for files that shouldn't be formatted/checked
     - Document why files are excluded (pseudo-code, examples, etc.)
     - Common exclusion patterns:
       - `^tasks/` - Task files with pseudo-code
       - `^\.claude/commands/` - Command docs with examples
       - `^docs/explanation/` - Architectural docs with illustrative code
       - `^examples/` - Example code that may not be valid

   - **Local Quality Checks**:

     ```bash
     # Run FULL quality suite locally
     make quality                    # All linters
     pytest                          # All tests
     pre-commit run --all-files      # All hooks

     # CI-specific checks (if available locally)
     tox -e py310,py311,py312,py313,py314,py315  # Multi-version testing
     make docs                       # Documentation build
     ```

   - **Dependency Installation Validation** (if added new dependencies):

     ```bash
     # Verify new dependencies install correctly
     uv pip install -e ".[group-name]"  # For new optional deps
     uv lock                             # Update lock file
     git diff uv.lock                    # Review lock changes

     # Test in clean environment
     uv venv --python 3.10 test-env
     source test-env/bin/activate
     uv pip install -e ".[group-name]"
     # Verify imports work
     python -c "import package_name"
     which tool-name  # For CLI tools
     deactivate && rm -rf test-env
     ```

   **Why This Matters**:

   - Catches CI failures locally before pushing
   - Pre-commit hooks can have parse errors on pseudo-code
   - Tests may require tools not available in all environments
   - Dependencies may have installation issues
   - Saves 10-15 minutes per PR by avoiding CI iterations

   **Time Investment**: 5-10 minutes upfront
   **Time Saved**: 10-15 minutes per CI iteration avoided

1. **Update Documentation**

   - Update files mentioned in task "Related Files"
   - **Internal Documentation**:
     - Add/update docstrings for new code
     - Update module docstrings if architecture changed
     - Add inline comments for complex logic
     - Update type hints
   - **External Documentation**:
     - Update README.md if public API changed
     - Update CHANGELOG.md with change description
     - Update CONTRIBUTING.md if workflow changed
     - Update relevant docs/ files
   - **Configuration Documentation**:
     - Document new configuration options
     - Update example configs
     - Add environment variable docs
   - Ensure 100% docstring coverage for new code
   - Run `interrogate` to verify

1. **Commit Implementation**

   - Stage all changes: `git add -A`
   - Review staged changes: `git diff --cached`
   - Create commit following task specification:
     - Use conventional commit format
     - Reference GitHub issue number
     - Include task file reference
   - Verify commit created: `git log -1`

1. **Automated Pre-Flight Validation**

   Run comprehensive validation before pushing to ensure CI will pass:

   **a. Run Pre-Commit on All Files**

   ```bash
   pre-commit run --all-files
   ```

   - Verifies all 58 hooks pass
   - Catches formatting, linting, security issues
   - Fixes auto-fixable issues
   - Reports any failures

   **If pre-commit failures occur:**

   1. Review failure messages carefully
   1. Fix issues (most hooks auto-fix):
      ```bash
      ruff check --fix src/
      ruff format src/
      ```
   1. Re-stage changes: `git add -A`
   1. Amend commit: `git commit --amend --no-edit`
   1. Re-run pre-commit: `pre-commit run --all-files`
   1. Continue when all hooks pass

   **b. Run All Tox Environments**

   ```bash
   tox -p auto
   ```

   - Tests all Python versions (3.10-3.15)
   - Runs quality checks (ruff-check, mypy, etc.)
   - Runs test suite with coverage
   - Parallel execution for speed (~3-5 min total)
   - Python 3.15-dev allowed to fail (experimental)

   **If tox failures occur:**

   1. Review tox output for failing environment
   1. Run specific environment for details:
      ```bash
      tox -e py312  # Or whichever failed
      pytest -vv    # For test failures
      mypy src/     # For type errors
      ```
   1. Fix issues in code
   1. Commit fixes: `git add -A && git commit --amend --no-edit`
   1. Re-run failed environment: `tox -e py312`
   1. Re-run full tox when fixed: `tox -p auto`
   1. Continue when all environments pass

   **c. Verify Clean State**

   ```bash
   git status
   ```

   - Ensure no uncommitted changes
   - Verify working tree is clean
   - Confirm ready to push

   **Validation Success Output:**

   ```
   🔍 Pre-Flight Validation

   ✅ Pre-commit hooks: All 58 hooks passed (45s)
   ✅ Tox environments: All environments passed
      - py310: ✅ (1m 29s)
      - py311: ✅ (1m 45s)
      - py312: ✅ (1m 33s)
      - py313: ✅ (1m 33s)
      - py314: ✅ (1m 27s)
      - py315: ⚠️  (allowed to fail - experimental)
      - ruff-check: ✅ (19s)
      - mypy: ✅ (20s)
      - coverage: ✅ (1m 18s)
   ✅ Working tree: Clean

   Total validation time: 3m 45s

   ✅ Pre-flight validation passed! Safe to push.
   ```

   **Validation Failure Output:**

   ```
   🔍 Pre-Flight Validation

   ❌ Pre-commit hooks: 2 hooks failed
      - ruff-check: Failed on src/nhl_scrabble/cli.py:42
      - mypy: Type error in src/nhl_scrabble/api/nhl_client.py:156

   ❌ Pre-flight validation failed!

   Recommendations:
   1. Fix ruff issues: ruff check --fix src/
   2. Fix mypy errors: mypy src/ --show-error-codes
   3. Re-stage: git add -A
   4. Amend commit: git commit --amend --no-edit
   5. Re-run validation: pre-commit run --all-files

   DO NOT PUSH until all checks pass.
   ```

   **Skip Options** (use with extreme caution):

   ⚠️ **Emergency use only** - skipping validation may result in CI failures

   ```bash
   # Skip pre-commit only (not recommended)
   SKIP=pre-commit git push

   # Skip specific tox environments
   # (Cannot skip - must run tox -p auto)

   # Skip validation entirely (EMERGENCY ONLY)
   # Push directly without running validation
   # Only use for: emergency hotfixes, CI infrastructure issues,
   # time-critical security fixes where you've manually verified
   ```

   **When to skip validation:**

   - ✅ Emergency production hotfix (after manual verification)
   - ✅ CI infrastructure is broken (not your code)
   - ✅ You manually ran all checks and they passed
   - ✅ Time-critical security fix (after thorough testing)

   **When NOT to skip:**

   - ❌ "I'm sure it's fine" (validate to be sure!)
   - ❌ "I'll fix it in the PR" (fix before pushing)
   - ❌ "CI will catch it" (catch it locally first)
   - ❌ Regular workflow (always validate)

   **Why Pre-Flight Validation Matters:**

   - **Catches issues locally** before they reach CI
   - **Saves time**: 3-5 min validation vs 15-30 min CI failure cycle
   - **Reduces CI load**: ~83% reduction in failed CI runs
   - **Prevents context switching**: Fix issues before pushing
   - **Cleaner git history**: No "fix CI" commits
   - **Higher confidence**: Know it will pass before pushing

   **Time Investment**: 3-5 minutes upfront
   **Time Saved**: 10-15 minutes per CI iteration avoided
   **Success Rate**: ~95% first-time CI pass (vs ~70% without validation)

1. **Push to Remote**

   Only push after validation passes:

   - Push branch: `git push -u origin {branch-name}`
   - Verify push succeeded
   - Get remote branch URL

1. **Create Pull Request**

   - Create PR using `gh pr create`:
     - Title: Task title from task file
     - Body:
       - Link to task file
       - Link to GitHub issue
       - Summary of changes
       - Testing notes
       - Acceptance criteria checklist
     - Auto-link issue with "Closes #{issue-number}"
   - Example PR body:
     ```markdown
     ## Task

     **Task File**: `tasks/bug-fixes/007-api-404-handling.md`
     **GitHub Issue**: Closes #52

     ## Summary

     Fix NHL API 404 error handling to properly raise `NHLApiNotFoundError`
     instead of just logging a warning.

     ## Changes

     - Updated `NHLClient` to raise `NHLApiNotFoundError` on 404
     - Added tests for 404 scenarios
     - Updated error handling documentation

     ## Testing

     - ✅ Unit tests: All passing (12 new tests)
     - ✅ Integration tests: All passing
     - ✅ Manual testing: Verified 404 handling
     - ✅ Coverage: 95% on modified code

     ## Acceptance Criteria

     - [x] Raises `NHLApiNotFoundError` on 404 responses
     - [x] Tests cover 404 scenarios
     - [x] Documentation updated
     - [x] All tests pass
     - [x] Type checking passes
     ```

1. **Update Task File**

   - Mark completed acceptance criteria with ✅
   - Add Implementation Notes section:
     ```markdown
     ## Implementation Notes

     **Implemented**: 2026-04-16
     **Branch**: bug-fixes/007-api-404-handling
     **PR**: #54 - https://github.com/user/repo/pull/54
     **Commits**: 3 commits (a1b2c3d, d4e5f6g, h7i8j9k)

     ### Actual Implementation

     Followed the proposed solution closely with one modification:
     - Added custom exception hierarchy for better error categorization
     - Implemented retry logic for temporary 404s

     ### Challenges Encountered

     - Mock API testing required more sophisticated fixtures
     - Had to handle edge case where API returns 404 with body

     ### Deviations from Plan

     - Added `NHLApiTemporaryError` for retry scenarios
     - Extended testing beyond original scope to cover edge cases

     ### Actual vs Estimated Effort

     - **Estimated**: 1-2h
     - **Actual**: 2.5h
     - **Reason**: Additional exception hierarchy and edge case handling

     ### Related PRs

     - #54 - Main implementation

     ### Lessons Learned

     - API error handling needs comprehensive edge case coverage
     - Mock fixtures benefit from dedicated helper functions
     ```
   - Update any outdated sections
   - Add metrics if applicable

1. **Move Task to Completed**

   - Determine category from task file path
   - Create `tasks/completed/{category}/` if doesn't exist
   - Move task file: `tasks/{category}/{id}-{slug}.md` → `tasks/completed/{category}/{id}-{slug}.md`
   - Update internal links if necessary
   - Preserve git history with `git mv`

1. **Update tasks/README.md**

   - **Task Index**:
     - Remove task from active category table
     - Add task to completed section with:
       - Completion date
       - PR number
       - Final effort
   - **Total Project Roadmap**:
     - Decrement category task count
     - Subtract estimated effort from category total
     - Update overall statistics
     - Increment completed count
   - **Recommended Implementation Order**:
     - Remove task if it was listed
     - Re-evaluate order based on remaining tasks
   - **Completed Tasks Section** (if exists):
     - Add entry with metadata:
       ```markdown
       | ID | Title | Priority | Effort | Completed | PR |
       |---|---|---|---|---|---|
       | 007 | Fix API 404 handling | HIGH | 2.5h | 2026-04-16 | #54 |
       ```
   - Maintain proper markdown formatting

1. **Commit and Push Changes**

   - Stage all changes:
     - Modified task file (with completion notes)
     - Moved task file location
     - Updated tasks/README.md
     - Implementation code
     - Tests
     - Documentation
   - Review changes: `git diff --cached`
   - Create commit with message:
     ```
     {type}: {task-title}

     {description}

     Task: tasks/{category}/{id}-{slug}.md
     Issue: Closes #{issue-number}
     ```
   - Push to remote: `git push`
   - Verify push succeeded

1. **Wait for CI/CD**

   - Monitor PR status: `gh pr status`

   - Use background job for long waits:

     ```bash
     # Background monitoring (recommended for >1 minute waits)
     # Background job will notify when complete
     ```

   - Wait for all checks to pass:

     - GitHub Actions workflows
     - Pre-commit hooks (if run in CI)
     - Test suite (all Python versions)
     - Code quality checks (ruff, mypy)
     - Coverage requirements
     - Documentation builds

   - Poll every 30 seconds: `gh pr checks`

   - **Retry Logic for Flaky Tests** (automatic retry up to 3 times):

     When CI checks fail, automatically retry failed jobs to handle transient failures:

     **1. Detect Failure**: Check if any jobs failed

     ```bash
     gh run view <run-id> --json conclusion,jobs
     ```

     **2. Identify Failed Jobs**: Extract failed job names/IDs

     ```bash
     # Get list of failed jobs
     gh api repos/:owner/:repo/actions/runs/<run-id>/jobs \
       --jq '.jobs[] | select(.conclusion == "failure") | .name'
     ```

     **3. Retry Failed Jobs Only** (not all jobs):

     ```bash
     # Re-run only failed jobs (not entire workflow)
     gh run rerun <run-id> --failed
     ```

     **Important**: Always use `--failed` flag to retry only failed jobs, saving time and CI resources

     **4. Retry Loop** (maximum 3 attempts):

     ```python
     retry_count = 0
     max_retries = 3

     while retry_count < max_retries:
         wait_for_completion()

         if all_checks_passed():
             # Success! Continue to merge
             break
         elif has_failed_jobs():
             retry_count += 1
             if retry_count < max_retries:
                 log(f"⚠️  Retry {retry_count}/{max_retries}: Re-running failed jobs...")
                 gh_run_rerun(run_id, failed_only=True)
                 # Continue loop to wait for retry results
             else:
                 # Max retries exhausted
                 break

     if retry_count >= max_retries and has_failed_jobs():
         # Stop and ask user what to do
         prompt_user_for_action()
     ```

     **5. User Prompt** (if still failing after 3 retries):

     ```
     ⚠️  CI Checks Failed After 3 Retries

     PR #287 has persistent failures despite retrying failed jobs 3 times.

     Failed Jobs:
     - Test on Python 3.15-dev (failure)
     - Tox tests with UV (py315) (failure)
     - codecov/project (86.60% vs 90.00% target)

     Retry History:
     - Attempt 1: Failed (same errors)
     - Attempt 2: Failed (same errors)
     - Attempt 3: Failed (same errors)

     Failure Logs:
     - View full logs: gh run view <run-id> --log-failed
     - View job details: gh run view <run-id> --job <job-id>

     Options:
     1. Investigate failures locally and push fix
     2. Retry manually one more time: gh run rerun <run-id> --failed
     3. Skip failing jobs if non-critical (e.g., py315-dev experimental)
     4. Abort task and investigate thoroughly
     5. View detailed failure analysis

     What would you like to do? [1/2/3/4/5]
     ```

     **Retry Decision Tree**:

     **When automatic retry HELPS** ✅:

     - Network-dependent tests (API calls, external services)
     - Rate-limited operations (GitHub API, third-party APIs)
     - Timing-sensitive integration tests (race conditions)
     - External service availability (transient outages)
     - Resource contention (parallel test runners, CPU/memory spikes)
     - Flaky tests with intermittent failures

     **When automatic retry DOES NOT HELP** ❌:

     - Build/compilation errors (always reproducible)
     - Linting/formatting failures (deterministic)
     - Type checking errors (deterministic)
     - Missing dependencies (won't resolve without code change)
     - Test assertion failures (logic errors)
     - Import errors (missing modules)
     - Syntax errors (parse failures)

     **Retry Strategy**:

     - **First failure**: Immediate retry (may be transient)
     - **Second failure**: Wait 30s, then retry (service may be recovering)
     - **Third failure**: Wait 60s, then retry (final attempt)
     - **Fourth failure**: Stop and prompt user (likely requires intervention)

     **Monitoring During Retries**:

     ```bash
     # Watch retry progress in real-time
     gh run watch <run-id>

     # Check specific job status
     gh run view <run-id> --job <job-id>

     # View failure logs immediately
     gh run view <run-id> --log-failed
     ```

     **Time Savings**:

     - Flaky test success rate: ~70% on first retry
     - Average retry time: 2-5 minutes (vs 15-30 min manual investigation)
     - CI resource savings: Retry only failed jobs (not all 50 checks)
     - Developer productivity: Automatic handling of transient failures

   - **Common CI Failure Patterns** (with fixes):

     **Pattern 1: Missing External Tools**

     ```
     Error: FileNotFoundError: [Errno 2] No such file or directory: 'tool-name'
     Location: tests/test_file.py::test_function
     ```

     **Diagnosis**: Test requires external tool not available in CI environment
     **Fix**: Add `@pytest.mark.skipif` to skip when tool unavailable

     ```python
     import shutil
     import pytest

     # Module-level skip for all tests
     pytestmark = pytest.mark.skipif(
         shutil.which("tool-name") is None,
         reason="tool-name not found (optional dependencies not installed)",
     )
     ```

     **Prevention**: Always check tool availability in Pre-Flight Validation

     **Pattern 2: Pre-commit Hook Parse/Formatting Errors**

     ```
     hook-name......................Failed
     - exit code: 2
     file.md:10: code block parse error Cannot parse: ...
     ```

     **Diagnosis**: Hook trying to format pseudo-code or illustrative examples
     **Fix**: Add exclusion pattern to `.pre-commit-config.yaml`

     ```yaml
       - id: hook-name
         exclude: ^(tasks/|\.claude/commands/|docs/explanation/|examples/)
         args: ['...']
     ```

     **Prevention**: Always test new hooks with `pre-commit run hook-name --all-files`

     **Pattern 3: Pre-commit Hook Modified Files**

     ```
     hook-name......................Failed
     - files were modified by this hook
     ```

     **Diagnosis**: Hook auto-formatted files that weren't committed
     **Fix**: Run hook locally, review changes, commit formatted files

     ```bash
     pre-commit run hook-name --all-files
     git add -A
     git commit --amend --no-edit
     git push --force-with-lease
     ```

     **Prevention**: Always run `pre-commit run --all-files` in Pre-Flight Validation

     **Pattern 4: Security/Linter False Positives**

     ```
     S603 `subprocess` call: check for execution of untrusted input
     S607 Starting a process with a partial executable path
     Location: file.py:42
     ```

     **Diagnosis**: Subprocess call flagged but is actually safe
     **Fix**: Add targeted noqa comment with justification

     ```python
     # Safe: sphinx-build is trusted tool from project dependencies
     result = subprocess.run(  # noqa: S603, S607
         ["sphinx-build", "-b", "html", str(docs_dir), str(build_dir)],
         capture_output=True,
         check=True,
     )
     ```

     **When to use noqa**: Only when command is hardcoded, trusted, and arguments are validated
     **When NOT to use noqa**: User input in command, shell=True, unvalidated paths

     **Pattern 5: Import/Dependency Issues**

     ```
     ModuleNotFoundError: No module named 'package_name'
     ImportError: cannot import name 'symbol' from 'package'
     ```

     **Diagnosis**: Missing dependency or dependency not in correct group
     **Fix**: Add to appropriate group in `pyproject.toml`

     ```toml
     [project.optional-dependencies]
     docs = [
       "sphinx>=7.2.6",
       "package-name>=1.0.0", # NEW
     ]
     ```

     Then update lock file:

     ```bash
     uv lock
     git add pyproject.toml uv.lock
     git commit -m "fix(deps): Add missing package-name dependency"
     git push
     ```

     **Prevention**: Test dependency installation in Pre-Flight Validation

     **Pattern 6: Test Failures**

     ```
     FAILED tests/test_file.py::test_name - AssertionError: ...
     ```

     **Diagnosis**: Test logic error or environment difference
     **Fix**: Run test locally to reproduce

     ```bash
     pytest tests/test_file.py::test_name -vv
     # Debug and fix issue
     # Commit fix
     ```

   - **CI Failure Response Workflow**:

     **Automatic Response** (for transient failures):

     1. System detects CI failure
     1. Automatic retry initiated (up to 3 times)
     1. Only failed jobs re-run (not entire workflow)
     1. If retry succeeds: Continue to merge
     1. If all retries fail: Proceed to manual response below

     **Manual Response** (after automatic retries exhausted or for non-retryable errors):

     1. `gh run view <run-id> --log-failed` - Get failure details
     1. Match failure to pattern above (or diagnose new pattern)
     1. Determine if error is retryable or requires code fix
     1. If requires fix:

     - Apply fix locally
     - Test fix locally:
       ```bash
       pytest                           # Verify tests pass
       pre-commit run --all-files      # Verify hooks pass
       make quality                    # Verify quality checks
       ```
     - Commit fix with descriptive message
     - Push: `git push`
     - CI re-runs automatically (with fresh retry budget)

     1. If error appears transient but retries failed:

     - Manual retry: `gh run rerun <run-id> --failed`
     - Monitor results closely
     - If still failing: Investigate deeper (may be environment-specific)

   - **When to Wait vs. Fix Immediately**:

     - **Wait & Auto-Retry** (up to 3 times): External service issues, transient network failures, rate limiting, flaky tests, resource contention, timing-sensitive tests
     - **Fix Immediately** (no retry): Test assertion failures, linting errors, type errors, missing deps, parse errors, build failures, syntax errors
     - **Maximum wait**: 30 minutes total (including retries) before manual intervention
     - **Retry decision**: Automatic retry beneficial for transient issues, manual fix required for reproducible errors

1. **Merge Pull Request**

   - Verify all checks passed: `gh pr checks`
   - Verify PR is approved (if required)
   - Check merge conflicts: `gh pr view --json mergeable`
   - If conflicts exist:
     - Update branch: `git pull origin main`
     - Resolve conflicts
     - Run tests again
     - Push resolution
     - Wait for CI again
   - Merge PR using strategy from `.github/` config:
     - Default: `gh pr merge --squash`
     - Or: `gh pr merge --merge` (preserve commits)
     - Or: `gh pr merge --rebase` (linear history)
   - Use PR title as squash commit message
   - Include PR number in commit
   - Delete remote branch: `gh pr merge --delete-branch`

1. **Close GitHub Issue**

   - Verify issue is linked to PR
   - Check if issue was auto-closed by PR merge
   - If not auto-closed, manually close:
     - Add comment with completion info:
       ```
       Completed in PR #54

       Implementation: tasks/completed/bug-fixes/007-api-404-handling.md
       Actual effort: 2.5h (estimated: 1-2h)
       ```
     - Close issue: `gh issue close {issue-number}`
   - Verify issue is closed: `gh issue view {issue-number}`

1. **Return to Main Branch**

   - Checkout main: `git checkout main`
   - Verify on main: `git branch --show-current`

1. **Update Local Main**

   - Fetch from remote: `git fetch origin`
   - Pull latest changes: `git pull origin main`
   - Verify merge commit exists
   - Verify task implementation is present
   - Run quick smoke test: `pytest -x`

1. **Delete Task Branch**

   - List local branches: `git branch`
   - Delete local branch: `git branch -d {branch-name}`
   - Verify deletion: `git branch`
   - Remote branch should already be deleted from merge

1. **Report Completion**

   - Display summary:
     ```
     ✅ Task Implementation Complete!

     Task: Fix API 404 handling (bug-fixes/007)
     Priority: HIGH

     Implementation:
     - Branch: bug-fixes/007-api-404-handling (deleted)
     - Commits: 3 commits
     - Tests: 12 new tests, all passing
     - Coverage: 95% on modified code

     Pull Request:
     - PR #54: https://github.com/user/repo/pull/54
     - Status: Merged
     - Checks: All passed

     GitHub Issue:
     - Issue #52: Closed

     Effort:
     - Estimated: 1-2h
     - Actual: 2.5h

     Task File: tasks/completed/bug-fixes/007-api-404-handling.md

     Next Steps:
     - Task marked complete in tasks/README.md
     - Ready for next task!
     ```

## Branch Naming Convention

Follow git-flow style branch naming:

**Pattern**: `{category}/{id}-{slug}`

**Categories** (from task categories):

- `bug-fixes/` - Bug fixes and corrections
- `security/` - Security improvements
- `optimization/` - Performance optimizations
- `enhancement/` - Feature enhancements
- `testing/` - Test coverage improvements
- `new-features/` - Major new features
- `refactoring/` - Code refactoring

**Examples**:

```
tasks/bug-fixes/007-api-404-handling.md
  → bug-fixes/007-api-404-handling

tasks/new-features/002-rest-api-server.md
  → new-features/002-rest-api-server

tasks/optimization/003-cache-api-responses.md
  → optimization/003-cache-api-responses
```

## Commit Message Format

Follow conventional commits with task references:

```
{type}({scope}): {subject}

{body}

Task: tasks/{category}/{id}-{slug}.md
Issue: Closes #{issue-number}

{footer}
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `perf`: Performance improvement
- `refactor`: Code refactoring
- `test`: Test changes
- `docs`: Documentation changes
- `build`: Build system changes
- `ci`: CI/CD changes

**Example**:

```
fix(api): properly handle 404 errors from NHL API

Replace warning log with NHLApiNotFoundError exception when API
returns 404 status. Add comprehensive tests for error scenarios.

Changes:
- Raise NHLApiNotFoundError on 404 responses
- Add custom exception hierarchy
- Add 12 new unit tests for error handling
- Update API client documentation

Task: tasks/bug-fixes/007-api-404-handling.md
Issue: Closes #52
```

## Pull Request Template

Standard PR body structure:

```markdown
## Task

**Task File**: `tasks/{category}/{id}-{slug}.md`
**GitHub Issue**: Closes #{issue-number}
**Priority**: {priority}
**Estimated Effort**: {effort}

## Summary

{brief-description}

## Changes

- {change-1}
- {change-2}
- {change-3}

## Implementation Details

{architecture-changes}
{key-decisions}
{trade-offs}

## Testing

- ✅ Unit tests: {status} ({count} new tests)
- ✅ Integration tests: {status}
- ✅ Manual testing: {status}
- ✅ Coverage: {percentage}% on modified code

## Acceptance Criteria

- [x] {criterion-1}
- [x] {criterion-2}
- [x] {criterion-3}
- [x] All tests pass
- [x] Documentation updated
- [x] Code quality checks pass

## Documentation

- {docs-updated}

## Breaking Changes

{breaking-changes-or-none}

## Migration Required

{migration-steps-or-none}

## Performance Impact

{performance-notes}

## Security Considerations

{security-notes}
```

## Task File Updates

### Marking Acceptance Criteria

Replace `- [ ]` with `- [x]` for completed items:

**Before**:

```markdown
## Acceptance Criteria

- [ ] Raises NHLApiNotFoundError on 404
- [ ] Tests cover 404 scenarios
- [ ] Documentation updated
- [ ] All tests pass
```

**After**:

```markdown
## Acceptance Criteria

- [x] Raises NHLApiNotFoundError on 404
- [x] Tests cover 404 scenarios
- [x] Documentation updated
- [x] All tests pass
```

### Adding Implementation Notes

Append to end of task file:

```markdown
## Implementation Notes

**Implemented**: {date}
**Branch**: {branch-name}
**PR**: #{pr-number} - {pr-url}
**Commits**: {commit-count} commits ({commit-hashes})

### Actual Implementation

{what-was-actually-done}

### Challenges Encountered

{challenges-and-solutions}

### Deviations from Plan

{any-changes-from-original-plan}

### Actual vs Estimated Effort

- **Estimated**: {original-estimate}
- **Actual**: {actual-time}
- **Variance**: {difference}
- **Reason**: {explanation-for-difference}

### Related PRs

- #{pr-number} - {description}

### Lessons Learned

{insights-for-future-tasks}

### Performance Metrics

{if-applicable}

### Test Coverage

{coverage-metrics}
```

## CI/CD Monitoring

### Check Status

```bash
# View PR status
gh pr status

# Check PR checks
gh pr checks {pr-number}

# View workflow runs
gh run list --branch {branch-name}

# View specific run
gh run view {run-id}

# Watch run (auto-refresh)
gh run watch {run-id}
```

### Polling Strategy

```python
import time

max_wait = 1800  # 30 minutes
poll_interval = 30  # 30 seconds
elapsed = 0

while elapsed < max_wait:
    status = check_pr_status()
    if status == "success":
        break
    elif status == "failure":
        report_failure()
        exit(1)
    time.sleep(poll_interval)
    elapsed += poll_interval

if elapsed >= max_wait:
    report_timeout()
    exit(1)
```

### CI Failure Handling

If CI fails:

1. Review failure logs: `gh run view {run-id} --log-failed`
1. Identify failure cause
1. Fix issue locally
1. Run tests: `pytest`
1. Run quality checks: `make quality`
1. Commit fix
1. Push: `git push`
1. Wait for re-run
1. Repeat if necessary

## Error Handling

### Missing Task File

```
🔴 Error: Task file not found

File: tasks/bug-fixes/007-api-404-handling.md

Please verify:
- File path is correct
- File exists in repository
- You have read permissions

Usage: /implement-task tasks/{category}/{id}-{slug}.md
```

### Invalid Task File

```
🔴 Error: Invalid task file format

File: tasks/bug-fixes/007-api-404-handling.md

Missing required sections:
- Implementation Steps
- Testing Strategy
- Acceptance Criteria

Please update task file to include all required sections.
```

### Unmet Dependencies

```
🔴 Error: Task dependencies not met

Task: 007-api-404-handling
Depends on:
- Task 005-api-base-client (Status: In Progress)
- Package 'requests-retry' (Status: Not Installed)

Please complete dependencies before implementing this task.
```

### Branch Already Exists

```
🔴 Error: Branch already exists

Branch: bug-fixes/007-api-404-handling

Options:
1. Delete existing branch: git branch -D bug-fixes/007-api-404-handling
2. Use existing branch: git checkout bug-fixes/007-api-404-handling
3. Choose different task

Continue? [y/N]
```

### CI Timeout

```
⏱️  CI Timeout

PR #54 checks have been running for 30 minutes.

Current status:
- ✅ pre-commit: Passed
- ✅ test-py310: Passed
- ✅ test-py311: Passed
- 🔄 test-py312: Running (25 minutes)

Options:
1. Continue waiting
2. Cancel and investigate
3. Merge anyway (if non-critical)

What would you like to do?
```

### Merge Conflicts

```
🔴 Error: Merge conflicts detected

PR #54 has conflicts with main branch.

Conflicting files:
- src/nhl_scrabble/api/nhl_client.py
- tests/unit/test_nhl_client.py

Resolution steps:
1. Update branch: git pull origin main
2. Resolve conflicts in listed files
3. Run tests: pytest
4. Commit resolution: git add . && git commit
5. Push: git push

Continue with automatic resolution? [y/N]
```

## Safety Considerations

**Before Implementation**:

- ✅ Verify main branch is up-to-date
- ✅ Check task dependencies are met
- ✅ Review task specification thoroughly
- ✅ Understand acceptance criteria
- ✅ Estimate realistic time commitment

**During Implementation**:

- ✅ Follow coding standards
- ✅ Write tests alongside code
- ✅ Commit frequently with clear messages
- ✅ Keep changes focused on task scope
- ✅ Run tests regularly
- ✅ Update documentation as you go

**Before PR**:

- ✅ Run full test suite
- ✅ Run all quality checks
- ✅ Review all changes
- ✅ Update CHANGELOG.md
- ✅ Verify acceptance criteria

**Before Merge**:

- ✅ All CI checks pass
- ✅ Code review approved (if required)
- ✅ No merge conflicts
- ✅ Documentation complete
- ✅ Breaking changes documented

**After Merge**:

- ✅ Verify merge succeeded
- ✅ Smoke test main branch
- ✅ Clean up branches
- ✅ Update local repository

## Usage

```bash
# Implement a specific task
/implement-task tasks/bug-fixes/007-api-404-handling.md

# Implement with custom options
/implement-task tasks/new-features/002-rest-api-server.md --wait-timeout 3600

# Dry run (show plan without executing)
/implement-task tasks/optimization/003-cache-api.md --dry-run

# Skip CI wait (for quick fixes)
/implement-task tasks/bug-fixes/008-typo-fix.md --no-wait

# Auto-merge on success (requires approval settings)
/implement-task tasks/testing/004-add-coverage.md --auto-merge
```

## Example Output

```
🚀 Implementing Task: Fix API 404 handling

Task Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File: tasks/bug-fixes/007-api-404-handling.md
Title: Fix NHL API 404 error handling
Priority: HIGH
Estimated: 1-2h
Issue: #52 - https://github.com/user/repo/issues/52

Steps:
1. ✅ Parse task file
2. ✅ Create branch: bug-fixes/007-api-404-handling
3. 🔄 Implement solution...
   - Updated NHLClient.fetch_team_roster()
   - Added NHLApiNotFoundError exception
   - Added exception hierarchy
4. 🔄 Implement tests...
   - Added 12 unit tests
   - Added 3 integration tests
   - Coverage: 95%
5. ✅ Verify acceptance criteria
   - [x] Raises NHLApiNotFoundError on 404
   - [x] Tests cover 404 scenarios
   - [x] Documentation updated
   - [x] All tests pass
6. ✅ Update documentation
   - Updated API client docstrings
   - Updated error handling docs
   - Updated CHANGELOG.md
7. ✅ Create pull request
   - PR #54: https://github.com/user/repo/pull/54
8. ✅ Update task file
   - Marked acceptance criteria complete
   - Added implementation notes
   - Documented actual effort: 2.5h
9. ✅ Move to completed: tasks/completed/bug-fixes/007-api-404-handling.md
10. ✅ Update tasks/README.md
11. ✅ Commit and push changes
12. ⏱️  Wait for CI/CD (estimated: 3-5 minutes)
    - ✅ pre-commit: Passed (30s)
    - ✅ test-py310: Passed (1m 15s)
    - ✅ test-py311: Passed (1m 20s)
    - ✅ test-py312: Passed (1m 18s)
    - ✅ ruff-check: Passed (15s)
    - ✅ mypy: Passed (45s)
    - ✅ coverage: Passed (1m 30s)
13. ✅ Merge pull request (squash)
14. ✅ Close GitHub issue #52
15. ✅ Return to main branch
16. ✅ Update local main
17. ✅ Delete branch: bug-fixes/007-api-404-handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Task Implementation Complete!

Summary:
  Task: Fix API 404 handling (bug-fixes/007)
  Priority: HIGH
  Estimated: 1-2h
  Actual: 2.5h
  Status: ✅ Complete

Implementation:
  Branch: bug-fixes/007-api-404-handling (deleted)
  Commits: 3 commits (a1b2c3d, d4e5f6g, h7i8j9k)
  Files changed: 8 files
  Lines: +247 -15
  Tests: 15 new tests, all passing
  Coverage: 95% on modified code

Pull Request:
  PR #54: https://github.com/user/repo/pull/54
  Status: ✅ Merged
  Checks: 7/7 passed
  Reviews: 1 approval

GitHub Issue:
  Issue #52: ✅ Closed

Task File:
  Location: tasks/completed/bug-fixes/007-api-404-handling.md
  Status: Complete with implementation notes

Next Steps:
  ✨ Task complete and merged!
  📋 tasks/README.md updated
  🎯 Ready for next task

Total time: 2.5h
```

## Integration with Other Commands

**Works with**:

- `/create-task` - Creates task files that this command implements
- `/analyze-project` - Generates tasks for this command to implement
- `/update-docs` - Can be run after implementation to polish docs
- `/git:commit` - Used internally for commits
- `/gh:create-pr` - Used internally for PR creation
- `/gh:merge-pr` - Used internally for merging

**Workflow**:

```bash
# 1. Analyze project to find improvements
/analyze-project

# 2. Creates tasks automatically (via analyze-project)
# tasks/optimization/003-cache-api-responses.md created

# 3. Implement specific task
/implement-task tasks/optimization/003-cache-api-responses.md

# 4. Task is complete, merged, and documented!
```

## Configuration

### Default Settings

```bash
# CI wait timeout (seconds)
CI_WAIT_TIMEOUT=1800  # 30 minutes

# CI poll interval (seconds)
CI_POLL_INTERVAL=30  # 30 seconds

# Auto-merge on success
AUTO_MERGE=false

# Delete remote branch on merge
DELETE_REMOTE_BRANCH=true

# Merge strategy
MERGE_STRATEGY=squash  # squash|merge|rebase

# Require approval before merge
REQUIRE_APPROVAL=false

# Run tests before commit
PRE_COMMIT_TEST=true
```

### Per-Task Configuration

Add to task file frontmatter:

```markdown
---
auto_merge: false
merge_strategy: squash
require_approval: true
ci_timeout: 3600
---
```

## Best Practices

**Task Implementation**:

1. **Read carefully**: Understand entire task before starting
1. **Follow plan**: Use implementation steps as guide
1. **Test early**: Write tests alongside code
1. **Commit often**: Small, focused commits
1. **Document as you go**: Update docs with code changes
1. **Stay focused**: Avoid scope creep

**Testing**:

1. **Write tests first**: TDD when appropriate
1. **Cover edge cases**: Don't just test happy path
1. **Test errors**: Verify error handling
1. **Integration tests**: Test component interactions
1. **Manual testing**: Verify user-facing changes

**Documentation**:

1. **Docstrings**: Complete docstrings for all public APIs
1. **Comments**: Explain complex logic
1. **Examples**: Working code examples
1. **Changelog**: Document all changes
1. **README**: Update if public API changed

**Git Workflow**:

1. **Branch naming**: Follow convention
1. **Commit messages**: Clear and descriptive
1. **PR description**: Complete and detailed
1. **Review changes**: Before pushing
1. **Clean history**: Squash if appropriate

## Troubleshooting

**Implementation taking longer than estimated**:

- Document why in implementation notes
- Update effort estimate if significantly off
- Consider breaking into smaller tasks

**Tests failing**:

- Review test output carefully
- Fix root cause, not symptoms
- Don't skip tests
- Add more tests if coverage gaps found

**CI checks failing**:

- Review failure logs
- Fix locally and test
- Don't bypass checks
- Ask for help if stuck

**Merge conflicts**:

- Update from main: `git pull origin main`
- Resolve carefully
- Re-run tests
- Verify resolution

**Documentation incomplete**:

- Review all modified files
- Check docstring coverage
- Update CHANGELOG.md
- Update relevant guides

## Tips

- **Start small**: Choose smaller tasks to learn workflow
- **Use dry-run**: Test command without executing
- **Review changes**: Always review before pushing
- **Test thoroughly**: Better to catch bugs early
- **Document well**: Future you will thank you
- **Ask for help**: If stuck, ask before continuing
- **Learn from deviations**: Update estimates based on actual effort
- **Keep it focused**: One task at a time
- **Celebrate wins**: Task complete is an achievement!

## Related Commands

- `/create-task` - Create task specification
- `/analyze-project` - Generate task roadmap
- `/update-docs` - Update documentation
- `/git:commit` - Commit changes
- `/gh:create-pr` - Create pull request
- `/gh:merge-pr` - Merge pull request

## Notes

- This command automates the complete workflow
- Always review automated changes before final push
- CI must pass before merge
- Task files are permanent record of work
- Actual effort tracking improves future estimates
- Implementation notes help team learning
- Breaking changes must be documented
- Security considerations must be noted
