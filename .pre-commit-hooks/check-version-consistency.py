#!/usr/bin/env python3
"""Pre-commit hook to validate version consistency for hatch-vcs setup.

This script validates version-related requirements for hatch-vcs dynamic versioning.
It's designed to run as a pre-commit hook and uses print() for user-facing output.

Ruff exceptions:
- S603, S607: subprocess with partial path - safe for trusted git commands
- T201: print statements - required for pre-commit hook user output
- BLE001: broad exception - intentional to provide user-friendly error messages
"""

# ruff: noqa: T201, S603, S607

import re
import subprocess
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
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(version_file)],
            capture_output=True,
            text=True,
            check=False,
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

    # Check for dynamic = ["version"] (with flexible whitespace)
    # Matches: dynamic = ["version"], dynamic = [ "version" ], dynamic = ['version']
    dynamic_pattern = re.compile(r'dynamic\s*=\s*\[\s*["\']version["\']\s*\]')
    if not dynamic_pattern.search(content):
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
        print("  Solution: Import from _version.py instead")
        return False

    return True


def check_git_tag_format() -> bool:
    """Check that git tags follow semantic versioning (vX.Y.Z)."""
    # Get most recent tag
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        # No tags yet - that's okay
        print(f"{YELLOW}⚠ WARNING:{RESET} No git tags found (this is okay for new repos)")
        return True

    tag = result.stdout.strip()

    # Check format: vX.Y.Z or vX.Y.Z-<prerelease>
    semver_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9.-]+)?$")

    if not semver_pattern.match(tag):
        print(f"{RED}✗ FAIL:{RESET} Latest git tag does not follow semantic versioning")
        print(f"  Tag: {tag}")
        print("  Expected format: vX.Y.Z (e.g., v2.1.0, v1.0.0-rc1)")
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
        except Exception as e:  # noqa: BLE001
            print(f"{RED}✗ ERROR{RESET}: {name}")
            print(f"  Exception: {e}")
            results.append(False)

    print()  # Blank line

    if all(results):
        print(f"{GREEN}All version consistency checks passed!{RESET}\n")
        return 0
    print(f"{RED}Version consistency checks failed!{RESET}")
    print(f"{YELLOW}Fix the issues above and try again.{RESET}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
