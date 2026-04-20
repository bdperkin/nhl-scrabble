# Create Comprehensive Release Automation Skill

**GitHub Issue**: #247 - https://github.com/bdperkin/nhl-scrabble/issues/247

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

8-12 hours

## Description

Create a comprehensive Claude Code custom command (`/release`) that automates and orchestrates the complete release process including version bumping, changelog updates, testing, building, publishing to PyPI, creating GitHub releases, deploying documentation, and preparing the repository for the next development cycle.

## Current State

**Fragmented Release Process:**

Currently, releasing a new version requires manual execution of many disconnected steps across multiple systems:

```bash
# Current manual release workflow (15-30 steps)

# 1. Pre-release verification
pytest
tox -p auto
make check

# 2. Version bumping
# Manually edit pyproject.toml
# Manually edit __init__.py
# Manually edit CHANGELOG.md

# 3. Documentation updates
make docs
# Deploy docs manually

# 4. Git operations
git add -A
git commit -m "Release v2.1.0"
git tag v2.1.0
git push origin main
git push --tags

# 5. Package building
python -m build
twine check dist/*

# 6. Publishing
twine upload dist/*  # PyPI

# 7. GitHub Release
gh release create v2.1.0 --generate-notes

# 8. Post-release
# Bump version to next dev version
# Update CHANGELOG for next release
# Create announcement
```

**Problems:**

1. **Manual Steps**: 15-30 manual commands across multiple tools
1. **Error-Prone**: Easy to forget steps or execute in wrong order
1. **Time-Consuming**: 30-60 minutes of focused manual work
1. **Inconsistent**: Different developers may follow different procedures
1. **No Verification**: No automated checks between steps
1. **Context Switching**: Must remember state across multiple terminal sessions
1. **Rollback Complexity**: Hard to undo if something goes wrong mid-release

**Existing Automation:**

- ✅ Task 018: GitHub Actions auto-publish on git tags
- ✅ Pre-commit hooks for code quality
- ✅ Tox environments for testing
- ❌ **NO unified release command**
- ❌ **NO interactive release wizard**
- ❌ **NO automated version bumping**
- ❌ **NO automated changelog management**
- ❌ **NO rollback mechanism**

## Proposed Solution

### Create `/release` Custom Command

Create a comprehensive Claude Code skill that orchestrates the entire release process interactively:

```bash
# Simple invocation
/release

# With options
/release --version 2.1.0 --dry-run
/release --type major  # Auto-bump major version
/release --type minor  # Auto-bump minor version
/release --type patch  # Auto-bump patch version
```

### Release Process Workflow

**Phase 1: Pre-Release Validation** (Steps 1-5)

1. **Check Working Directory**

   - Ensure no uncommitted changes
   - Ensure on main branch
   - Ensure up-to-date with origin

1. **Run Test Suite**

   - Run `tox -p auto` (all Python versions)
   - Ensure 100% test pass rate
   - Check code coverage meets threshold

1. **Run Quality Checks**

   - Run `make check` (all linters, formatters, type checkers)
   - Ensure no quality violations
   - Verify documentation builds

1. **Determine Version**

   - Read current version from pyproject.toml
   - Ask user for new version or auto-calculate
   - Validate semantic versioning format
   - Confirm version bump type (major/minor/patch)

1. **Review Changes Since Last Release**

   - `git log <last-tag>..HEAD --oneline`
   - Show commit summary
   - Identify breaking changes, features, fixes

**Phase 2: Version Bumping** (Steps 6-8)

6. **Update Version in All Files**

   - `pyproject.toml`: `version = "2.1.0"`
   - `src/nhl_scrabble/__init__.py`: `__version__ = "2.1.0"`
   - `CITATION.cff`: `version: 2.1.0` (if exists)
   - `docs/conf.py`: `release = "2.1.0"` (if Sphinx docs)

