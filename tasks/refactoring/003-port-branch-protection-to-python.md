# Port check-branch-protection.sh Git Hook to Python

**GitHub Issue**: #101 - https://github.com/bdperkin/nhl-scrabble/issues/101

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Port the `.git-hooks/check-branch-protection.sh` shell script to an equivalent Python script (`.git-hooks/check-branch-protection.py`). The shell script currently warns developers when committing directly to protected branches (main/master) and prompts for confirmation. Converting to Python improves cross-platform compatibility, maintainability, and consistency with other project tooling.

## Current State

The project has a bash script for branch protection checking:

**.git-hooks/check-branch-protection.sh** (79 lines):

```bash
#!/usr/bin/env bash
# Git hook to warn about committing directly to protected branches

set -e

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
PROTECTED_BRANCHES="^(main|master)$"

# Check if running in CI environment
is_ci() {
    # GitHub Actions
    [[ -n "${GITHUB_ACTIONS}" ]] && return 0
    # GitLab CI
    [[ -n "${GITLAB_CI}" ]] && return 0
    # Travis CI
    [[ -n "${TRAVIS}" ]] && return 0
    # CircleCI
    [[ -n "${CIRCLECI}" ]] && return 0
    # Jenkins
    [[ -n "${JENKINS_URL}" ]] && return 0
    # Generic CI indicator
    [[ -n "${CI}" ]] && return 0

    return 1
}

if [[ "$BRANCH" =~ $PROTECTED_BRANCHES ]]; then
    # In CI: Allow the commit (it's already on main after PR merge)
    if is_ci; then
        echo "ℹ️  CI environment detected: Allowing commit to '$BRANCH' branch"
        exit 0
    fi

    # Local: Warn and prompt for confirmation
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  WARNING: You are committing directly to the '$BRANCH' branch!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    # ... (warning message)

    read -p "⚠️  Continue committing to '$BRANCH'? [y/N] " -n 1 -r

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Commit aborted."
        exit 1
    fi
fi

exit 0
```

**Pre-commit hook** (.pre-commit-config.yaml):

```yaml
- repo: local
  hooks:
    - id: check-branch-protection
      name: Check Branch Protection
      entry: .git-hooks/check-branch-protection.sh
      language: script
      always_run: true
      pass_filenames: false
      stages: [pre-commit]
```

**Issues**:

1. **Platform Dependency**: Requires bash (not native on Windows)
1. **Interactive Input**: Uses bash `read` (problematic for non-interactive environments)
1. **Inconsistency**: Other tools use Python
1. **Limited Testing**: Bash scripts harder to unit test
1. **Maintenance**: Shell syntax less familiar to Python developers
1. **Error Handling**: Limited structured error handling

## Proposed Solution

Create `.git-hooks/check-branch-protection.py` following Python best practices:

**.git-hooks/check-branch-protection.py** (Python equivalent):

