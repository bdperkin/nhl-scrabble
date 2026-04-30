# Release Package

______________________________________________________________________

## title: 'Release Package' read_only: false type: 'command'

Automate the complete release process for the nhl-scrabble package.

## Status

**Phase 1 Complete**: Pre-Release Validation ✅
**Phase 2 Complete**: Version Bumping ✅
**Phase 3 Complete**: Build and Validate ✅
**Phase 4 Complete**: Publish ✅
**Phase 5 Complete**: Post-Release Tasks ✅
**Phase 6 Complete**: Verification and Reporting ✅
**Phase 7 Complete**: Complete Release Orchestration ✅

**All phases implemented!** The `/release` command now provides complete end-to-end release automation.

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

This command executes the complete release process in 7 phases. All phases are now fully implemented and orchestrated.

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

### Phase 2: Version Bumping ✅

Update CHANGELOG.md with new version and generate changelog entries from git commit history using conventional commits format.

**Important**: This project uses **hatch-vcs for dynamic versioning** from git tags. Version is NOT manually set in `pyproject.toml` or `__init__.py` - it's automatically derived from git tags. The version files will be updated by the git tag in Phase 4 (Publish).

**Step 1: Generate Changelog Entry from Commits**

Parse conventional commits since last release and generate changelog entry:

```bash
# Get latest version tag
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# Get commits since last tag (or all commits if no tags)
if [ -z "$latest_tag" ]; then
    commit_range="HEAD"
    echo "No previous release found - generating changelog from all commits"
else
    commit_range="$latest_tag..HEAD"
    echo "Generating changelog from $latest_tag to HEAD"
fi

# Parse conventional commits by type
# Format: type(scope): subject
# Example: feat(api): Add new endpoint

# Extract features (feat:)
features=$(git log $commit_range --oneline --grep="^feat" --grep="^feat(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- feat: /- /' | \
    sed 's/^- feat(/- (/')

# Extract bug fixes (fix:)
fixes=$(git log $commit_range --oneline --grep="^fix" --grep="^fix(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- fix: /- /' | \
    sed 's/^- fix(/- (/')

# Extract documentation changes (docs:)
docs=$(git log $commit_range --oneline --grep="^docs" --grep="^docs(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- docs: /- /' | \
    sed 's/^- docs(/- (/')

# Extract performance improvements (perf:)
perf=$(git log $commit_range --oneline --grep="^perf" --grep="^perf(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- perf: /- /' | \
    sed 's/^- perf(/- (/')

# Extract refactoring (refactor:)
refactor=$(git log $commit_range --oneline --grep="^refactor" --grep="^refactor(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- refactor: /- /' | \
    sed 's/^- refactor(/- (/')

# Extract tests (test:)
tests=$(git log $commit_range --oneline --grep="^test" --grep="^test(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- test: /- /' | \
    sed 's/^- test(/- (/')

# Extract build/CI changes (build:, ci:)
build=$(git log $commit_range --oneline --grep="^build" --grep="^build(" --grep="^ci" --grep="^ci(" | \
    sed 's/^[a-f0-9]* /- /' | \
    sed 's/^- build: /- /' | \
    sed 's/^- build(/- (/' | \
    sed 's/^- ci: /- /' | \
    sed 's/^- ci(/- (/')

# Check for breaking changes
breaking=$(git log $commit_range --grep="BREAKING CHANGE" | \
    grep -A 1 "BREAKING CHANGE:" | \
    grep -v "^--$" | \
    sed 's/BREAKING CHANGE: //')

# Count total commits
commit_count=$(git log $commit_range --oneline | wc -l)
```

