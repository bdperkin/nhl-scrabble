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

# ruff: noqa: T201, S607, RUF001
# T201: print statements are appropriate for git hooks
# S603/S607: subprocess calls to git (trusted tool with hardcoded path)
# RUF001: Unicode emoji characters are intentional for visual output

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
    """Check branch protection and prompt user if necessary.

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