```python
#!/usr/bin/env python3
"""Git hook to warn about committing directly to protected branches.

This hook prevents accidental commits to main/master branches by displaying
a warning and requiring user confirmation. In CI environments, commits are
allowed automatically (expected after PR merge).

Usage:
    Called automatically by pre-commit hook

Exit Codes:
    0: Commit allowed (not on protected branch, or user confirmed, or CI)
    1: Commit blocked (user declined confirmation)
"""

# ruff: noqa: T201, S603
# T201: print statements are appropriate for git hooks
# S603: subprocess calls to git (trusted tool)

from __future__ import annotations

import os
import re
import subprocess
import sys


# Protected branch pattern (main or master)
PROTECTED_BRANCHES = re.compile(r"^(main|master)$")


def get_current_branch() -> str | None:
    """Get the current git branch name.

    Returns:
        Branch name, or None if not on a branch (detached HEAD)
    """
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def is_ci_environment() -> bool:
    """Check if running in a CI environment.

    Checks for common CI environment variables.

    Returns:
        True if in CI, False otherwise
    """
    ci_indicators = [
        "GITHUB_ACTIONS",  # GitHub Actions
        "GITLAB_CI",  # GitLab CI
        "TRAVIS",  # Travis CI
        "CIRCLECI",  # CircleCI
        "JENKINS_URL",  # Jenkins
        "CI",  # Generic CI indicator
    ]
    return any(os.environ.get(indicator) for indicator in ci_indicators)


def is_protected_branch(branch: str) -> bool:
    """Check if branch is protected (main/master).

    Args:
        branch: Branch name to check

    Returns:
        True if branch is protected, False otherwise
    """
    return PROTECTED_BRANCHES.match(branch) is not None


def print_warning(branch: str) -> None:
    """Print warning message about committing to protected branch.

    Args:
        branch: Protected branch name
    """
    print()
    print("━" * 60)
    print(f"⚠️  WARNING: You are committing directly to the '{branch}' branch!")
    print("━" * 60)
    print()
    print("✅ Best practice workflow:")
    print("   1. Create a feature branch:")
    print("      git checkout -b feature/your-feature-name")
    print()
    print("   2. Make your commits on the feature branch")
    print()
    print("   3. Push and create a PR:")
    print("      git push -u origin feature/your-feature-name")
    print("      gh pr create")
    print()
    print("   4. Merge via PR after CI passes")
    print()
    print("━" * 60)
    print()
    print("To proceed anyway: Continue below (not recommended)")
    print("To abort and create a feature branch: Press Ctrl+C")
    print()


def print_abort_help() -> None:
    """Print help message after aborting commit."""
    print("❌ Commit aborted.")
    print()
    print("💡 Quick fix if you already made commits to main:")
    print("   # Move commits to a feature branch")
    print("   git checkout -b feature/your-feature-name")
    print("   git checkout main")
    print("   git reset --hard origin/main")
    print("   git checkout feature/your-feature-name")
    print()


def prompt_user_confirmation(branch: str) -> bool:
    """Prompt user to confirm committing to protected branch.

    Args:
        branch: Protected branch name

    Returns:
        True if user confirms, False otherwise
    """
    try:
        response = input(f"⚠️  Continue committing to '{branch}'? [y/N] ")
        print("━" * 60)
        return response.strip().lower() in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        print("━" * 60)
        return False


def main() -> int:
    """Main entry point for branch protection check.

    Returns:
        0 if commit allowed, 1 if commit blocked
    """
    # Get current branch
    branch = get_current_branch()
    if branch is None:
        # Not on a branch (detached HEAD), allow commit
        return 0

    # Check if branch is protected
    if not is_protected_branch(branch):
        # Not a protected branch, allow commit
        return 0

    # In CI: Allow commit (expected after PR merge)
    if is_ci_environment():
        print(f"ℹ️  CI environment detected: Allowing commit to '{branch}' branch")
        return 0

    # Local: Warn and prompt for confirmation
    print_warning(branch)

    if not prompt_user_confirmation(branch):
        print_abort_help()
        return 1

    print(f"✅ Proceeding with commit to '{branch}' (you chose to bypass protection)...")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Update .pre-commit-config.yaml**:

```yaml
- repo: local
  hooks:
    - id: check-branch-protection
      name: Check Branch Protection
      entry: python .git-hooks/check-branch-protection.py  # Changed from script to python
      language: system
      always_run: true
      pass_filenames: false
      stages: [pre-commit]
```

## Implementation Steps

1. **Create Python script**

   - Create `.git-hooks/check-branch-protection.py`
   - Implement all functions from shell script
   - Add proper docstrings and type hints
   - Follow project's ruff rules and style
   - Make executable: `chmod +x .git-hooks/check-branch-protection.py`

1. **Update pre-commit hook**

   - Change entry from `.git-hooks/check-branch-protection.sh` to `python .git-hooks/check-branch-protection.py`
   - Change language from `script` to `system`
   - Verify hook still triggers correctly

1. **Test functionality**

   - Test on protected branch (main/master)
   - Test on non-protected branch
   - Test in CI environment
   - Test user confirmation (y/n)
   - Test keyboard interrupt (Ctrl+C)
   - Test non-interactive mode

1. **Update documentation**

   - Update `docs/BRANCH_PROTECTION.md` if it references the script
   - Update `CONTRIBUTING.md` if it references the script
   - Update `CLAUDE.md` if it references the script

1. **Remove old script**

   - Delete `.git-hooks/check-branch-protection.sh`
   - Ensure no other files reference it

1. **Verify pre-commit**

   - Run pre-commit manually: `pre-commit run check-branch-protection --all-files`
   - Verify it works when committing to main
   - Verify it allows commits to feature branches
   - Verify it works in CI simulation

## Testing Strategy

### Manual Testing

```bash
# 1. Test on protected branch (main)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test"
# Expected: Warning displayed, prompt for confirmation

# 2. Test declining confirmation
# When prompted, press 'n' or Ctrl+C
# Expected: "Commit aborted" message, exit code 1

# 3. Test accepting confirmation
git commit -m "test"
# When prompted, press 'y'
# Expected: "Proceeding with commit..." message, commit succeeds

# 4. Test on feature branch
git checkout -b feature/test
echo "test" >> test.txt
git add test.txt
git commit -m "test"
# Expected: No warning, commit succeeds immediately

# 5. Test CI environment simulation
export CI=true
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test"
# Expected: "CI environment detected" message, commit succeeds
unset CI

# 6. Test with pre-commit hook
pre-commit run check-branch-protection --all-files
# Expected: Same behavior as direct script execution
```

### Non-Interactive Testing

```bash
# Test in non-interactive environment (simulates CI pipes)
echo "n" | python .git-hooks/check-branch-protection.py
# Expected: Reads 'n' from stdin, aborts

