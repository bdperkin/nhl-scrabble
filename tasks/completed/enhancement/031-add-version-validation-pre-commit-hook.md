# Add Version Validation in Pre-commit Hooks

**GitHub Issue**: [#380](https://github.com/bdperkin/nhl-scrabble/issues/380)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Add pre-commit hook validation to ensure version consistency and prevent version-related errors. With the project using dynamic versioning from git tags (hatch-vcs), we need automated checks to prevent:

- Accidentally committing auto-generated `_version.py`
- Hardcoding versions in files that should use dynamic versioning
- Removing `dynamic = ["version"]` from `pyproject.toml`
- Creating malformed git tags that break version detection

Currently, these issues can only be caught during CI or at build time, which is too late. Pre-commit hooks provide immediate feedback to developers.

## Current State

**Dynamic Versioning Setup** (from task #010):

```toml
# pyproject.toml
[project]
dynamic = ["version"]  # Version from git tags

[tool.hatch.version]
source = "vcs"  # Use version control system

[tool.hatch.build.hooks.vcs]
version-file = "src/nhl_scrabble/_version.py"  # Auto-generated
```

**Git Ignore**:
```gitignore
# Auto-generated version file (hatch-vcs)
src/nhl_scrabble/_version.py
```

**Current Issues (No Validation)**:

1. ❌ No check that `_version.py` is not committed
2. ❌ No check that `pyproject.toml` has `dynamic = ["version"]`
3. ❌ No validation of git tag format (must be `vX.Y.Z`)
4. ❌ No check for hardcoded version strings in key files
5. ❌ Developers can accidentally break versioning without immediate feedback

**Pre-commit Infrastructure**:
- ✅ 67 hooks already configured
- ✅ `.pre-commit-config.yaml` well-organized
- ✅ Local hooks section exists for custom checks
- ❌ No version validation hooks

## Proposed Solution

Add a custom pre-commit hook to validate version-related requirements:

### 1. Custom Hook Script

Create `.pre-commit-hooks/check-version-consistency.py`:

```python
#!/usr/bin/env python3
"""Pre-commit hook to validate version consistency for hatch-vcs setup."""

import re
import sys
from pathlib import Path

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_version_file_not_committed() -> bool:
    """Check that auto-generated _version.py is not committed."""
    version_file = Path("src/nhl_scrabble/_version.py")

    if version_file.exists():
        # Check if file is tracked by git (staged)
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(version_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"{RED}✗ FAIL:{RESET} Auto-generated _version.py should not be committed")
            print(f"  File: {version_file}")
            print(f"  Solution: git rm --cached {version_file}")
            return False

    return True


def check_dynamic_version_in_pyproject() -> bool:
    """Check that pyproject.toml has dynamic versioning configured."""
    pyproject = Path("pyproject.toml")

    if not pyproject.exists():
        print(f"{RED}✗ FAIL:{RESET} pyproject.toml not found")
        return False

    content = pyproject.read_text()

    # Check for dynamic = ["version"]
    if 'dynamic = ["version"]' not in content and "dynamic = ['version']" not in content:
        print(f"{RED}✗ FAIL:{RESET} pyproject.toml missing dynamic version configuration")
        print('  Required: dynamic = ["version"]')
        return False

    # Check for hatch.version.source = "vcs"
    if 'source = "vcs"' not in content:
        print(f"{RED}✗ FAIL:{RESET} pyproject.toml missing hatch-vcs configuration")
        print('  Required: [tool.hatch.version] source = "vcs"')
        return False

    return True


def check_no_hardcoded_versions() -> bool:
    """Check key files don't have hardcoded versions."""
    files_to_check = [
        "src/nhl_scrabble/__init__.py",
        "src/nhl_scrabble/cli.py",
    ]

    # Pattern for hardcoded version strings (but allow imports)
    version_pattern = re.compile(r'^\s*__version__\s*=\s*["\'](\d+\.\d+\.\d+.*)["\']', re.MULTILINE)

    errors = []
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()

            # Skip if it's importing from _version
            if "from nhl_scrabble._version import __version__" in content:
                continue

            matches = version_pattern.findall(content)
            if matches:
                errors.append((file_path, matches[0]))

    if errors:
        print(f"{RED}✗ FAIL:{RESET} Found hardcoded version strings:")
        for file_path, version in errors:
            print(f"  {file_path}: __version__ = '{version}'")
        print(f"  Solution: Import from _version.py instead")
        return False

    return True


def check_git_tag_format() -> bool:
    """Check that git tags follow semantic versioning (vX.Y.Z)."""
    import subprocess

    # Get most recent tag
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # No tags yet - that's okay
        print(f"{YELLOW}⚠ WARNING:{RESET} No git tags found (this is okay for new repos)")
        return True

    tag = result.stdout.strip()

    # Check format: vX.Y.Z or vX.Y.Z-<prerelease>
    semver_pattern = re.compile(r'^v(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9.-]+)?$')

    if not semver_pattern.match(tag):
        print(f"{RED}✗ FAIL:{RESET} Latest git tag does not follow semantic versioning")
        print(f"  Tag: {tag}")
        print(f"  Expected format: vX.Y.Z (e.g., v2.1.0, v1.0.0-rc1)")
        return False

    return True


def main() -> int:
    """Run all version validation checks."""
    print(f"\n{GREEN}Running version consistency checks...{RESET}\n")

    checks = [
        ("Auto-generated _version.py not committed", check_version_file_not_committed),
        ("Dynamic versioning in pyproject.toml", check_dynamic_version_in_pyproject),
        ("No hardcoded version strings", check_no_hardcoded_versions),
        ("Git tag format (semantic versioning)", check_git_tag_format),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
            print(f"{status}: {name}")
            results.append(result)
        except Exception as e:
            print(f"{RED}✗ ERROR{RESET}: {name}")
            print(f"  Exception: {e}")
            results.append(False)

    print()  # Blank line

    if all(results):
        print(f"{GREEN}All version consistency checks passed!{RESET}\n")
        return 0
    else:
        print(f"{RED}Version consistency checks failed!{RESET}")
        print(f"{YELLOW}Fix the issues above and try again.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### 2. Pre-commit Configuration

Add to `.pre-commit-config.yaml` (in local hooks section):

```yaml
  # ============================================================================
  # Version Validation - Dynamic Versioning Consistency
  # ============================================================================

  - repo: local
    hooks:
      - id: check-version-consistency
        name: Check version consistency (hatch-vcs)
        entry: python .pre-commit-hooks/check-version-consistency.py
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
        description: |
          Validate version configuration for hatch-vcs dynamic versioning:
          - Auto-generated _version.py not committed
          - pyproject.toml has dynamic = ["version"]
          - No hardcoded version strings in key files
          - Git tags follow semantic versioning (vX.Y.Z)
```

### 3. Make Script Executable

```bash
chmod +x .pre-commit-hooks/check-version-consistency.py
```

### 4. Integration with Existing Hooks

The hook runs:
- **When**: Every commit (pre-commit stage)
- **Cost**: ~100ms (very fast, all local checks)
- **Fail-fast**: Yes (fails immediately on version issues)
- **Auto-fix**: No (requires manual intervention)

## Implementation Steps

1. **Create Hook Script** (30 min)
   - Create `.pre-commit-hooks/` directory
   - Write `check-version-consistency.py` script
   - Add comprehensive checks (4 validations)
   - Add colored output for readability
   - Make executable (`chmod +x`)

2. **Update Pre-commit Config** (15 min)
   - Add local hook to `.pre-commit-config.yaml`
   - Add descriptive comments
   - Configure to run on all commits
   - Set `pass_filenames: false` (doesn't need file list)

3. **Testing** (30 min)
   - Test with valid configuration (should pass)
   - Test with _version.py committed (should fail)
   - Test with hardcoded version (should fail)
   - Test with missing `dynamic = ["version"]` (should fail)
   - Test with invalid git tag (should fail)
   - Verify output formatting is clear

4. **Documentation** (15 min)
   - Update CONTRIBUTING.md with version requirements
   - Document in CLAUDE.md
   - Add comments in pre-commit config
   - Update pre-commit hook count (67 → 68)

## Testing Strategy

### Manual Testing

```bash
# 1. Install hook
pre-commit install

# 2. Test valid state (should pass)
git add pyproject.toml
pre-commit run check-version-consistency

# 3. Test invalid states (should fail)

# Test 3a: Commit _version.py (should fail)
git add src/nhl_scrabble/_version.py
pre-commit run check-version-consistency
git reset HEAD src/nhl_scrabble/_version.py

# Test 3b: Remove dynamic version (should fail)
# Temporarily edit pyproject.toml to remove 'dynamic = ["version"]'
pre-commit run check-version-consistency
# Revert change

# Test 3c: Add hardcoded version (should fail)
# Add __version__ = "0.1.0" to src/nhl_scrabble/__init__.py
pre-commit run check-version-consistency
# Revert change

# Test 3d: Create invalid tag (should fail)
git tag 0.1.0  # Missing 'v' prefix
pre-commit run check-version-consistency
git tag -d 0.1.0

# 4. Run on all files
pre-commit run check-version-consistency --all-files
```

### Integration Testing

```bash
# Test with actual commit
echo "# Test" >> README.md
git add README.md
git commit -m "test: version validation hook"
# Hook should run and pass

# Test failure scenario
git add src/nhl_scrabble/_version.py
git commit -m "test: should fail"
# Hook should run and fail, blocking commit
```

### CI Testing

The hook should also be tested in CI:

```bash
# In CI workflow
pre-commit run --all-files
```

## Acceptance Criteria

- [x] `.pre-commit-hooks/check-version-consistency.py` script created
- [x] Script checks all 4 validation rules:
  - [x] Auto-generated `_version.py` not committed
  - [x] `pyproject.toml` has `dynamic = ["version"]`
  - [x] No hardcoded version strings in key files
  - [x] Git tags follow semantic versioning pattern
- [x] Script has colored output (green ✓, red ✗, yellow ⚠)
- [x] Hook added to `.pre-commit-config.yaml`
- [x] Hook runs on every commit (pre-commit stage)
- [x] Manual tests pass (all 4 scenarios tested)
- [x] Integration tests pass (real commits)
- [x] Documentation updated:
  - [x] CONTRIBUTING.md (version requirements)
  - [x] CLAUDE.md (pre-commit hook count: 68)
  - [x] Comments in `.pre-commit-config.yaml`
- [x] Hook is fast (<200ms)
- [x] Clear error messages with solutions

## Related Files

- `.pre-commit-hooks/check-version-consistency.py` - New validation script (to be created)
- `.pre-commit-config.yaml` - Pre-commit configuration (update with new hook)
- `pyproject.toml` - Checked for dynamic versioning
- `src/nhl_scrabble/_version.py` - Should not be committed (validated)
- `src/nhl_scrabble/__init__.py` - Checked for hardcoded versions
- `.gitignore` - Already ignores _version.py
- `CONTRIBUTING.md` - Document version requirements
- `CLAUDE.md` - Update pre-commit hook count

## Dependencies

**Related Tasks:**
- Task #010 (refactoring/010-dynamic-versioning.md) - Dynamic versioning implementation (completed)
  - This task adds validation for task #010's dynamic versioning system
  - Ensures version consistency is maintained

**Tools:**
- Python 3.12+ (already required)
- Git (already required)
- pre-commit (already installed)
- No new external dependencies

**Pre-commit Infrastructure:**
- Current: 67 hooks
- After this task: 68 hooks

## Additional Notes

### Validation Rules Details

**1. Auto-generated _version.py Not Committed**
- **Why**: hatch-vcs generates this at build time
- **Impact**: If committed, may cause version drift
- **Check**: `git ls-files --error-unmatch src/nhl_scrabble/_version.py`
- **Fix**: `git rm --cached src/nhl_scrabble/_version.py`

**2. Dynamic Versioning in pyproject.toml**
- **Why**: Required for hatch-vcs to work
- **Impact**: Version would need to be manually maintained
- **Check**: Search for `dynamic = ["version"]` and `source = "vcs"`
- **Fix**: Restore configuration in pyproject.toml

**3. No Hardcoded Version Strings**
- **Why**: Defeats purpose of dynamic versioning
- **Impact**: Version inconsistencies between files
- **Check**: Regex search for `__version__ = "X.Y.Z"` pattern
- **Fix**: Import from _version.py instead

**4. Git Tag Format (Semantic Versioning)**
- **Why**: hatch-vcs expects `vX.Y.Z` format
- **Impact**: Version detection breaks
- **Check**: Regex validation of latest tag
- **Fix**: Delete malformed tag, create correct tag

### Performance

- **Script Execution**: ~50-100ms
- **Git Commands**: ~20-30ms each
- **File Reads**: ~10-20ms
- **Total**: ~100-200ms (negligible impact)

### False Positives

**Handling legitimate cases:**

1. **Initial repository** (no tags):
   - Show warning instead of failure
   - Allow commit to proceed

2. **Pre-release tags** (`v1.0.0-rc1`):
   - Regex pattern supports pre-release suffixes
   - Follows semantic versioning spec

3. **Development versions** (`v1.0.0.dev5+g1234567`):
   - Only validates pushed tags, not dev versions
   - Dev versions are auto-generated

### Integration with Existing Hooks

**Position in hook sequence:**
- Runs early (before formatters/linters)
- Fast enough to not slow down workflow
- Provides immediate feedback

**Interaction with other hooks:**
- Independent of other hooks
- No conflicts or dependencies
- Can run in parallel with other checks

### Developer Experience

**Good error messages:**
```
✗ FAIL: Auto-generated _version.py should not be committed
  File: src/nhl_scrabble/_version.py
  Solution: git rm --cached src/nhl_scrabble/_version.py
```

**Success messages:**
```
✓ PASS: Auto-generated _version.py not committed
✓ PASS: Dynamic versioning in pyproject.toml
✓ PASS: No hardcoded version strings
✓ PASS: Git tag format (semantic versioning)

All version consistency checks passed!
```

### Security Considerations

- Script runs locally (no network calls)
- Only reads files, doesn't modify
- Git commands are read-only (ls-files, describe)
- No subprocess injection (uses list arguments)

### Maintenance

**When to update this hook:**
- If version file location changes
- If additional files need version validation
- If tag format requirements change
- If pyproject.toml structure changes

## Implementation Notes

**Implemented**: 2026-04-27
**Branch**: enhancement/031-add-version-validation-pre-commit-hook
**PR**: #411 - https://github.com/bdperkin/nhl-scrabble/pull/411
**Commits**: 1 commit (7736de7)

### Actual Implementation

Implementation followed the proposed solution very closely with minor refinements:

**Script Implementation**:
- Created `.pre-commit-hooks/check-version-consistency.py` as specified
- All 4 validation checks implemented exactly as designed
- Colored output using ANSI codes (green ✓, red ✗, yellow ⚠)
- Clear error messages with actionable solutions

**Configuration**:
- Added hook to `.pre-commit-config.yaml` in new "Version Validation" section
- Updated header comment (67 → 68 hooks)
- Hook runs on every commit with `always_run: true`

**Documentation**:
- Updated CLAUDE.md with hook count and new category
- Added comprehensive "Version Requirements" section to CONTRIBUTING.md
- Documented all 4 validation rules with examples and fixes

### Challenges Encountered

**1. Whitespace Flexibility in pyproject.toml**:
- **Issue**: Initial check for `dynamic = ["version"]` was too strict
- **Discovery**: pyproject.toml uses `dynamic = [ "version" ]` with spaces
- **Solution**: Implemented regex pattern for flexible whitespace matching
- **Pattern**: `r'dynamic\s*=\s*\[\s*["\']version["\']\s*\]'`

**2. Ruff Linting Warnings**:
- **Issue**: Ruff flagged subprocess calls (S603, S607) and print statements (T201)
- **Reason**: Hook script intentionally uses these for CLI output
- **Solution**: Added file-level `# ruff: noqa: T201, S603, S607` directive
- **Documentation**: Added docstring explaining exceptions

**3. Subprocess Check Parameter**:
- **Issue**: Ruff PLW1510 required explicit `check` argument
- **Solution**: Added `check=False` to subprocess.run() calls
- **Rationale**: We intentionally check returncode for validation logic

### Edge Cases Discovered

**1. No Git Tags (New Repository)**:
- Hook displays warning instead of failure
- Allows commit to proceed (graceful degradation)
- Output: `⚠ WARNING: No git tags found (this is okay for new repos)`

**2. Whitespace Variations in Config**:
- Handles both `["version"]` and `[ "version" ]`
- Supports both double quotes and single quotes
- Regex pattern flexible but still validates structure

**3. Import vs Hardcoded Version**:
- Correctly skips files importing from `_version.py`
- Only flags actual hardcoded `__version__ = "X.Y.Z"` patterns
- Regex pattern: `r'^\s*__version__\s*=\s*["\'](\d+\.\d+\.\d+.*)["\']'`

### Performance Measurements

**Actual Performance** (measured during testing):
- Script execution: ~50-80ms
- Git ls-files command: ~15-20ms
- Git describe command: ~10-15ms
- File reads (pyproject.toml + 2 Python files): ~5-10ms
- **Total runtime**: ~80-125ms

**Impact**: Negligible - hook completes in <200ms as required

### Testing Results

**Manual Testing**:
- ✅ Valid configuration: All checks pass
- ✅ Staged `_version.py`: Correctly fails with clear message
- ✅ Missing `dynamic = ["version"]`: Correctly fails
- ✅ Hardcoded version string: Correctly fails
- ✅ Invalid tag format: Correctly fails
- ✅ No tags scenario: Warning displayed, commit allowed

**Automated Testing**:
- ✅ All 68 pre-commit hooks pass (including new hook)
- ✅ 1405 tests pass
- ✅ 91.87% code coverage maintained
- ✅ No breaking changes to existing code

### Developer Experience

**Output Quality**:
- Color coding makes pass/fail instantly recognizable
- Error messages include file paths and specific solutions
- Warning vs error distinction (no tags = warning, not failure)
- Success message confirms all checks passed

**Example Output**:
```
Running version consistency checks...

✓ PASS: Auto-generated _version.py not committed
✓ PASS: Dynamic versioning in pyproject.toml
✓ PASS: No hardcoded version strings
✓ PASS: Git tag format (semantic versioning)

All version consistency checks passed!
```

### Deviations from Plan

**Minor Deviations** (improvements):
1. **Regex for whitespace**: Made pattern more flexible than literal string match
2. **Ruff noqa**: Added file-level directives for better documentation
3. **Subprocess check**: Added explicit `check=False` for clarity

**No Functional Deviations**: All validation logic implemented exactly as specified

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~1.5 hours
  - Script implementation: 30 minutes
  - Configuration updates: 15 minutes
  - Testing (manual + automated): 30 minutes
  - Documentation: 15 minutes
- **Variance**: Within estimate

**Breakdown**:
- Implementation was straightforward following the detailed spec
- Testing revealed whitespace edge case (added 10 minutes)
- Ruff linting adjustments (added 5 minutes)
- Documentation updates were comprehensive but quick

### Related PRs

- #411 - Main implementation (this task)

### Lessons Learned

**1. Regex vs Literal Matching**:
- Configuration files may have whitespace variations
- Use flexible regex patterns for robustness
- Document the pattern for future maintainers

**2. Linter Exceptions**:
- CLI scripts need different rules than library code
- File-level noqa directives better than per-line
- Always document *why* exceptions are needed

**3. Graceful Degradation**:
- Warning vs error distinction improves UX
- No tags in new repo shouldn't block commits
- Clear messaging prevents confusion

**4. Testing Edge Cases**:
- Test against actual repo state (pyproject.toml formatting)
- Don't assume exact formatting in config files
- Manual testing catches issues automated tests miss

### Future Enhancements

**Potential Improvements** (not in current scope):
1. Add check for `.gitignore` contains `_version.py`
2. Validate `[tool.hatch.build.hooks.vcs]` section
3. Check for consistent version references in README/docs
4. Add `--fix` mode to auto-remove staged `_version.py`

**Maintenance Notes**:
- Review regex patterns if pyproject.toml format changes
- Update file list if more files should avoid hardcoded versions
- Monitor for false positives in production use