1. **Update CHANGELOG.md**

   - Move Unreleased section to new version section
   - Add release date: `## [2.1.0] - 2026-04-19`
   - Generate changelog from commits (conventional commits)
   - Ask user to review/edit changelog

1. **Commit Version Bump**

   - `git add` all version files
   - `git commit -m "Release v2.1.0"`
   - Don't push yet (allow review)

**Phase 3: Build and Validate** (Steps 9-12)

9. **Build Python Packages**

   - Clean dist directory: `rm -rf dist/`
   - Build: `python -m build`
   - Generate both wheel and sdist

1. **Validate Packages**

   - Run `twine check dist/*`
   - Run `check-wheel-contents dist/*.whl`
   - Verify LICENSE and README in wheel
   - Check package metadata

1. **Test Installation**

   - Create temporary venv
   - Install from wheel: `pip install dist/*.whl`
   - Run basic smoke test: `nhl-scrabble --version`
   - Cleanup venv

1. **Build Documentation**

   - Run `make docs`
   - Check for broken links
   - Verify version in docs

**Phase 4: Publish** (Steps 13-16)

13. **Create Git Tag**

    - `git tag -a v2.1.0 -m "Release version 2.1.0"`
    - Show tag info: `git show v2.1.0`

01. **Push to GitHub**

    - Push commits: `git push origin main`
    - Push tag: `git push origin v2.1.0`
    - Wait for CI to pass (monitor GitHub Actions)

01. **Publish to PyPI**

    - Option A: Wait for GitHub Actions (task 018)
    - Option B: Manual publish: `twine upload dist/*`
    - Verify package appears on PyPI
    - Test install: `pip install nhl-scrabble==2.1.0`

01. **Create GitHub Release**

    - `gh release create v2.1.0`
    - Use changelog as release notes
    - Attach distribution files (wheel, sdist)
    - Mark as latest release

**Phase 5: Documentation Deployment** (Steps 17-18)

17. **Deploy Documentation**

    - Push docs to GitHub Pages (if configured)
    - Or deploy to Read the Docs
    - Verify docs available at public URL

01. **Update Documentation Links**

    - Update README badges
    - Update documentation version links

**Phase 6: Post-Release** (Steps 19-22)

19. **Bump to Next Development Version**

    - Calculate next version (e.g., 2.1.0 → 2.2.0-dev)
    - Update pyproject.toml: `version = "2.2.0.dev0"`
    - Update `__init__.py`

01. **Update CHANGELOG for Next Release**

    - Add new `## [Unreleased]` section
    - Add empty subsections (Added, Changed, Fixed, etc.)

01. **Commit Development Version**

    - `git add` version files and CHANGELOG
    - `git commit -m "Bump version to 2.2.0.dev0"`
    - `git push origin main`

01. **Create Release Announcement**

    - Generate announcement text from changelog
    - Suggest posting to:
      - GitHub Discussions
      - Python Discourse (if applicable)
      - Social media (if applicable)
    - Copy announcement to clipboard

**Phase 7: Verification and Cleanup** (Steps 23-25)

23. **Verify Release Artifacts**

    - Check PyPI package page
    - Check GitHub release page
    - Check documentation deployment
    - Verify all links work

01. **Run Post-Release Tests**

    - Fresh install test: `pip install nhl-scrabble`
    - Run smoke tests
    - Check --version output

01. **Generate Release Report**

    - Summary of what was released
    - Links to all artifacts
    - Statistics (commits since last release, contributors, etc.)
    - Any issues encountered
    - Next steps

### Command Structure