echo "y" | python .git-hooks/check-branch-protection.py
# Expected: Reads 'y' from stdin, proceeds
```

### Cross-Platform Testing

```bash
# Test on Windows (PowerShell)
python .git-hooks/check-branch-protection.py
# Expected: Works without bash dependency

# Test on macOS
python3 .git-hooks/check-branch-protection.py
# Expected: Works with system Python
```

## Acceptance Criteria

- [x] `.git-hooks/check-branch-protection.py` created with equivalent functionality
- [x] Script follows project style (ruff, mypy, docstrings)
- [x] Type hints added throughout
- [x] Detects protected branches correctly (main/master)
- [x] Detects CI environments correctly (all 6 indicators)
- [x] Warns and prompts on protected branches locally
- [x] Allows commits in CI without prompting
- [x] Allows commits on non-protected branches
- [x] Handles user confirmation (y/yes/n/no)
- [x] Handles keyboard interrupt (Ctrl+C)
- [x] Exit codes match original (0 = allow, 1 = block)
- [x] Pre-commit hook updated to use Python script
- [x] Pre-commit hook works correctly
- [x] `.git-hooks/check-branch-protection.sh` deleted
- [x] No references to old shell script remain
- [x] Documentation updated
- [x] Works on Windows (no bash dependency)
- [x] All ruff/mypy checks pass
- [x] Script is executable

## Related Files

- `.git-hooks/check-branch-protection.sh` - Original shell script (to be deleted)
- `.git-hooks/check-branch-protection.py` - New Python script (to be created)
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `docs/BRANCH_PROTECTION.md` - Branch protection documentation
- `CONTRIBUTING.md` - May reference the script
- `CLAUDE.md` - Developer documentation
- `tasks/completed/bug-fixes/007-fix-ci-branch-protection.md` - Related completed task

## Dependencies

None - This is a standalone refactoring task.

## Additional Notes

### Benefits

**Cross-Platform Compatibility**:

- Works on Windows without bash/WSL
- No shell-specific syntax
- Consistent behavior across platforms

**Maintainability**:

- Python developers more familiar with Python than bash
- Easier to add features and error handling
- Can be unit tested (unlike shell scripts)
- Type checking with mypy
- Linting with ruff

**Better Error Handling**:

- Structured exception handling
- Clear error messages
- Handles keyboard interrupts gracefully
- Handles non-interactive environments

**Consistency**:

- Matches other Python tools in project
- Uses subprocess, os, re modules
- Proper docstrings and type hints
- Follows project style guide

### Breaking Changes

None - This is a drop-in replacement:

- Same command-line interface (no arguments)
- Same exit codes (0 = allow, 1 = block)
- Same output messages
- Same behavior in all scenarios

### Performance Impact

Negligible - Python interpreter overhead is minimal:

- Simple script with no heavy operations
- Git subprocess calls are the main time consumer
- Expected overhead: \<50ms, negligible for a pre-commit hook

### Security Considerations

**Subprocess Calls**:

- All subprocess calls are to git (trusted tool)
- No user input in git commands
- Proper noqa comments document security exceptions (S603)

**User Input**:

- Only reads y/n confirmation from stdin
- No injection vulnerabilities
- Handles EOFError and KeyboardInterrupt safely

**Same Security Profile as Shell Script**:

- Python version has same security characteristics
- No new security concerns introduced

### CI Environment Detection

The script checks for common CI environment variables:

- `GITHUB_ACTIONS` - GitHub Actions
- `GITLAB_CI` - GitLab CI
- `TRAVIS` - Travis CI
- `CIRCLECI` - CircleCI
- `JENKINS_URL` - Jenkins
- `CI` - Generic CI indicator

This ensures commits are allowed in CI after PR merges without manual intervention.

### Interactive vs Non-Interactive

**Interactive Mode** (local development):

- Displays warning message
- Prompts for user confirmation
- Handles keyboard interrupt gracefully

**Non-Interactive Mode** (CI/pipes):

- Detects CI environment
- Skips prompt, allows commit
- Or reads from stdin if provided

### Future Enhancements

After this refactoring, the Python script could be enhanced with:

- **Configurable protection**: Read protected branches from `.git/config`
- **Custom messages**: Allow projects to customize warning text
- **Skip option**: Environment variable to skip check (`SKIP_BRANCH_CHECK=1`)
- **Logging**: Optional logging of protection events
- **JSON output**: Machine-readable output for automation

These are outside the scope of this task but are easier to implement in Python.

### Migration Notes

**For Developers**:

- Pre-commit hook updates automatically (just pull latest)
- No action needed - script called by pre-commit infrastructure
- Same behavior as before

**For CI/CD**:

- No changes needed - CI detection works the same
- Same environment variables checked

**Testing the Migration**:

1. Before merging: Test pre-commit hook manually
1. After merging: Verify hook works locally
1. Monitor first few commits for any issues

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Testing results
- Any issues discovered with the original shell script
