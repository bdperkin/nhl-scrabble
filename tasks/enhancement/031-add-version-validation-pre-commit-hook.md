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

- [ ] `.pre-commit-hooks/check-version-consistency.py` script created
- [ ] Script checks all 4 validation rules:
  - [ ] Auto-generated `_version.py` not committed
  - [ ] `pyproject.toml` has `dynamic = ["version"]`
  - [ ] No hardcoded version strings in key files
  - [ ] Git tags follow semantic versioning pattern
- [ ] Script has colored output (green ✓, red ✗, yellow ⚠)
- [ ] Hook added to `.pre-commit-config.yaml`
- [ ] Hook runs on every commit (pre-commit stage)
- [ ] Manual tests pass (all 4 scenarios tested)
- [ ] Integration tests pass (real commits)
- [ ] Documentation updated:
  - [ ] CONTRIBUTING.md (version requirements)
  - [ ] CLAUDE.md (pre-commit hook count: 68)
  - [ ] Comments in `.pre-commit-config.yaml`
- [ ] Hook is fast (<200ms)
- [ ] Clear error messages with solutions

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

*To be filled during implementation:*
- Actual script implementation challenges
- Edge cases discovered during testing
- Performance measurements
- Developer feedback on error messages
- Any deviations from proposed solution
- Actual effort vs estimated