```python
# .claude/commands/release.md

## title: 'Release Package'
## type: 'command'
## read_only: false

# Comprehensive release automation command

Release a new version of the package with full automation.

## Usage

/release                      # Interactive mode (asks all questions)
/release --version 2.1.0      # Specify version
/release --type patch         # Auto-bump patch version
/release --type minor         # Auto-bump minor version
/release --type major         # Auto-bump major version
/release --dry-run            # Preview without making changes
/release --skip-tests         # Skip test suite (NOT RECOMMENDED)
/release --skip-publish       # Don't publish to PyPI (create tag only)

## Process

The command executes these phases:

1. Pre-Release Validation (check git, run tests, run quality checks)
2. Version Bumping (update all version files, update changelog)
3. Build and Validate (build packages, validate, test install)
4. Publish (git tag, push, PyPI publish, GitHub release)
5. Documentation Deployment (deploy docs)
6. Post-Release (bump to dev version, update changelog)
7. Verification and Cleanup (verify artifacts, generate report)

## Safety Features

- Dry-run mode to preview all changes
- Rollback on error (git reset, delete tags)
- Confirmation prompts at key steps
- Pre-flight validation (tests must pass)
- Working directory backup before changes

## Error Handling

If any step fails:
1. Stop execution immediately
2. Show error details
3. Offer rollback options
4. Save state for manual recovery
5. Provide detailed instructions for manual completion
```

### Implementation Details

**File Structure:**

```
.claude/commands/
├── release.md                 # Main release command
└── release/                   # Supporting modules
    ├── pre_release.py         # Pre-release validation
    ├── version_bump.py        # Version bumping logic
    ├── changelog.py           # Changelog management
    ├── build.py               # Package building
    ├── publish.py             # Publishing to PyPI
    ├── github_release.py      # GitHub release creation
    ├── docs_deploy.py         # Documentation deployment
    ├── post_release.py        # Post-release tasks
    └── rollback.py            # Rollback on error
```

**Key Features:**

1. **Interactive Mode**: Ask user for confirmation at each phase
1. **Dry-Run Mode**: Show what would happen without making changes
1. **Rollback Support**: Automatic rollback on errors
1. **Progress Tracking**: Show progress through all 25 steps
1. **Detailed Logging**: Log all actions for debugging
1. **Error Recovery**: Save state and provide manual recovery instructions

### Configuration

**pyproject.toml:**

````toml
[tool.release]
# Version bump behavior
version_files = [
    "pyproject.toml",
    "src/nhl_scrabble/__init__.py",
    "CITATION.cff",
]

# Changelog settings
changelog_file = "CHANGELOG.md"
changelog_format = "keep-a-changelog"  # or "conventional-commits"

# Pre-release checks
require_tests = true
require_quality_checks = true
require_clean_working_directory = true
require_main_branch = true

# Publishing
publish_to_pypi = true
publish_to_testpypi_first = false
create_github_release = true
attach_dist_files = true

# Documentation
deploy_docs = true
docs_command = "make docs"
docs_deploy_command = "make docs-deploy"  # If custom deployment

# Post-release
bump_dev_version = true
dev_version_suffix = ".dev0"

# Announcements
announcement_template = """
## NHL Scrabble v{version} Released! 🎉

We're excited to announce the release of NHL Scrabble v{version}!

{changelog}

Install or upgrade:
```bash
pip install --upgrade nhl-scrabble
````

Full changelog: {github_release_url}
"""

````

## Implementation Steps

1. **Create Command File** (2h)

   - Create `.claude/commands/release.md`
   - Define command interface (arguments, options)
   - Document usage and examples
   - Add help text

2. **Implement Pre-Release Validation** (1h)

   - Check git status (clean, on main, up-to-date)
   - Run test suite integration
   - Run quality checks integration
   - Version determination logic

3. **Implement Version Bumping** (1.5h)

   - Parse current version from pyproject.toml
   - Calculate next version (semantic versioning)
   - Update all version files
   - Changelog update logic (manual and auto-generated)

4. **Implement Build and Validation** (1h)

   - Package building integration
   - Twine check integration
   - check-wheel-contents integration
   - Test installation in temporary venv

5. **Implement Publishing** (1.5h)

   - Git tagging logic
   - Push to GitHub with CI monitoring
   - PyPI publishing (with TestPyPI option)
   - GitHub release creation with gh CLI