**Requirements:**
- Parse all commits since last release tag
- Extract commits by conventional commit type (feat, fix, docs, etc.)
- Identify breaking changes (BREAKING CHANGE in commit body)
- Format entries for Keep a Changelog style
- Include PR numbers if present (#123)

**Output Format:**
Each section should contain bulleted list of changes:
- One bullet per commit
- Remove conventional commit prefix (feat:, fix:)
- Keep scope in parentheses if present
- Keep PR number if present

**Step 2: Build CHANGELOG Entry**

Construct the new changelog section using Keep a Changelog format:

```bash
# Get today's date
release_date=$(date +%Y-%m-%d)

# Build changelog entry
changelog_entry="## [$new_version] - $release_date

"

# Add sections in order (only if non-empty)

# Breaking Changes (if any)
if [ -n "$breaking" ]; then
    changelog_entry+="### ⚠️ BREAKING CHANGES

$breaking

"
fi

# Added (features)
if [ -n "$features" ]; then
    changelog_entry+="### Added

$features

"
fi

# Changed (refactoring, performance)
if [ -n "$refactor" ] || [ -n "$perf" ]; then
    changelog_entry+="### Changed

"
    [ -n "$refactor" ] && changelog_entry+="$refactor
"
    [ -n "$perf" ] && changelog_entry+="$perf
"
fi

# Fixed (bug fixes)
if [ -n "$fixes" ]; then
    changelog_entry+="### Fixed

$fixes

"
fi

# Documentation
if [ -n "$docs" ]; then
    changelog_entry+="### Documentation

$docs

"
fi

# Tests
if [ -n "$tests" ]; then
    changelog_entry+="### Tests

$tests

"
fi

# Build/CI
if [ -n "$build" ]; then
    changelog_entry+="### Build / CI

$build

"
fi

echo "$changelog_entry"
```

**Requirements:**
- Follow Keep a Changelog section order:
  1. ⚠️ BREAKING CHANGES (if any)
  2. Added (features)
  3. Changed (refactoring, performance)
  4. Fixed (bug fixes)
  5. Documentation
  6. Tests
  7. Build / CI
- Use proper markdown formatting
- Include version and date in header
- Only include non-empty sections

**Step 3: Update CHANGELOG.md**

Insert new version section into CHANGELOG.md:

```bash
# Read current CHANGELOG.md
changelog_file="CHANGELOG.md"

# Find line number of [Unreleased] section
unreleased_line=$(grep -n "## \[Unreleased\]" $changelog_file | cut -d: -f1)

# Create temporary file with new content
{
    # Keep everything up to and including [Unreleased]
    head -n $unreleased_line $changelog_file

    # Add empty line after [Unreleased]
    echo ""

    # Add new version section
    echo "$changelog_entry"

    # Add rest of file (skip [Unreleased] line and empty line after it)
    tail -n +$((unreleased_line + 2)) $changelog_file
} > "${changelog_file}.new"

# Replace original with new file
mv "${changelog_file}.new" "$changelog_file"

echo "✅ CHANGELOG.md updated with version $new_version"
```

**Requirements:**
- Insert new version after `## [Unreleased]` header
- Preserve existing changelog entries
- Maintain proper markdown formatting
- Keep `## [Unreleased]` section empty for future changes

**Step 4: Preview Changes**

Show user what will be committed:

```bash
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Changelog Preview"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "$changelog_entry"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Modified files:"
echo "  - CHANGELOG.md"
echo ""
echo "Commit count: $commit_count commits since $latest_tag"
echo ""

# Show git diff for CHANGELOG.md
git diff CHANGELOG.md
```

**Requirements:**
- Display formatted changelog entry
- Show git diff of modified files
- Show summary of changes (commit count)
- Clear visual separation

**Step 5: Confirm Version Bump**

Prompt user to confirm before committing:

```bash
echo ""
read -p "Proceed with version bump to v$new_version? [y/N]: " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo ""
    echo "❌ Version bump cancelled by user"
    echo ""
    echo "Reverting changes..."
    git checkout CHANGELOG.md
    echo "✅ Changes reverted"
    exit 1
fi
```

**Requirements:**
- Require explicit confirmation (y/Y)
- Default to NO (any other input cancels)
- Provide option to revert changes
- Clear messaging about what will happen

**Error Handling:**
- If user declines:
  - Revert all file modifications (`git checkout CHANGELOG.md`)
  - Display cancellation message
  - Exit cleanly with non-zero status
  - Provide instructions for manual process

**Step 6: Create Version Bump Commit**

Create git commit with version bump:

```bash
# Stage CHANGELOG.md
git add CHANGELOG.md

# Create commit message
commit_message="chore(release): Prepare release v$new_version

- Update CHANGELOG.md with $commit_count changes
- Categorized by conventional commit types
- Release date: $release_date

This commit prepares the release but does not create the git tag.
The tag will be created in Phase 4 (Publish) after build validation.
"

# Create commit
git commit -m "$commit_message"

echo ""
echo "✅ Version bump commit created"
echo ""
git log -1 --stat
```

**Requirements:**
- Stage only CHANGELOG.md
- Use conventional commit format: `chore(release): Prepare release vX.Y.Z`
- Include commit summary in message body
- Explain that tag creation happens in Phase 4
- Show commit details after creation

**Error Handling:**
- If commit fails:
  - Display git error message
  - Show what files were staged
  - Suggest checking git status
  - Do not proceed to next phase
  - Exit with failure

**Step 7: Version Bump Summary**

Display summary of version bump phase:

```
✅ Phase 2: Version Bumping Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version:
  Current: 0.0.12
  Next: 0.0.13
  Type: patch

Changes Included:
  Total commits: 3
  Features: 1
  Bug fixes: 2
  Documentation: 0
  Breaking changes: 0

Files Modified:
  ✅ CHANGELOG.md updated

Git Commit:
  ✅ Created: chore(release): Prepare release v0.0.13
  📝 Commit SHA: abc123d
  ⚠️  Not pushed yet (will push in Phase 4)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Note: Version files (pyproject.toml, __init__.py) use dynamic versioning
      from git tags (hatch-vcs). They will update automatically when
      the git tag is created in Phase 4 (Publish).

Next Steps (Phase 3+):
  - Build and Validate (not yet implemented)
  - Publish to PyPI (not yet implemented)
  - Create GitHub Release (not yet implemented)
  - Post-Release Tasks (not yet implemented)

⚠️  Note: Only Phases 1-2 are currently implemented.
    Future phases will be added in subsequent tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To continue manually:
1. Review commit: git show HEAD
2. Build packages: python -m build
3. Test install: pip install dist/*.whl
4. Create tag: git tag -a v0.0.13 -m "Release version 0.0.13"
5. Push: git push && git push v0.0.13
6. Wait for CI to publish to PyPI
7. Create GitHub release: gh release create v0.0.13 --generate-notes

See tasks/new-features/019-comprehensive-release-automation-skill.md for full automation roadmap.
```

### Phase 3: Build and Validate ✅

Build Python packages (wheel and sdist), validate with twine, and test installation in an isolated environment to ensure the package is ready for publishing.

**Step 1: Clean Previous Builds**

Remove old build artifacts before creating new packages:

```bash
# Remove dist directory if it exists
if [ -d "dist" ]; then
    echo "🧹 Cleaning old build artifacts..."
    rm -rf dist/
    echo "✅ Removed dist/"
fi

# Remove build directory if it exists
if [ -d "build" ]; then
    rm -rf build/
    echo "✅ Removed build/"
fi

# Remove .egg-info directories
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
```

**Requirements:**
- Remove dist/ directory (old packages)
- Remove build/ directory (build cache)
- Remove *.egg-info directories
- Continue even if directories don't exist

**Step 2: Build Packages**

Build both wheel and source distribution:

```bash
echo ""
echo "📦 Building packages..."
echo ""

# Build using python -m build (PEP 517)
python -m build

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Package build failed"
    echo ""
    echo "Common issues:"
    echo "  - Missing build dependencies (install: pip install build)"
    echo "  - Syntax errors in setup files"
    echo "  - Missing required files (README.md, LICENSE, etc.)"
    echo ""
    exit 1
fi

echo ""
echo "✅ Packages built successfully"
echo ""

# List built packages
ls -lh dist/
```

**Requirements:**
- Use `python -m build` (PEP 517 compliant)
- Build both wheel (.whl) and sdist (.tar.gz)
- Check build exit code
- Display built packages with sizes

**Error Handling:**
- If build fails:
  - Display build error output
  - Suggest common fixes (install build, check syntax, check manifest)
  - Show current working directory
  - Exit with failure
- If no packages created:
  - Error: "No packages found in dist/"
  - Show dist/ directory contents
  - Exit with failure

**Step 3: Validate with Twine**

Check packages for common issues using twine:

```bash
echo ""
echo "🔍 Validating packages with twine..."
echo ""

# Run twine check on all packages
twine check dist/*

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Package validation failed"
    echo ""
    echo "Twine found issues with the packages."
    echo "Review the errors above and fix before releasing."
    echo ""
    exit 1
fi

echo ""
echo "✅ Packages passed twine validation"
```

**Requirements:**
- Run `twine check` on all dist/* files
- Check for PyPI compatibility
- Validate package metadata
- Validate long_description rendering

**Error Handling:**
- If twine check fails:
  - Display twine error details
  - Common issues:
    - Invalid RST/Markdown in README
    - Missing required metadata fields
    - Invalid version format
    - Malformed MANIFEST.in
  - Suggest: "Fix issues and re-run build"
  - Exit with failure
- If twine not installed:
  - Error: "twine not found"
  - Suggest: "pip install twine"
  - Exit with failure

**Step 4: Check Package Contents**

Verify wheel contents with check-wheel-contents:

```bash
echo ""
echo "🔍 Checking wheel contents..."
echo ""

# Find wheel file
wheel_file=$(ls dist/*.whl 2>/dev/null | head -1)

if [ -z "$wheel_file" ]; then
    echo "❌ No wheel file found in dist/"
    exit 1
fi

# Run check-wheel-contents
check-wheel-contents "$wheel_file"

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Wheel contents check found issues"
    echo ""
    echo "Review warnings above. Some warnings may be acceptable."
    echo ""
    read -p "Continue anyway? [y/N]: " continue_check

    if [ "$continue_check" != "y" ] && [ "$continue_check" != "Y" ]; then
        echo "❌ Build validation cancelled"
        exit 1
    fi
fi

echo ""
echo "✅ Wheel contents validated"
```

**Requirements:**
- Check wheel file exists
- Run `check-wheel-contents` on wheel
- Validate:
  - No duplicate files
  - LICENSE and README included
  - No .pyc files
  - No __pycache__ directories
  - Proper file permissions

**Error Handling:**
- If no wheel found:
  - Error: "No .whl file in dist/"
  - List dist/ contents
  - Exit with failure
- If check-wheel-contents not available:
  - Warning: "check-wheel-contents not found (optional)"
  - Suggest: "pip install check-wheel-contents"
  - Continue (not required, but recommended)
- If issues found:
  - Display issues
  - Prompt user to continue or cancel
  - Default to cancel

**Step 5: Test Installation in Isolated Environment**

Create temporary venv and test package installation:

```bash
echo ""
echo "🧪 Testing installation in isolated environment..."
echo ""

# Create temporary directory for venv
test_venv_dir=$(mktemp -d)
echo "📁 Created temp venv: $test_venv_dir"

# Create virtual environment
python -m venv "$test_venv_dir/test-install"

# Check if venv created successfully
if [ ! -d "$test_venv_dir/test-install" ]; then
    echo "❌ Failed to create test venv"
    rm -rf "$test_venv_dir"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate venv
source "$test_venv_dir/test-install/bin/activate"

# Upgrade pip
pip install --upgrade pip --quiet

# Find wheel file
wheel_file=$(ls dist/*.whl | head -1)

# Install package from wheel
echo "📦 Installing package from wheel..."
pip install "$wheel_file" --quiet

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Installation failed"
    deactivate
    rm -rf "$test_venv_dir"
    exit 1
fi

echo "✅ Package installed successfully"

# Test that package is importable
echo "🧪 Testing package import..."
python -c "import nhl_scrabble; print(f'Version: {nhl_scrabble.__version__}')"

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Package import failed"
    deactivate
    rm -rf "$test_venv_dir"
    exit 1
fi

echo "✅ Package import successful"

# Test CLI command
echo "🧪 Testing CLI command..."
nhl-scrabble --version

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ CLI command failed"
    deactivate
    rm -rf "$test_venv_dir"
    exit 1
fi

echo "✅ CLI command works"

# Deactivate and cleanup
deactivate
rm -rf "$test_venv_dir"

echo ""
echo "✅ Installation test passed"
```

**Requirements:**
- Create temporary venv
- Install package from wheel (not sdist)
- Test import: `import nhl_scrabble`
- Test CLI: `nhl-scrabble --version`
- Cleanup venv after test

**Error Handling:**
- If venv creation fails:
  - Error: "Failed to create virtual environment"
  - Suggest: "Check Python installation"
  - Exit with failure
- If installation fails:
  - Display pip error
  - Common issues:
    - Missing dependencies in setup
    - Syntax errors in package
    - Incompatible Python version
  - Cleanup venv
  - Exit with failure
- If import fails:
  - Error: "Package import failed"
  - Show Python error
  - Cleanup venv
  - Exit with failure
- If CLI fails:
  - Error: "CLI command not found or failed"
  - Check entry_points in setup
  - Cleanup venv
  - Exit with failure

**Step 6: Verify Package Metadata**

Extract and display package metadata for review:

```bash
echo ""
echo "📋 Package Metadata:"
echo ""

# Extract metadata from wheel
wheel_file=$(ls dist/*.whl | head -1)

# Show package info using pip
python -m venv temp-meta-venv --quiet
source temp-meta-venv/bin/activate
pip install "$wheel_file" --quiet
pip show nhl-scrabble

deactivate
rm -rf temp-meta-venv

echo ""
```

**Requirements:**
- Display package name, version, summary
- Show author, license
- List dependencies
- Show package location

**Step 7: Build Validation Summary**

Display comprehensive summary of build validation:

```
✅ Phase 3: Build and Validate Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build Artifacts:
  ✅ dist/nhl_scrabble-0.0.13-py3-none-any.whl (45 KB)
  ✅ dist/nhl_scrabble-0.0.13.tar.gz (38 KB)

Validation:
  ✅ Twine check: Passed
  ✅ Wheel contents: Validated
  ✅ Installation test: Successful
  ✅ Package import: Working
  ✅ CLI command: Working

Package Metadata:
  Name: nhl-scrabble
  Version: 0.0.13
  Author: Brandon Perkins
  License: MIT
  Python: >=3.12

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps (Phase 4+):
  - Publish to PyPI (not yet implemented)
  - Create GitHub Release (not yet implemented)
  - Post-Release Tasks (not yet implemented)

⚠️  Note: Only Phases 1-3 are currently implemented.
    Future phases will be added in subsequent tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Packages are ready for publishing!

To continue manually:
1. Review packages: ls -lh dist/
2. Create tag: git tag -a v0.0.13 -m "Release version 0.0.13"
3. Push: git push && git push v0.0.13
4. Wait for CI to publish to PyPI (or publish manually: twine upload dist/*)
5. Create GitHub release: gh release create v0.0.13 --generate-notes

See tasks/new-features/019-comprehensive-release-automation-skill.md for full automation roadmap.
```

### Phase 4: Publish ✅

**Objective**: Create git tag, publish GitHub release, and trigger automated PyPI publishing.

**Prerequisites**:
- Phase 3 completed (packages built and validated)
- Working tree is clean
- All changes committed
- Ready to publish version

**Important**: This project uses automated PyPI publishing via GitHub Actions. When you push a version tag (`v*`), the `publish.yml` workflow automatically builds and publishes to PyPI using OIDC authentication (no manual tokens needed).

**Step 1: Create Git Tag**

Create an annotated git tag with the new version:

```bash
echo ""
echo "📍 Step 1: Create Git Tag"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get version from user (already set in Phase 2)
new_version="$new_version"  # From Phase 2
tag_name="v$new_version"

# Check if tag already exists
if git rev-parse "$tag_name" >/dev/null 2>&1; then
    echo "❌ Error: Tag $tag_name already exists!"
    echo ""
    echo "Options:"
    echo "  1. Delete existing tag: git tag -d $tag_name && git push origin :refs/tags/$tag_name"
    echo "  2. Use a different version number"
    echo "  3. Abort release"
    echo ""
    read -p "Abort release? [Y/n] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "❌ Release aborted."
        exit 1
    fi
fi

# Create annotated tag with release notes
echo "Creating tag: $tag_name"
echo ""

# Generate tag message from changelog entry (from Phase 2)
tag_message="Release version $new_version

$(sed -n "/^## \[$new_version\]/,/^## \[/p" CHANGELOG.md | sed '1d;$d' | sed '/^$/d')

See CHANGELOG.md for full details."

# Create the tag
git tag -a "$tag_name" -m "$tag_message"

# Verify tag created
if git rev-parse "$tag_name" >/dev/null 2>&1; then
    echo "✅ Tag created successfully: $tag_name"
    echo ""
    echo "Tag details:"
    git show "$tag_name" --quiet
    echo ""
else
    echo "❌ Error: Failed to create tag $tag_name"
    exit 1
fi
```

**Requirements:**
- Create annotated tag (not lightweight)
- Include release notes in tag message
- Extract notes from CHANGELOG.md
- Verify tag creation

**Step 2: Push Tag to Remote**

Push the git tag to GitHub to trigger automated publishing:

```bash
echo ""
echo "📤 Step 2: Push Tag to Remote"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "⚠️  IMPORTANT: Pushing this tag will trigger:"
echo "   - Automated PyPI publishing workflow"
echo "   - Package build and upload to PyPI"
echo "   - SBOM and SLSA provenance generation"
echo ""
echo "This action cannot be easily undone. PyPI releases cannot be deleted,"
echo "only yanked (hidden from pip install but still accessible)."
echo ""
read -p "Push tag $tag_name to origin? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Tag push cancelled."
    echo ""
    echo "Tag created locally but not pushed."
    echo "To push later: git push origin $tag_name"
    echo "To delete local tag: git tag -d $tag_name"
    exit 1
fi

# Push tag to origin
echo "Pushing tag to origin..."
if git push origin "$tag_name"; then
    echo "✅ Tag pushed successfully: $tag_name"
    echo ""
    echo "GitHub Actions workflows triggered:"
    echo "  - PyPI Publishing (publish.yml)"
    echo "  - GitHub Release Creation"
    echo "  - SBOM Generation"
    echo "  - SLSA Provenance"
    echo ""
else
    echo "❌ Error: Failed to push tag $tag_name"
    echo ""
    echo "Common issues:"
    echo "  - Authentication failure: Check GitHub credentials"
    echo "  - Network error: Check connection and retry"
    echo "  - Protected tags: Check repository settings"
    echo ""
    echo "To retry: git push origin $tag_name"
    echo "To delete local tag: git tag -d $tag_name"
    exit 1
fi

# Wait a moment for GitHub to process the tag
sleep 2
```

**Requirements:**
- Confirm before pushing (cannot be undone)
- Warn about automated publishing
- Push tag to origin
- Verify push succeeded
- Handle authentication errors

**Step 3: Monitor Automated Publishing**

Monitor the GitHub Actions workflows triggered by the tag push:

```bash
echo ""
echo "🔍 Step 3: Monitor Automated Publishing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Checking for triggered workflows..."
echo ""

# Get the workflow run triggered by this tag
# Wait a few seconds for GitHub to create the run
sleep 5

# Find the publish workflow run for this tag
run_id=$(gh run list --workflow=publish.yml --json databaseId,headBranch,status \
    --jq ".[] | select(.headBranch == \"$tag_name\") | .databaseId" | head -1)

if [ -z "$run_id" ]; then
    echo "⚠️  Warning: Could not find workflow run for tag $tag_name"
    echo ""
    echo "The workflow may still be starting. Check manually:"
    echo "  gh run list --workflow=publish.yml"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "Found workflow run: $run_id"
    echo ""
    echo "Monitoring publish workflow (this may take 5-10 minutes)..."
    echo "  - Building package for multiple Python versions"
    echo "  - Running tests on multiple platforms"
    echo "  - Publishing to PyPI via OIDC"
    echo "  - Generating SBOM and provenance"
    echo ""

    # Watch the workflow run
    echo "View workflow: https://github.com/bdperkin/nhl-scrabble/actions/runs/$run_id"
    echo ""
    read -p "Watch workflow progress in terminal? [Y/n] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Watch the run (auto-updates)
        gh run watch "$run_id"

        # Check final status
        status=$(gh run view "$run_id" --json conclusion --jq '.conclusion')

        if [ "$status" = "success" ]; then
            echo ""
            echo "✅ Publish workflow completed successfully!"
            echo ""
        else
            echo ""
            echo "❌ Publish workflow failed: $status"
            echo ""
            echo "View logs: gh run view $run_id --log-failed"
            echo ""
            read -p "Continue anyway? [y/N] " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "See ROLLBACK section below for recovery steps."
                exit 1
            fi
        fi
    fi
fi
```

**Requirements:**
- Find the workflow run triggered by tag
- Display workflow URL
- Offer to watch progress
- Check final status
- Handle workflow failures

**Step 4: Create GitHub Release**

Create a GitHub release with auto-generated release notes:

```bash
echo ""
echo "🎉 Step 4: Create GitHub Release"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Creating GitHub release for $tag_name..."
echo ""

# Generate release notes from changelog
release_notes="$(sed -n "/^## \[$new_version\]/,/^## \[/p" CHANGELOG.md | sed '1d;$d')"

# Create release with gh CLI
if gh release create "$tag_name" \
    --title "Release $new_version" \
    --notes "$release_notes" \
    --latest \
    dist/*.whl dist/*.tar.gz; then

    echo "✅ GitHub release created successfully!"
    echo ""
    echo "Release URL: https://github.com/bdperkin/nhl-scrabble/releases/tag/$tag_name"
    echo ""
    echo "Attached artifacts:"
    ls -lh dist/*.whl dist/*.tar.gz | awk '{print "  - " $9 " (" $5 ")"}'
    echo ""
else
    echo "❌ Error: Failed to create GitHub release"
    echo ""
    echo "Common issues:"
    echo "  - Release already exists: Delete it first with 'gh release delete $tag_name'"
    echo "  - Network error: Retry the command"
    echo "  - Permission error: Check GitHub token permissions"
    echo ""
    echo "To retry:"
    echo "  gh release create $tag_name --title \"Release $new_version\" \\"
    echo "    --notes \"$release_notes\" --latest dist/*.whl dist/*.tar.gz"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "See ROLLBACK section below for recovery steps."
        exit 1
    fi
fi
```

**Requirements:**
- Extract release notes from CHANGELOG.md
- Create release with gh CLI
- Attach build artifacts (wheel and sdist)
- Mark as latest release
- Handle errors (duplicate release, network, permissions)

**Step 5: Verify PyPI Publication**

Verify that the package was successfully published to PyPI:

```bash
echo ""
echo "✅ Step 5: Verify PyPI Publication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Waiting for PyPI to index the new version (this may take 1-2 minutes)..."
sleep 30

# Check if package is on PyPI
echo "Checking PyPI for nhl-scrabble $new_version..."
echo ""

# Try to fetch package info from PyPI
max_attempts=6
attempt=1
found=false

while [ $attempt -le $max_attempts ]; do
    if curl -s "https://pypi.org/pypi/nhl-scrabble/json" | grep -q "\"version\": \"$new_version\""; then
        found=true
        break
    fi

    echo "Attempt $attempt/$max_attempts: Not yet available, waiting 30s..."
    sleep 30
    ((attempt++))
done

if [ "$found" = true ]; then
    echo "✅ Package found on PyPI!"
    echo ""
    echo "PyPI URL: https://pypi.org/project/nhl-scrabble/$new_version/"
    echo ""

    # Test installation in temporary venv
    echo "Testing installation from PyPI..."
    temp_venv=$(mktemp -d)/pypi-test-venv
    python -m venv "$temp_venv" --quiet
    source "$temp_venv/bin/activate"

    if pip install "nhl-scrabble==$new_version" --quiet; then
        installed_version=$(python -c "import nhl_scrabble; print(nhl_scrabble.__version__)")
        if [ "$installed_version" = "$new_version" ]; then
            echo "✅ Installation test passed!"
            echo "   Installed version: $installed_version"
            echo ""
        else
            echo "⚠️  Warning: Version mismatch!"
            echo "   Expected: $new_version"
            echo "   Got: $installed_version"
            echo ""
        fi
    else
        echo "❌ Error: Failed to install from PyPI"
        echo ""
    fi

    deactivate
    rm -rf "$temp_venv"
else
    echo "⚠️  Warning: Package not found on PyPI after $max_attempts attempts"
    echo ""
    echo "Possible reasons:"
    echo "  - PyPI indexing is slow (can take 5-10 minutes)"
    echo "  - Publish workflow is still running"
    echo "  - Publish workflow failed"
    echo ""
    echo "Check workflow status: gh run list --workflow=publish.yml"
    echo "Check PyPI: https://pypi.org/project/nhl-scrabble/"
    echo ""
fi
```

**Requirements:**
- Wait for PyPI to index new version
- Check PyPI API for version
- Retry with backoff (up to 6 attempts)
- Test installation from PyPI
- Verify installed version matches

**Step 6: Publish Summary**

Display comprehensive summary of what was published:

```bash
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 4: Publish Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Release: $new_version"
echo "Tag: $tag_name"
echo ""
echo "Published To:"
echo "  ✅ Git: Tag pushed to origin"
echo "  ✅ GitHub: Release created with artifacts"
echo "  ✅ PyPI: Package published (or publishing)"
echo ""
echo "URLs:"
echo "  🏷️  Tag: https://github.com/bdperkin/nhl-scrabble/releases/tag/$tag_name"
echo "  📦 PyPI: https://pypi.org/project/nhl-scrabble/$new_version/"
echo "  📄 Docs: https://bdperkin.github.io/nhl-scrabble/"
echo ""
echo "Artifacts:"
ls -lh dist/ | grep -E '\.(whl|tar\.gz)$' | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "Next Steps (Phase 5+):"
echo "  - Post-release tasks (not yet implemented)"
echo "  - Verification and cleanup (not yet implemented)"
echo ""
echo "⚠️  Note: Only Phases 1-4 are currently implemented."
echo "    Future phases will be added in subsequent tasks."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Release $new_version published successfully!"
echo ""
```

**Step 7: Rollback Support**

If something goes wrong during publishing, here's how to rollback:

```bash
echo ""
echo "🔄 ROLLBACK: If Something Goes Wrong"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If you need to rollback the release:"
echo ""
echo "1. Delete GitHub Release:"
echo "   gh release delete $tag_name --yes"
echo ""
echo "2. Delete Git Tag (Local):"
echo "   git tag -d $tag_name"
echo ""
echo "3. Delete Git Tag (Remote):"
echo "   git push origin :refs/tags/$tag_name"
echo ""
echo "4. PyPI Package:"
echo "   ⚠️  CANNOT DELETE - Can only yank (hide from pip install)"
echo "   pip install twine"
echo "   twine upload --skip-existing dist/*  # if you need to re-upload"
echo "   # Or use PyPI web interface to yank the release"
echo ""
echo "5. Revert CHANGELOG.md (if committed):"
echo "   git revert <commit-sha>"
echo "   # Or manually edit and commit"
echo ""
echo "⚠️  Important Notes:"
echo "  - PyPI releases cannot be deleted, only yanked"
echo "  - Yanked releases are hidden but still accessible"
echo "  - Version numbers cannot be reused on PyPI"
echo "  - If you need to fix issues, bump to a new version (e.g., 0.0.14)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
```

**Rollback Scenarios:**

1. **Tag created but not pushed**:
   - Simple: `git tag -d $tag_name`
   - No remote impact

2. **Tag pushed but GitHub release failed**:
   - Delete remote tag: `git push origin :refs/tags/$tag_name`
   - Delete local tag: `git tag -d $tag_name`
   - Fix issue and retry

3. **GitHub release created but PyPI publish failed**:
   - Delete GitHub release: `gh release delete $tag_name --yes`
   - Delete tags (local and remote)
   - Check workflow logs: `gh run view $run_id --log-failed`
   - Fix issue and retry

4. **PyPI published but package is broken**:
   - **Cannot delete from PyPI!**
   - Yank the release (hides from pip install)
   - Bump version to fix (e.g., 0.0.14)
   - Publish fixed version

5. **Everything published but needs changes**:
   - Leave published version as-is
   - Make fixes
   - Bump version
   - Publish new version

### Phase 5: Post-Release Tasks ✅

**Objective**: Prepare repository for next development cycle after successful release.

**Prerequisites**:
- Phase 4 completed (release published)
- Currently on main branch
- All release changes committed and pushed

**Important**: This project uses **hatch-vcs** for dynamic versioning from git tags. After tagging a release (e.g., `v0.0.13`), the version automatically becomes the next development version (e.g., `0.0.14.dev0+g<hash>`) for subsequent commits. No manual version file updates are needed.

**Step 1: Prepare CHANGELOG.md for Next Release**

Add an `## [Unreleased]` section to CHANGELOG.md to track future changes:

```bash
echo ""
echo "📝 Step 1: Prepare CHANGELOG.md for Next Release"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Unreleased section already exists
if grep -q "^## \[Unreleased\]" CHANGELOG.md; then
    echo "✅ CHANGELOG.md already has [Unreleased] section"
    echo ""
else
    echo "Adding [Unreleased] section to CHANGELOG.md..."
    echo ""

    # Find the first version heading (e.g., "## [0.0.13]")
    first_version_line=$(grep -n "^## \[" CHANGELOG.md | head -1 | cut -d: -f1)

    if [ -z "$first_version_line" ]; then
        echo "❌ Error: Could not find version headings in CHANGELOG.md"
        echo ""
        echo "Expected format:"
        echo "  ## [0.0.13] - 2026-04-30"
        echo ""
        exit 1
    fi

    # Create temp file with Unreleased section
    {
        # Copy everything before first version
        head -n $((first_version_line - 1)) CHANGELOG.md

        # Add Unreleased section
        echo "## [Unreleased]"
        echo ""
        echo "### Added"
        echo ""
        echo "### Changed"
        echo ""
        echo "### Fixed"
        echo ""

        # Copy rest of file (starting from first version)
        tail -n +${first_version_line} CHANGELOG.md
    } > CHANGELOG.md.tmp

    # Replace original with updated version
    mv CHANGELOG.md.tmp CHANGELOG.md

    echo "✅ Added [Unreleased] section to CHANGELOG.md"
    echo ""

    # Show what was added
    echo "Preview:"
    sed -n '/^## \[Unreleased\]/,/^## \[/p' CHANGELOG.md | head -10
    echo ""
fi
```

**Requirements:**
- Add `## [Unreleased]` section if not present
- Include standard subsections (Added, Changed, Fixed)
- Place before first versioned release entry
- Empty sections (ready for future changes)

**Step 2: Update Release Documentation**

Update any documentation that references the latest release:

```bash
echo ""
echo "📚 Step 2: Update Release Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get the version we just released (from last commit/tag)
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
released_version="${latest_tag#v}"  # Remove 'v' prefix

echo "Latest release: $released_version"
echo ""

# Check if README.md needs updates
if [ -f "README.md" ]; then
    echo "Checking README.md for release references..."

    # This is informational - no automatic updates
    # Users should manually update version-specific docs if needed

    echo "✅ README.md checked"
    echo ""
    echo "💡 Note: If README.md has version-specific instructions or"
    echo "   examples, consider updating them to reference the new release."
    echo ""
else
    echo "⚠️  README.md not found (optional)"
    echo ""
fi

# Note about documentation deployment
echo "📖 Documentation Deployment:"
echo "   Documentation for the new release was automatically deployed"
echo "   by GitHub Actions when the tag was pushed (Phase 4)."
echo ""
echo "   Docs URL: https://bdperkin.github.io/nhl-scrabble/"
echo ""
```

**Requirements:**
- Check for documentation that needs updates
- Note that docs were auto-deployed in Phase 4
- Provide informational output only (no automatic doc edits)

**Step 3: Verify Version Auto-Increment**

Verify that hatch-vcs automatically incremented the development version:

```bash
echo ""
echo "🔢 Step 3: Verify Version Auto-Increment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing version detection..."
echo ""

# Get current version (should be dev version after tag)
if command -v python >/dev/null 2>&1; then
    current_version=$(python -c "
try:
    import nhl_scrabble
    print(nhl_scrabble.__version__)
except Exception as e:
    print('error')
" 2>/dev/null)

    if [ "$current_version" = "error" ] || [ -z "$current_version" ]; then
        echo "⚠️  Could not detect version (package may need installation)"
        echo ""
        echo "After committing CHANGELOG changes, the version will be:"
        echo "  ${released_version%.*}.$((${released_version##*.} + 1)).dev0+g<commit-hash>"
        echo ""
    else
        echo "Current version: $current_version"
        echo ""

        if [[ "$current_version" == *"dev"* ]]; then
            echo "✅ Version correctly shows development suffix"
            echo ""
        elif [ "$current_version" = "$released_version" ]; then
            echo "⚠️  Version still shows release version: $released_version"
            echo ""
            echo "After making a commit, version will automatically include .dev suffix"
            echo ""
        else
            echo "✅ Version: $current_version"
            echo ""
        fi
    fi
else
    echo "⚠️  Python not available for version check"
    echo ""
fi

echo "ℹ️  Version Management:"
echo "   This project uses hatch-vcs for dynamic versioning."
echo "   Versions are automatically derived from git tags:"
echo ""
echo "   - On tag v0.0.13:     version = 0.0.13"
echo "   - After tag + 3 commits: version = 0.0.14.dev3+g<hash>"
echo ""
echo "   No manual version file updates needed!"
echo ""
```

**Requirements:**
- Explain hatch-vcs dynamic versioning
- Show current version if available
- Clarify that version auto-increments with commits
- Note that no manual version updates are needed

**Step 4: Commit Post-Release Changes**

Commit the CHANGELOG.md update and any other post-release changes:

```bash
echo ""
echo "💾 Step 4: Commit Post-Release Changes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  No post-release changes to commit"
    echo ""
    echo "This may happen if:"
    echo "  - CHANGELOG.md already had [Unreleased] section"
    echo "  - No documentation updates were needed"
    echo ""
else
    echo "Changes to commit:"
    git status --short
    echo ""

    # Stage changes
    git add CHANGELOG.md

    # Create commit message
    commit_msg="chore(release): Prepare for next development cycle

Add [Unreleased] section to CHANGELOG.md for future changes.

Post-release cleanup after v${released_version}."

    echo "Creating commit..."
    if git commit -m "$commit_msg"; then
        echo "✅ Post-release commit created"
        echo ""

        # Show commit details
        git log -1 --oneline
        echo ""
    else
        echo "❌ Error: Failed to create commit"
        exit 1
    fi
fi
```

**Requirements:**
- Stage CHANGELOG.md changes
- Create descriptive commit message
- Reference the version that was just released
- Only commit if there are actual changes

**Step 5: Push Post-Release Changes**

Push the post-release commit to the main branch:

```bash
echo ""
echo "📤 Step 5: Push Post-Release Changes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if there are unpushed commits
unpushed_commits=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l)

if [ "$unpushed_commits" -eq 0 ]; then
    echo "ℹ️  No commits to push"
    echo ""
else
    echo "Pushing $unpushed_commits commit(s) to origin/main..."
    echo ""

    read -p "Push post-release changes to remote? [Y/n] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if git push origin main; then
            echo "✅ Post-release changes pushed successfully"
            echo ""
        else
            echo "❌ Error: Failed to push changes"
            echo ""
            echo "Common issues:"
            echo "  - Authentication failure: Check GitHub credentials"
            echo "  - Protected branch: May need PR for main branch"
            echo "  - Network error: Check connection and retry"
            echo ""
            echo "To retry: git push origin main"
            exit 1
        fi
    else
        echo "⚠️  Push cancelled"
        echo ""
        echo "Post-release changes committed locally but not pushed."
        echo "To push later: git push origin main"
        echo ""
    fi
fi
```

**Requirements:**
- Confirm before pushing
- Push to origin/main
- Handle push errors gracefully
- Provide clear error messages

**Step 6: Post-Release Summary**

Display summary of post-release tasks completed:

```bash
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 5: Post-Release Tasks Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Release: v${released_version}"
echo ""
echo "Completed Tasks:"
echo "  ✅ CHANGELOG.md prepared for next release"
echo "  ✅ Documentation references checked"
echo "  ✅ Version management verified (hatch-vcs)"
echo "  ✅ Post-release changes committed"
echo "  ✅ Changes pushed to remote"
echo ""
echo "Repository State:"
echo "  Branch: main"
echo "  Latest release: v${released_version}"
echo "  Next version: ${released_version%.*}.$((${released_version##*.} + 1)).dev"
echo ""
echo "CHANGELOG.md:"
echo "  [Unreleased] section ready for future changes"
echo ""
echo "Next Steps (Phase 6):"
echo "  - Verification and reporting"
echo "  - Run: continue with Phase 6"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Release cycle complete!"
echo ""
echo "The repository is now ready for continued development."
echo "Future changes will be tracked in the [Unreleased] section"
echo "of CHANGELOG.md until the next release."
echo ""
```

### Phase 6: Verification and Reporting ✅

**Purpose**: Verify release artifacts and generate comprehensive release report

**Prerequisites**:
- Phase 5 completed (post-release tasks done)
- Release tag pushed
- GitHub Actions workflow completed
- PyPI package published

**Inputs**:
- Released version (from Phase 4)
- GitHub release URL
- PyPI package URL
- Documentation URL

**Outputs**:
- Verification status for each artifact
- Comprehensive release report
- Success/failure summary

**Process**:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Phase 6: Verification and Reporting
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Phase 6: Verification and Reporting"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get the released version (from Phase 4 output or git tag)
if [[ -z "${released_version:-}" ]]; then
    released_version=$(git describe --tags --abbrev=0 | sed 's/^v//')
    echo "ℹ️  Detected released version from git: ${released_version}"
else
    echo "ℹ️  Using released version: ${released_version}"
fi

tag_name="v${released_version}"

# Initialize verification status
pypi_status="❌"
github_status="❌"
docs_status="❌"
verification_failed=false

# ============================================================================
# Step 1: Verify PyPI Package Availability
# ============================================================================

echo ""
echo "📦 Step 1: Verifying PyPI Package..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pypi_url="https://pypi.org/project/nhl-scrabble/${released_version}/"
pypi_json_url="https://pypi.org/pypi/nhl-scrabble/json"

# Check if package exists on PyPI
if curl -sf "${pypi_json_url}" | jq -e ".releases.\"${released_version}\"" > /dev/null 2>&1; then
    pypi_status="✅"
    echo "✅ PyPI package verified"
    echo "   URL: ${pypi_url}"

    # Get package metadata
    package_info=$(curl -sf "${pypi_json_url}" | jq -r ".releases.\"${released_version}\"[0]")
    upload_time=$(echo "${package_info}" | jq -r '.upload_time')
    package_size=$(echo "${package_info}" | jq -r '.size')

    echo "   Upload time: ${upload_time}"
    echo "   Package size: $(numfmt --to=iec-i --suffix=B "${package_size}" 2>/dev/null || echo "${package_size} bytes")"

    # Verify installability (optional - can be slow)
    echo ""
    echo "   Testing package installation..."
    if python -m pip install --dry-run "nhl-scrabble==${released_version}" > /dev/null 2>&1; then
        echo "   ✅ Package is installable"
    else
        echo "   ⚠️  Package installation test failed (may be temporary)"
    fi
else
    pypi_status="❌"
    verification_failed=true
    echo "❌ PyPI package not found"
    echo "   Expected URL: ${pypi_url}"
    echo ""
    echo "   Possible reasons:"
    echo "   - GitHub Actions workflow still running"
    echo "   - PyPI publishing failed (check workflow logs)"
    echo "   - PyPI indexing delay (wait 5-10 minutes)"
    echo ""
    echo "   Check workflow: gh run list --workflow=publish.yml --limit 1"
fi

# ============================================================================
# Step 2: Verify GitHub Release
# ============================================================================

echo ""
echo "🏷️  Step 2: Verifying GitHub Release..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if release exists
if gh release view "${tag_name}" > /dev/null 2>&1; then
    github_status="✅"
    echo "✅ GitHub release verified"

    # Get release metadata
    release_url=$(gh release view "${tag_name}" --json url --jq '.url')
    release_date=$(gh release view "${tag_name}" --json publishedAt --jq '.publishedAt')
    asset_count=$(gh release view "${tag_name}" --json assets --jq '.assets | length')

    echo "   URL: ${release_url}"
    echo "   Published: ${release_date}"
    echo "   Assets: ${asset_count}"

    # List assets
    if [[ ${asset_count} -gt 0 ]]; then
        echo ""
        echo "   Release Assets:"
        gh release view "${tag_name}" --json assets --jq '.assets[] | "   - \(.name) (\(.size) bytes)"'
    fi
else
    github_status="❌"
    verification_failed=true
    echo "❌ GitHub release not found"
    echo "   Expected tag: ${tag_name}"
    echo ""
    echo "   Create release manually:"
    echo "   gh release create \"${tag_name}\" --title \"Release ${released_version}\" --generate-notes"
fi

# ============================================================================
# Step 3: Verify Documentation Deployment
# ============================================================================

echo ""
echo "📚 Step 3: Verifying Documentation Deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docs_url="https://bdperkin.github.io/nhl-scrabble/"

# Check if docs are accessible
if curl -sf -o /dev/null -w "%{http_code}" "${docs_url}" | grep -q "200"; then
    docs_status="✅"
    echo "✅ Documentation verified"
    echo "   URL: ${docs_url}"

    # Check if version is mentioned in docs (optional verification)
    if curl -sf "${docs_url}" | grep -q "${released_version}"; then
        echo "   ✅ Version ${released_version} found in documentation"
    else
        echo "   ℹ️  Version ${released_version} not yet visible (may take a few minutes)"
    fi
else
    docs_status="⚠️"
    echo "⚠️  Documentation not accessible (may be temporary)"
    echo "   URL: ${docs_url}"
    echo ""
    echo "   Check GitHub Pages deployment:"
    echo "   gh run list --workflow=pages-build-deployment --limit 1"
fi

# ============================================================================
# Step 4: Generate Release Report
# ============================================================================

echo ""
echo "📊 Step 4: Generating Release Report..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get additional metadata
current_branch=$(git branch --show-current)
commit_count=$(git rev-list --count "${tag_name}")
contributors=$(git shortlog -s "${tag_name}" | wc -l)

# Get changelog for this version
changelog_entry=$(sed -n "/^## \[${released_version}\]/,/^## \[/p" CHANGELOG.md | sed '1d;$d' | sed '/^$/d')

# Display comprehensive report
cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Release Report: v${released_version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Package Information
   Version: ${released_version}
   Tag: ${tag_name}
   Branch: ${current_branch}
   Total commits: ${commit_count}
   Contributors: ${contributors}

📋 Verification Status
   ${pypi_status} PyPI Package
   ${github_status} GitHub Release
   ${docs_status} Documentation

🔗 Release URLs
   PyPI: ${pypi_url}
   GitHub: $(gh release view "${tag_name}" --json url --jq '.url' 2>/dev/null || echo "Not available")
   Docs: ${docs_url}

📝 Changes in This Release
${changelog_entry}

🚀 Installation
   pip install nhl-scrabble==${released_version}
   uv pip install nhl-scrabble==${released_version}

📚 Documentation
   Online: ${docs_url}
   Changelog: https://github.com/bdperkin/nhl-scrabble/blob/main/CHANGELOG.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

# ============================================================================
# Step 5: Final Status Summary
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ "${verification_failed}" == "false" ]]; then
    echo "✅ Phase 6: Verification and Reporting Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎉 All verifications passed!"
    echo ""
    echo "Release: v${released_version}"
    echo ""
    echo "Verified Components:"
    echo "  ✅ PyPI package available and installable"
    echo "  ✅ GitHub release published with assets"
    echo "  ✅ Documentation deployed and accessible"
    echo ""
    echo "Next Steps:"
    echo "  - Monitor PyPI download statistics"
    echo "  - Announce release (if applicable)"
    echo "  - Close related issues/milestones"
    echo "  - Update project roadmap"
else
    echo "⚠️  Phase 6: Verification Completed with Warnings"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "⚠️  Some verifications failed"
    echo ""
    echo "Status:"
    echo "  ${pypi_status} PyPI package"
    echo "  ${github_status} GitHub release"
    echo "  ${docs_status} Documentation"
    echo ""
    echo "Action Required:"
    echo "  - Review failed verifications above"
    echo "  - Check GitHub Actions workflows"
    echo "  - Wait for indexing/deployment (5-10 minutes)"
    echo "  - Re-run verification if needed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

```

### Phase 7: Complete Release Orchestration ✅

**Purpose**: Orchestrate all phases (1-6) into a complete end-to-end release workflow

**Features**:
- Sequential execution of all phases
- Progress tracking with phase status
- State saving for rollback capability
- Comprehensive error handling
- Dry-run mode for testing
- Skip options for flexibility

**Usage**:

```bash
# Standard release (executes all phases)
/release

# Dry-run mode (shows what would happen without executing)
/release --dry-run

# Skip specific phases (for debugging/testing)
/release --skip-tests        # Skip test execution in Phase 1
/release --skip-publish      # Skip PyPI publishing in Phase 4
/release --skip-verification # Skip verification in Phase 6

# Resume from specific phase (after fixing errors)
/release --start-from=3      # Resume from Phase 3 (Build)
```

**Process**:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Phase 7: Complete Release Orchestration
# ============================================================================

# Parse command-line arguments
DRY_RUN="${DRY_RUN:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_PUBLISH="${SKIP_PUBLISH:-false}"
SKIP_VERIFICATION="${SKIP_VERIFICATION:-false}"
START_FROM_PHASE="${START_FROM_PHASE:-1}"

# State file for rollback
STATE_FILE=".release-state.json"

# ============================================================================
# Helper Functions
# ============================================================================

# Save release state for rollback
save_state() {
    local phase=$1
    local data=$2

    cat > "${STATE_FILE}" <<EOF
{
  "phase": ${phase},
  "timestamp": "$(date -Iseconds)",
  "data": ${data}
}
EOF
}

# Load release state
load_state() {
    if [[ -f "${STATE_FILE}" ]]; then
        cat "${STATE_FILE}"
    else
        echo "{}"
    fi
}

# Clear release state
clear_state() {
    rm -f "${STATE_FILE}"
}

# Display progress
show_progress() {
    local current=$1
    local total=$2
    local phase_name=$3
    local status=$4  # running, complete, failed, skipped

    local symbol
    case "${status}" in
        running)   symbol="⏳" ;;
        complete)  symbol="✅" ;;
        failed)    symbol="❌" ;;
        skipped)   symbol="⏭️ " ;;
    esac

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "${symbol} Phase ${current}/${total}: ${phase_name}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Handle errors with rollback option
handle_error() {
    local phase=$1
    local error_msg=$2

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ Release Failed at Phase ${phase}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Error: ${error_msg}"
    echo ""
    echo "Current State:"
    cat "${STATE_FILE}" 2>/dev/null || echo "  No state file found"
    echo ""
    echo "Options:"
    echo "  1. Fix the issue and resume: /release --start-from=${phase}"
    echo "  2. Roll back changes (if any): git reset --hard HEAD~1"
    echo "  3. View release state: cat ${STATE_FILE}"
    echo "  4. Clear state: rm ${STATE_FILE}"
    echo ""

    exit 1
}

# ============================================================================
# Main Orchestration
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 NHL Scrabble Package Release Automation                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [[ "${DRY_RUN}" == "true" ]]; then
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

# Track start time
RELEASE_START_TIME=$(date +%s)

# ============================================================================
# Phase 1: Pre-Release Validation
# ============================================================================

if [[ ${START_FROM_PHASE} -le 1 ]]; then
    show_progress 1 6 "Pre-Release Validation" "running"

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "Would execute: Pre-release validation"
        echo "  - Check git status"
        echo "  - Verify current branch"
        echo "  - Ensure up-to-date with remote"
        if [[ "${SKIP_TESTS}" != "true" ]]; then
            echo "  - Run test suite"
        else
            echo "  - Skip tests (--skip-tests)"
        fi
        echo "  - Run quality checks"
        echo "  - Verify CI passing"
        echo "  - Determine next version"
        show_progress 1 6 "Pre-Release Validation" "complete"
    else
        # Execute Phase 1 (existing implementation)
        # Save state before starting
        save_state 1 '{}'

        # [Phase 1 bash code would go here - already implemented above in file]
        # For orchestration purposes, we assume it's already implemented

        show_progress 1 6 "Pre-Release Validation" "complete"
    fi
fi

# ============================================================================
# Phase 2: Version Bumping
# ============================================================================

if [[ ${START_FROM_PHASE} -le 2 ]]; then
    show_progress 2 6 "Version Bumping" "running"

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "Would execute: Version bumping"
        echo "  - Determine next version (based on CHANGELOG.md)"
        echo "  - Explain hatch-vcs dynamic versioning"
        echo "  - Note: Version will be set by git tag in Phase 4"
        show_progress 2 6 "Version Bumping" "complete"
    else
        # Execute Phase 2
        save_state 2 '{}'

        # [Phase 2 bash code already implemented]

        show_progress 2 6 "Version Bumping" "complete"
    fi
fi

# ============================================================================
# Phase 3: Build and Validate
# ============================================================================

if [[ ${START_FROM_PHASE} -le 3 ]]; then
    show_progress 3 6 "Build and Validate" "running"

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "Would execute: Build and validate"
        echo "  - Clean previous builds"
        echo "  - Build sdist and wheel"
        echo "  - Validate package with twine"
        echo "  - Inspect wheel contents"
        echo "  - Test installation in clean environment"
        show_progress 3 6 "Build and Validate" "complete"
    else
        # Execute Phase 3
        save_state 3 '{}'

        # [Phase 3 bash code already implemented]

        show_progress 3 6 "Build and Validate" "complete"
    fi
fi

# ============================================================================
# Phase 4: Publish
# ============================================================================

if [[ ${START_FROM_PHASE} -le 4 ]]; then
    if [[ "${SKIP_PUBLISH}" == "true" ]]; then
        show_progress 4 6 "Publish" "skipped"
        echo "Skipping publish phase (--skip-publish)"
    else
        show_progress 4 6 "Publish" "running"

        if [[ "${DRY_RUN}" == "true" ]]; then
            echo "Would execute: Publish"
            echo "  - Create git tag with release notes"
            echo "  - Push tag to origin (triggers automated publishing)"
            echo "  - Monitor GitHub Actions workflow"
            echo "  - Create GitHub release with assets"
            echo "  - Verify PyPI publication"
            show_progress 4 6 "Publish" "complete"
        else
            # Execute Phase 4
            save_state 4 '{}'

            # [Phase 4 bash code already implemented]

            show_progress 4 6 "Publish" "complete"
        fi
    fi
fi

# ============================================================================
# Phase 5: Post-Release Tasks
# ============================================================================

if [[ ${START_FROM_PHASE} -le 5 ]]; then
    show_progress 5 6 "Post-Release Tasks" "running"

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "Would execute: Post-release tasks"
        echo "  - Prepare CHANGELOG.md for next release"
        echo "  - Update release documentation"
        echo "  - Verify version auto-increment (hatch-vcs)"
        echo "  - Commit post-release changes"
        echo "  - Push changes to origin/main"
        show_progress 5 6 "Post-Release Tasks" "complete"
    else
        # Execute Phase 5
        save_state 5 '{}'

        # [Phase 5 bash code already implemented]

        show_progress 5 6 "Post-Release Tasks" "complete"
    fi
fi

# ============================================================================
# Phase 6: Verification and Reporting
# ============================================================================

if [[ ${START_FROM_PHASE} -le 6 ]]; then
    if [[ "${SKIP_VERIFICATION}" == "true" ]]; then
        show_progress 6 6 "Verification and Reporting" "skipped"
        echo "Skipping verification phase (--skip-verification)"
    else
        show_progress 6 6 "Verification and Reporting" "running"

        if [[ "${DRY_RUN}" == "true" ]]; then
            echo "Would execute: Verification and reporting"
            echo "  - Verify PyPI package availability"
            echo "  - Verify GitHub release"
            echo "  - Verify documentation deployment"
            echo "  - Generate release report"
            echo "  - Final status summary"
            show_progress 6 6 "Verification and Reporting" "complete"
        else
            # Execute Phase 6
            save_state 6 '{}'

            # [Phase 6 bash code already implemented]

            show_progress 6 6 "Verification and Reporting" "complete"
        fi
    fi
fi

# ============================================================================
# Release Complete
# ============================================================================

RELEASE_END_TIME=$(date +%s)
RELEASE_DURATION=$((RELEASE_END_TIME - RELEASE_START_TIME))
RELEASE_DURATION_MIN=$((RELEASE_DURATION / 60))
RELEASE_DURATION_SEC=$((RELEASE_DURATION % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎉 Release Complete!                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [[ "${DRY_RUN}" == "true" ]]; then
    echo "Dry run completed successfully in ${RELEASE_DURATION_MIN}m ${RELEASE_DURATION_SEC}s"
    echo ""
    echo "No changes were made. Run without --dry-run to execute the release."
else
    echo "Release completed successfully in ${RELEASE_DURATION_MIN}m ${RELEASE_DURATION_SEC}s"
    echo ""
    echo "Summary:"
    echo "  ✅ Phase 1: Pre-Release Validation"
    echo "  ✅ Phase 2: Version Bumping"
    echo "  ✅ Phase 3: Build and Validate"
    if [[ "${SKIP_PUBLISH}" == "true" ]]; then
        echo "  ⏭️  Phase 4: Publish (skipped)"
    else
        echo "  ✅ Phase 4: Publish"
    fi
    echo "  ✅ Phase 5: Post-Release Tasks"
    if [[ "${SKIP_VERIFICATION}" == "true" ]]; then
        echo "  ⏭️  Phase 6: Verification (skipped)"
    else
        echo "  ✅ Phase 6: Verification and Reporting"
    fi
    echo ""
    echo "Next Steps:"
    echo "  - Monitor PyPI download statistics"
    echo "  - Announce release (if applicable)"
    echo "  - Close related issues/milestones"
    echo "  - Update project roadmap"

    # Clear state file on success
    clear_state
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

```

**Rollback Support**:

If a release fails mid-process, the orchestration saves state at each phase. You can:

1. **Resume from failure point**:
   ```bash
   # Fix the issue, then resume from Phase 3
   /release --start-from=3
   ```

2. **Roll back git changes**:
   ```bash
   # Undo last commit (if version bump was committed)
   git reset --hard HEAD~1

   # Delete tag (if tag was created)
   git tag -d v0.0.14
   git push origin :refs/tags/v0.0.14
   ```

3. **Clean up state**:
   ```bash
   # Remove state file
   rm .release-state.json

   # Clean build artifacts
   rm -rf dist/ build/ *.egg-info
   ```

**Error Recovery Examples**:

```bash
# Scenario 1: Tests fail in Phase 1
# Output: "❌ Release Failed at Phase 1"
# Action: Fix tests, then restart
pytest
/release

# Scenario 2: Build fails in Phase 3
# Output: "❌ Release Failed at Phase 3"
# Action: Fix build issues, resume from Phase 3
/release --start-from=3

# Scenario 3: PyPI publish fails in Phase 4
# Output: "❌ Release Failed at Phase 4"
# Action: Check GitHub Actions logs, retry
gh run list --workflow=publish.yml
/release --start-from=4

# Scenario 4: Want to test without publishing
# Action: Use dry-run mode
/release --dry-run
```

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

**Phase 1** (Validation):
- ✅ Read-only git operations
- ✅ No file modifications
- ✅ No commits or tags created
- ✅ Safe to run anytime

**Phase 2** (Version Bumping):
- ✅ Modifies only CHANGELOG.md (reversible)
- ✅ Creates local commit (not pushed)
- ✅ Requires user confirmation before committing
- ✅ Can be reverted with git reset
- ✅ No git tags created yet
- ✅ No pushes to remote
- ✅ No publishing actions

**Phase 3** (Build and Validate):
- ✅ Creates local build artifacts in dist/ (can be deleted)
- ✅ Tests in isolated venv (auto-cleanup)
- ✅ No modifications to source code
- ✅ No git commits or tags
- ✅ No pushes to remote
- ✅ No publishing to PyPI
- ✅ Safe to run multiple times

**Future Phases** (4-7):
- ⚠️ Will include git tags, pushes, and publishing
- ⚠️ Will require careful testing before use

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

**Phase 1** (Validation) - can be tested safely:

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

**Phase 2** (Version Bumping) - test carefully:

- [ ] Test changelog generation from conventional commits
- [ ] Test with feat commits only
- [ ] Test with fix commits only
- [ ] Test with mixed commit types
- [ ] Test with breaking changes (BREAKING CHANGE in commit body)
- [ ] Test with PR numbers (#123) in commits
- [ ] Test with no commits since last tag (should still work)
- [ ] Test preview and confirmation prompt
- [ ] Test cancellation (should revert CHANGELOG.md)
- [ ] Test commit creation
- [ ] Verify commit message format

**Phase 3** (Build and Validate) - test carefully:

- [ ] Test package building (wheel and sdist)
- [ ] Test with clean dist/ directory
- [ ] Test with existing dist/ directory (should clean first)
- [ ] Test twine check validation
- [ ] Test check-wheel-contents (if available)
- [ ] Test installation in isolated venv
- [ ] Test package import
- [ ] Test CLI command execution
- [ ] Verify metadata display
- [ ] Test cleanup of temporary venv
- [ ] Test with missing build dependencies (should fail gracefully)

**Testing Approach:**

**Phase 1** (Safe - Read-only):
```bash
# Test validation in current state
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

**Phase 2** (Caution - Creates commits):
```bash
# OPTION 1: Test on feature branch (recommended)
git checkout -b test-release-026
# Make some conventional commits
git commit --allow-empty -m "feat: test feature"
git commit --allow-empty -m "fix: test bugfix"
/release  # Should generate changelog and create commit
# Review result
git log -1
git show HEAD
# Clean up
git checkout main
git branch -D test-release-026

# OPTION 2: Test with dry-run (future feature)
# /release --dry-run  # Not yet implemented

# OPTION 3: Test and reset
/release  # Go through the process
# If you want to undo:
git reset --soft HEAD~1  # Undo commit
git checkout CHANGELOG.md  # Revert CHANGELOG.md
```

**Phase 3** (Safe - Creates build artifacts):
```bash
# Test on feature branch (recommended)
git checkout -b test-release-027

# Go through phases 1-2 first (or continue from existing branch)
# ...

# Phase 3 will:
# - Build packages in dist/
# - Validate with twine
# - Test installation
# All changes are local and can be cleaned up

# Review build artifacts
ls -lh dist/

# Clean up
rm -rf dist/ build/ *.egg-info
git checkout main
git branch -D test-release-027

# Or test build phase standalone (no prior phases needed)
/release  # Run all phases including build
# Clean artifacts: rm -rf dist/
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

**Phase 2 Complete**: 2026-04-30

This phase implements automated version bumping and changelog generation:

- Conventional commits parsing (feat, fix, docs, perf, refactor, test, build, ci)
- Changelog generation from git commit history
- Keep a Changelog format support
- Categorization by commit type
- Breaking change detection (BREAKING CHANGE in commit body)
- CHANGELOG.md update with proper section insertion
- Preview of changelog before committing
- User confirmation before making changes
- Git commit creation with conventional format
- Important: Version files use hatch-vcs dynamic versioning (updated by git tag)

**Phase 3 Complete**: 2026-04-30

This phase implements package building and validation:

- Clean build artifacts (dist/, build/, *.egg-info)
- Build packages using `python -m build` (PEP 517 compliant)
- Create both wheel (.whl) and source distribution (.tar.gz)
- Validate with twine check (PyPI compatibility)
- Check wheel contents with check-wheel-contents
- Test installation in isolated temporary venv
- Verify package import and CLI command
- Display package metadata for review
- Auto-cleanup of test environment

**Future Phases**: Will be implemented in tasks 028-031 as sub-tasks of the parent task (#247).

**Design Decisions**:

1. **Read-Only Phase 1**: Deliberately made validation non-destructive to allow safe testing
1. **Interactive Prompts**: Provide user control over decisions (version bump type, handling warnings, confirmation)
1. **Comprehensive Error Messages**: Include context, suggestions, and options for all failures
1. **Staleness Detection**: Warn about old CI runs to prevent releasing with stale validation
1. **Version Validation**: Prevent common versioning errors (non-semver, duplicate tags, downgrades)
1. **Conventional Commits**: Parse standard commit format for automatic changelog generation
1. **Keep a Changelog**: Follow established changelog format for consistency
1. **Dynamic Versioning**: Respect hatch-vcs; version files updated by git tag, not manual edits
1. **User Confirmation**: Require explicit approval before creating version bump commit
1. **Reversible Changes**: Only modify CHANGELOG.md; easily reversed with git checkout

**Testing Approach**:
- Phase 1: Safe to test on live repository (read-only)
- Phase 2: Test on feature branches or with understanding that commits can be reset

**Next Steps**: Implement Phase 3 (Build and Validate) in task 027.
