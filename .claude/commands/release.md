# Release Package

______________________________________________________________________

## title: 'Release Package' read_only: false type: 'command'

Automate the complete release process for the nhl-scrabble package.

## Status

**Phase 1 Complete**: Pre-Release Validation ✅
**Phase 2-7**: Coming in future tasks (see tasks/new-features/019-comprehensive-release-automation-skill.md)

## Usage

```bash
# Interactive mode (current: Phase 1 only - validation)
/release

# With options (future phases)
/release --version 2.1.0      # Specify version
/release --type patch         # Auto-bump patch version
/release --type minor         # Auto-bump minor version
/release --type major         # Auto-bump major version
/release --dry-run            # Preview without making changes
```

## Process

This command executes the release process in phases. Currently only Phase 1 is implemented.

### Phase 1: Pre-Release Validation ✅

Validate that the repository is ready for a release by checking git status, running tests, verifying CI, and determining the next version.

**Step 1: Check Git Status**

Verify the working directory is clean and ready for release:

```bash
# Check for uncommitted changes
git status --porcelain

# If output is not empty:
# - Show list of uncommitted files
# - Error: "Uncommitted changes detected. Please commit or stash changes before releasing."
# - Exit with failure
```

**Requirements:**
- No uncommitted changes (git status --porcelain returns empty)
- Working tree must be clean

**Error Handling:**
- If uncommitted changes exist:
  - List all uncommitted files with their status
  - Prompt user: "Would you like to see 'git status' output? [y/N]"
  - If yes: Run `git status` and display full output
  - Suggest: "Please commit or stash changes: git add -A && git commit or git stash"
  - Exit with clear error message

**Step 2: Verify Current Branch**

Ensure we're on the main branch before releasing:

```bash
# Get current branch name
current_branch=$(git branch --show-current)

# Check if on main/master
if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    # Error: "Not on main branch (currently on: $current_branch)"
    # Suggest: git checkout main
    # Exit with failure
fi
```

**Requirements:**
- Must be on `main` or `master` branch
- No releases from feature branches

**Error Handling:**
- If on wrong branch:
  - Show current branch name
  - Show main branch name (from git remote show origin)
  - Prompt: "Would you like to switch to main? [y/N]"
  - If yes: Run `git checkout main` or `git checkout master`
  - If no: Exit with instructions

**Step 3: Ensure Up-to-Date with Remote**

Verify local main is synchronized with origin:

```bash
# Fetch latest from origin
git fetch origin

# Get local and remote commit SHAs
local_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse origin/$(git branch --show-current))

# Compare
if [ "$local_sha" != "$remote_sha" ]; then
    # Check if local is ahead, behind, or diverged
    git rev-list --left-right --count HEAD...origin/$(git branch --show-current)

    # If behind: Error and suggest git pull
    # If ahead: Warning (OK to release, will push later)
    # If diverged: Error and suggest git pull --rebase
fi
```

**Requirements:**
- Local main should not be behind origin/main
- Local main can be ahead (unpushed commits OK if tests pass)
- Local main must not be diverged from origin/main

**Error Handling:**
- If behind origin:
  - Show number of commits behind
  - Show latest remote commits: `git log HEAD..origin/main --oneline -5`
  - Prompt: "Would you like to pull changes? [y/N]"
  - If yes: Run `git pull`
  - If no: Exit with error
- If diverged:
  - Show divergence status
  - Error: "Local and remote have diverged. Please resolve before releasing."
  - Suggest: `git pull --rebase` or `git reset --hard origin/main`
  - Exit with failure
- If ahead:
  - Show number of commits ahead
  - Show commits to be pushed: `git log origin/main..HEAD --oneline`
  - Info: "Local has unpushed commits. These will be pushed during release."
  - Continue (this is OK)

**Step 4: Run Full Test Suite**

Execute comprehensive test suite to ensure code quality:

```bash
# Run pytest with coverage
pytest --cov --cov-report=term-missing --cov-report=html -v

# Check exit code
if [ $? -ne 0 ]; then
    # Error: "Test suite failed. Please fix failing tests before releasing."
    # Show: pytest output with failures
    # Exit with failure
fi
```