6. **Implement Documentation Deployment** (1h)

   - Documentation building
   - Deployment to GitHub Pages or Read the Docs
   - Link verification

7. **Implement Post-Release Tasks** (1h)

   - Bump to development version
   - Update changelog for next release
   - Generate announcement text
   - Clipboard integration

8. **Implement Error Handling and Rollback** (1.5h)

   - Error detection at each step
   - State saving for recovery
   - Git rollback (reset commits, delete tags)
   - Manual recovery instructions

9. **Implement Dry-Run Mode** (0.5h)

   - Preview mode that shows what would happen
   - No actual changes made
   - Detailed output of planned actions

10. **Add Interactive Prompts** (1h)

    - Confirmation prompts at key steps
    - User input for version numbers
    - Changelog review and editing
    - Final confirmation before publishing

11. **Testing** (1h)

    - Test dry-run mode
    - Test rollback on various errors
    - Test version bumping logic
    - Test with real release (on test repository)

12. **Documentation** (0.5h)

    - Update CONTRIBUTING.md with release process
    - Document command usage
    - Add troubleshooting section

## Testing Strategy

### Manual Testing

```bash
# Test dry-run mode
/release --dry-run
# Verify: Shows all planned actions, makes no changes

# Test version calculation
/release --type patch --dry-run
# Verify: Correctly calculates next patch version

# Test on test repository
# Create test repo or use branch
/release --version 0.1.0-test
# Verify: Full process works end-to-end

# Test rollback
# Intentionally cause error mid-release
# Verify: Rollback restores original state
````

### Integration Testing

```bash
# Test with actual release (careful!)
# On a test branch or version
/release --version 2.1.0-rc1 --skip-publish
# Verify: Everything except PyPI publish works

# Test individual phases
/release --stop-at build  # Stop after building
/release --start-at publish  # Resume from publishing
```

### Error Scenario Testing

```bash
# Test error handling
# Network failure during publish
# Git push failure
# CI failure after push
# Verify: Appropriate error messages and rollback options
```

## Acceptance Criteria

- [ ] `/release` command available in Claude Code
- [ ] All 25 release steps implemented
- [ ] Dry-run mode works (preview without changes)
- [ ] Interactive mode asks for confirmation at key steps
- [ ] Version bumping updates all configured files
- [ ] Changelog automatically updated
- [ ] Packages built and validated
- [ ] Git tag created and pushed
- [ ] PyPI publishing works
- [ ] GitHub release created with notes
- [ ] Documentation deployed
- [ ] Post-release version bump to dev version
- [ ] Rollback works on errors
- [ ] Progress displayed throughout process
- [ ] Release report generated at end
- [ ] Error recovery instructions provided
- [ ] Documentation updated
- [ ] Tested on real release

## Related Files

**Created Files:**

- `.claude/commands/release.md` - Main release command
- `.claude/commands/release/pre_release.py` - Pre-release validation
- `.claude/commands/release/version_bump.py` - Version bumping
- `.claude/commands/release/changelog.py` - Changelog management
- `.claude/commands/release/build.py` - Package building
- `.claude/commands/release/publish.py` - PyPI publishing
- `.claude/commands/release/github_release.py` - GitHub releases
- `.claude/commands/release/docs_deploy.py` - Docs deployment
- `.claude/commands/release/post_release.py` - Post-release tasks
- `.claude/commands/release/rollback.py` - Error rollback

**Modified Files:**

- `pyproject.toml` - Add `[tool.release]` configuration
- `CONTRIBUTING.md` - Document release process
- `Makefile` - Add `make release` target (wrapper)

## Dependencies

**Python Dependencies:**

- `build` - Already installed (package building)
- `twine` - Already installed (PyPI publishing)
- `check-wheel-contents` - Task 018 (wheel validation)
- `bump2version` or `bumpversion` - Version bumping helper (optional)
- `python-semantic-release` - Semantic versioning (optional)

**External Tools:**

- `gh` CLI - GitHub releases (already used)
- `git` - Version control (already used)

**Task Dependencies:**

- Task 018 - Automated package building (complementary, not required)
- Task 245 - check-wheel-contents validation

**Related Tasks:**

- Task 018: Automated Python package building and publishing
  - Provides GitHub Actions automation
  - `/release` command can trigger or complement this
- Task 245: check-wheel-contents
  - Used in validation phase

## Additional Notes

### Design Philosophy

**Automation vs Control:**

- Automate repetitive tasks
- Provide control points for human judgment
- Allow skipping steps if needed
- Support partial execution

**Safety First:**

- Dry-run by default or require explicit confirmation
- Rollback on any error
- Save state for manual recovery
- Comprehensive validation before destructive actions

**User Experience:**

- Clear progress indication
- Descriptive error messages
- Helpful recovery instructions
- Detailed logging

### Comparison with Task 018

**Task 018 (GitHub Actions Automation):**

- Triggered automatically on git tags
- No user interaction
- Full automation
- Runs in CI environment

**This Task (Release Command):**

- Triggered manually by developer
- Interactive with confirmations
- Guided process
- Runs in local environment
- Creates the git tag that triggers task 018

**How They Work Together:**

- `/release` command creates and pushes git tag
- This triggers GitHub Actions from task 018
- `/release` can wait for Actions to complete
- Or `/release` can publish directly

### Alternative Approaches

**Option 1: Minimal Command (Lower Effort)**

- Just version bumping and git tagging
- Rely on task 018 for publishing
- 3-4 hours instead of 8-12

**Option 2: Maximum Automation (Higher Effort)**

- AI-generated changelog from commits
- Automatic breaking change detection
- Automated documentation updates
- Social media posting automation
- 12-16 hours

**Recommended: Middle Ground (This Task)**

- Comprehensive but not over-automated
- Human review at key points
- Reliable and safe
- 8-12 hours

### Release Types

Support different release types:

```bash
/release --type major   # 2.1.0 → 3.0.0
/release --type minor   # 2.1.0 → 2.2.0
/release --type patch   # 2.1.0 → 2.1.1
/release --type rc      # 2.1.0 → 2.1.0-rc1
/release --type beta    # 2.1.0 → 2.1.0-beta1
/release --type alpha   # 2.1.0 → 2.1.0-alpha1
```

### Changelog Formats

Support multiple changelog formats:

**Keep a Changelog:**

```markdown
## [2.1.0] - 2026-04-19

### Added
- New feature X

### Changed
- Updated feature Y

### Fixed
- Bug fix Z
```

**Conventional Commits:**

```markdown
## [2.1.0] - 2026-04-19

**Features:**
- feat: new feature X (abc123)

**Bug Fixes:**
- fix: bug fix Z (def456)
```

### Success Metrics

- [ ] Time to release: 30-60 min manual → 5-10 min automated
- [ ] Error rate: 10-20% manual errors → \<1% automated errors
- [ ] Steps remembered: 15-30 steps → 1 command
- [ ] Rollback time: 30+ min manual → 1 min automated
- [ ] Developer satisfaction: Reduced release anxiety
- [ ] Release frequency: Enable more frequent releases

### Future Enhancements

After initial implementation:

1. **AI Changelog Generation**: Use commit messages to auto-generate changelog
1. **Breaking Change Detection**: Analyze code changes for breaking changes
1. **Release Notes Templates**: Customizable release note templates
1. **Multi-Platform Publishing**: Publish to multiple package registries
1. **Notification Integration**: Slack/Discord/Email notifications
1. **Metrics Collection**: Track release metrics over time

## Implementation Notes

*To be filled during implementation:*

- Actual command structure chosen
- Libraries/tools used
- Error scenarios encountered
- Rollback testing results
- User feedback on interactive prompts
- Time spent on each phase
- Deviations from plan
- Actual effort vs estimated
- Issues with any external tools
- Improvements for future releases