**Requirements:**
- All tests must pass (pytest exit code 0)
- Recommended: Coverage ≥80% (warn if below, but don't fail)
- Test run must complete without errors

**Error Handling:**
- If tests fail:
  - Display pytest output showing failures
  - Count number of failed tests
  - List failed test names
  - Suggest: "Fix failing tests and re-run: pytest -v"
  - Option: "Would you like to see verbose output? [y/N]"
  - If yes: Run `pytest -vv --tb=short`
  - Exit with failure
- If coverage below threshold:
  - Show current coverage percentage
  - Show files with low coverage
  - Warning: "Coverage is {coverage}%, below recommended 80%"
  - Prompt: "Continue anyway? [y/N]"
  - If yes: Continue
  - If no: Exit with message to improve coverage

**Step 5: Run Quality Checks**

Execute all code quality checks (linting, formatting, type checking):

```bash
# Run ruff linting
ruff check src/ tests/

# Run ruff formatting check
ruff format --check src/ tests/

# Run mypy type checking
mypy src/

# Check exit codes
if [ $? -ne 0 ]; then
    # Error: "Quality checks failed. Please fix issues before releasing."
    # Exit with failure
fi
```

**Requirements:**
- No ruff linting errors
- Code must be properly formatted (ruff format)
- No mypy type errors
- All quality checks must pass

**Error Handling:**
- If ruff check fails:
  - Display ruff output with violations
  - Count number of violations
  - Suggest: "Fix violations: ruff check --fix src/ tests/"
  - Option: "Would you like to auto-fix? [y/N]"
  - If yes: Run `ruff check --fix src/ tests/`
  - Exit with failure (or continue if fixed)
- If format check fails:
  - Display files that need formatting
  - Suggest: "Format code: ruff format src/ tests/"
  - Option: "Would you like to auto-format? [y/N]"
  - If yes: Run `ruff format src/ tests/`
  - Exit with failure (or continue if formatted)
- If mypy fails:
  - Display mypy errors with line numbers
  - Count number of type errors
  - Suggest: "Fix type errors and re-run: mypy src/"
  - Exit with failure

**Step 6: Verify CI Passing on Main**

Check that CI is passing on the main branch:

```bash
# Get latest CI run for main branch
gh run list --branch main --limit 1 --json conclusion,status,workflowName,createdAt

# Parse result
# - status: "completed"
# - conclusion: "success"

# If not successful:
# - Error: "CI is failing on main branch"
# - Show workflow run details
# - Exit with failure
```

**Requirements:**
- Latest CI run on main must have conclusion: "success"
- CI run must be completed (not pending/in_progress)
- CI run should be recent (warn if >24h old)

**Error Handling:**
- If CI not complete:
  - Show current CI status (pending/in_progress)
  - Show workflow name and start time
  - Info: "CI is currently running on main"
  - Prompt: "Wait for CI to complete? [y/N]"
  - If yes: Poll every 30s until complete, then re-check conclusion
  - If no: Exit with instructions
- If CI failed:
  - Show workflow run details
  - Show failed jobs: `gh run view {run-id} --json jobs`
  - Display failure summary
  - Suggest: "View logs: gh run view {run-id}"
  - Option: "Would you like to view failure details? [y/N]"
  - If yes: Run `gh run view {run-id} --log-failed`
  - Exit with error: "Fix CI failures before releasing"
- If CI is stale (>24h old):
  - Warning: "Latest CI run is {age} old"
  - Show run details (created_at, conclusion)
  - Prompt: "Trigger a fresh CI run? [y/N]"
  - If yes: Create empty commit or use gh workflow dispatch
  - If no: Prompt: "Continue with stale CI status? [y/N]"

**Step 7: Determine Next Version**

Calculate the next version number based on current version and bump type:

```bash
# Get current version from pyproject.toml
current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Parse semantic version: MAJOR.MINOR.PATCH
# Example: "0.0.12" -> major=0, minor=0, patch=12

# Ask user for version bump type (if not specified via --type flag)
echo "Current version: $current_version"
echo "Select version bump type:"
echo "1) patch (0.0.12 -> 0.0.13) - Bug fixes, minor changes"
echo "2) minor (0.0.12 -> 0.1.0) - New features, backward compatible"
echo "3) major (0.0.12 -> 1.0.0) - Breaking changes"
echo "4) custom - Specify exact version"
read -p "Choice [1-4]: " choice

# Calculate next version based on choice
case $choice in
    1) # Patch bump
        next_version="${major}.${minor}.$((patch + 1))"
        ;;
    2) # Minor bump
        next_version="${major}.$((minor + 1)).0"
        ;;
    3) # Major bump
        next_version="$((major + 1)).0.0"
        ;;
    4) # Custom
        read -p "Enter version (e.g., 2.1.0): " next_version
        # Validate format: X.Y.Z
        if ! [[ "$next_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            # Error: "Invalid version format. Use X.Y.Z (e.g., 2.1.0)"
            # Exit with failure
        fi
        ;;
esac

# Validate next_version > current_version
# Compare versions (implement semantic version comparison)
```

**Requirements:**
- Next version must be valid semantic version (X.Y.Z format)
- Next version must be greater than current version
- Version must not already exist as a git tag
- Version should follow semantic versioning rules

**Error Handling:**
- If invalid format:
  - Error: "Invalid version format: {version}"
  - Explain: "Must be semantic version: MAJOR.MINOR.PATCH (e.g., 2.1.0)"
  - Re-prompt for version
- If version not greater than current:
  - Error: "New version {new} must be greater than current {current}"
  - Show version comparison
  - Re-prompt for version
- If version tag already exists:
  - Error: "Git tag v{version} already exists"
  - Show existing tag details: `git show v{version} --stat`
  - Suggest: "Choose a different version or delete old tag"
  - Exit with failure

**Step 8: Show Commits Since Last Release**

Display commits that will be included in the release:

```bash
# Get latest version tag
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# If no tags exist, show all commits
if [ -z "$latest_tag" ]; then
    echo "No previous releases found. All commits will be included."
    git log --oneline --decorate
else
    echo "Commits since $latest_tag:"
    git log $latest_tag..HEAD --oneline --decorate

    # Categorize commits by type (if using conventional commits)
    echo ""
    echo "Features:"
    git log $latest_tag..HEAD --oneline | grep "^[a-f0-9]* feat:" || echo "  (none)"

    echo ""
    echo "Bug Fixes:"
    git log $latest_tag..HEAD --oneline | grep "^[a-f0-9]* fix:" || echo "  (none)"

    echo ""
    echo "Breaking Changes:"
    git log $latest_tag..HEAD --grep="BREAKING CHANGE" --oneline || echo "  (none)"
fi
```

**Requirements:**
- Display all commits since last release tag
- Categorize by conventional commit types (if applicable)
- Highlight breaking changes
- Show commit count and contributor summary

**Output:**
- List of commits with short hashes and messages
- Categorized by type (feat, fix, docs, etc.)
- Breaking changes highlighted
- Summary stats (X commits, Y contributors)

**Step 9: Pre-Release Validation Summary**

Display comprehensive validation summary and prompt for confirmation:

```
✅ Pre-Release Validation Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Git Status:
  ✅ No uncommitted changes
  ✅ On main branch
  ✅ Up-to-date with origin/main (3 commits ahead)

Tests:
  ✅ All tests passing (170 tests)
  ✅ Coverage: 87.3% (above 80% threshold)

Quality:
  ✅ Ruff: No violations
  ✅ Format: All files formatted
  ✅ Mypy: No type errors

CI Status:
  ✅ Latest run: success
  ⚠️  Run age: 2 hours old
  ℹ️  Workflow: CI / Test

Version:
  Current: 0.0.12
  Next: 0.0.13 (patch)
  Type: Bug fixes and minor improvements

Commits Since v0.0.12: (3 commits)
  - fix(api): Handle 404 errors properly (#261)
  - docs(readme): Update installation instructions
  - test(coverage): Add tests for error scenarios

Breaking Changes: None

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps (Phase 2+):
  - Version Bumping (not yet implemented)
  - Build and Validate (not yet implemented)
  - Publish to PyPI (not yet implemented)
  - Create GitHub Release (not yet implemented)
  - Deploy Documentation (not yet implemented)
  - Post-Release Tasks (not yet implemented)

⚠️  Note: Only Phase 1 (Pre-Release Validation) is currently implemented.
    Future phases will be added in subsequent tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository is ready for release!

To proceed manually:
1. Update version in pyproject.toml, __init__.py, etc.
2. Update CHANGELOG.md
3. Commit: git commit -m "Release v0.0.13"
4. Tag: git tag -a v0.0.13 -m "Release version 0.0.13"
5. Push: git push && git push --tags
6. Wait for CI to build and publish to PyPI
7. Create GitHub release: gh release create v0.0.13

See tasks/new-features/019-comprehensive-release-automation-skill.md for full automation roadmap.
```

### Phase 2-7: Coming Soon

Future phases will be implemented in subsequent tasks:

- **Phase 2**: Version Bumping (task 026)
- **Phase 3**: Build and Validate (task 027)
- **Phase 4**: Publish (task 028)
- **Phase 5**: Documentation Deployment (task 029)
- **Phase 6**: Post-Release Tasks (task 030)
- **Phase 7**: Verification and Cleanup (task 031)

See parent task: `tasks/new-features/019-comprehensive-release-automation-skill.md`

## Configuration

**Future**: Configuration will be added to `pyproject.toml` under `[tool.release]` section.

**Planned Configuration** (Phase 2+):

```toml
[tool.release]
# Version bump behavior
version_files = [
    "pyproject.toml",
    "src/nhl_scrabble/__init__.py",
]

# Pre-release checks
require_tests = true
require_quality_checks = true
require_clean_working_directory = true
require_main_branch = true
min_coverage_threshold = 80.0
allow_stale_ci = false
max_ci_age_hours = 24
```

## Error Handling

All validation steps include comprehensive error handling:

1. **Clear Error Messages**: Describe what went wrong and why
1. **Actionable Suggestions**: Tell user exactly how to fix the issue
1. **Interactive Prompts**: Offer to auto-fix when possible
1. **Graceful Exits**: Stop process cleanly on validation failures
1. **Detailed Context**: Show relevant command output and state

## Safety Features

Phase 1 focuses on validation only - no destructive actions:

- ✅ Read-only git operations
- ✅ No file modifications
- ✅ No commits or tags created
- ✅ No pushes to remote
- ✅ No publishing actions
- ✅ Safe to run anytime

## Usage Examples

**Example 1: Basic Validation**

```bash
/release

# Output:
# ✅ Pre-Release Validation Complete
# Repository is ready for release!
# Next version: 0.0.13 (patch)
```

**Example 2: Validation with Issues**

```bash
/release

# Output:
# ❌ Pre-Release Validation Failed
#
# Issues found:
# 1. ❌ Uncommitted changes detected (3 files)
# 2. ❌ Test suite failed (2 tests failing)
# 3. ⚠️  CI is stale (25 hours old)
#
# Please fix these issues before releasing.
```

**Example 3: Interactive Prompts**

```bash
/release

# Interactive prompts:
# Current version: 0.0.12
# Select version bump type:
# 1) patch (0.0.12 -> 0.0.13) - Bug fixes
# 2) minor (0.0.12 -> 0.1.0) - New features
# 3) major (0.0.12 -> 1.0.0) - Breaking changes
# 4) custom - Specify exact version
# Choice [1-4]: 1
#
# ⚠️  Latest CI run is 3 hours old
# Trigger a fresh CI run? [y/N]: n
# Continue with stale CI status? [y/N]: y
#
# ✅ Validation complete!
```

## Testing

**Manual Testing Checklist:**

Phase 1 validation can be tested with various repository states:

- [ ] Test with clean working directory
- [ ] Test with uncommitted changes (should fail)
- [ ] Test on feature branch (should fail)
- [ ] Test when behind origin/main (should fail)
- [ ] Test with failing tests (should fail)
- [ ] Test with quality violations (should fail)
- [ ] Test with failing CI (should fail)
- [ ] Test with stale CI (should warn)
- [ ] Test version determination (all bump types)
- [ ] Test with no previous tags (first release)
- [ ] Test with existing version tag (should fail)

**Safe Testing:**

Since Phase 1 is read-only, it's safe to test on the real repository:

```bash
# Test in current state
/release

# Test with uncommitted changes
echo "test" > temp_file.txt
/release  # Should fail
rm temp_file.txt

# Test on feature branch
git checkout -b test-branch
/release  # Should fail
git checkout main
git branch -D test-branch
```

## Troubleshooting

**Issue: "Uncommitted changes detected"**

```bash
# View changes
git status

# Option 1: Commit changes
git add -A
git commit -m "commit message"

# Option 2: Stash changes
git stash

# Then retry
/release
```

**Issue: "Not on main branch"**

```bash
# Switch to main
git checkout main

# Then retry
/release
```

**Issue: "CI is failing on main branch"**

```bash
# View CI status
gh run list --branch main --limit 5

# View latest run
gh run view

# View failure logs
gh run view --log-failed

# Fix issues, commit, push
# Wait for CI to pass
# Then retry
/release
```

**Issue: "Test suite failed"**

```bash
# Run tests locally
pytest -vv

# Fix failing tests
# Commit fixes
# Then retry
/release
```

## Related Commands

- `/git:status` - Check git status
- `/git:log` - View commit history
- `/gh:pr-status` - Check CI status
- `/test-optional-dependencies` - Validate test environment

## Implementation Notes

**Phase 1 Complete**: 2026-04-30

This initial implementation provides comprehensive pre-release validation:

- Git status checking with detailed error handling
- Branch verification (main/master)
- Remote synchronization checks
- Full test suite execution with coverage reporting
- Code quality validation (ruff, mypy)
- CI status verification with staleness detection
- Semantic version determination with validation
- Commit history review and categorization
- Interactive prompts for user decisions
- Comprehensive validation summary

**Future Phases**: Will be implemented in tasks 026-031 as sub-tasks of the parent task (#247).

**Design Decisions**:

1. **Read-Only Phase 1**: Deliberately made validation non-destructive to allow safe testing
1. **Interactive Prompts**: Provide user control over decisions (version bump type, handling warnings)
1. **Comprehensive Error Messages**: Include context, suggestions, and options for all failures
1. **Staleness Detection**: Warn about old CI runs to prevent releasing with stale validation
1. **Version Validation**: Prevent common versioning errors (non-semver, duplicate tags, downgrades)

**Testing Approach**: All validation logic can be safely tested on the live repository since no modifications are made.

**Next Steps**: Implement Phase 2 (Version Bumping) in task 026.
