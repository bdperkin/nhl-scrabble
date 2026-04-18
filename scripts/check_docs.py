"""Check if generated documentation is up-to-date.

This script regenerates API and CLI documentation and verifies that it matches
the committed versions. Used in pre-commit hooks to ensure documentation stays
in sync with code changes.

Usage:
    python scripts/check_docs.py

Exit Codes:
    0: Documentation is up-to-date or package not installed (skip)
    1: Documentation is out-of-date (needs regeneration)

Environment:
    Works in both local development and CI environments.
    Gracefully skips check if nhl_scrabble package is not importable
    (expected in pre-commit isolated environments).
"""

# ruff: noqa: INP001, S603, S607, T201
# INP001: tools directory is not a package
# S603/S607: subprocess calls are to trusted tools (pdoc, python, git)
# T201: print statements are appropriate for utility script

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[0;33m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str) -> None:
    """Print colored message to stdout.

    Args:
        message: Message to print
        color: ANSI color code
    """
    print(f"{color}{message}{Colors.NC}")


def check_package_importable() -> bool:
    """Check if nhl_scrabble package is importable.

    Returns:
        True if package can be imported, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import nhl_scrabble"],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def generate_api_docs() -> None:
    """Generate API reference documentation using pdoc.

    Raises:
        subprocess.CalledProcessError: If pdoc fails
    """
    print_colored("Generating API reference documentation...", Colors.BLUE)

    # Create output directory
    api_dir = Path("docs/reference/api")
    api_dir.mkdir(parents=True, exist_ok=True)

    # Run pdoc
    subprocess.run(
        ["pdoc", "nhl_scrabble", "-o", str(api_dir), "-d", "markdown"],
        check=True,
        capture_output=True,
    )


def generate_cli_docs() -> None:
    """Generate CLI reference documentation.

    Raises:
        subprocess.CalledProcessError: If generation fails
    """
    print_colored("Generating CLI reference documentation...", Colors.BLUE)

    subprocess.run(
        [sys.executable, "scripts/generate_cli_docs.py"],
        check=True,
        capture_output=True,
    )


def check_docs_modified() -> bool:
    """Check if generated documentation differs from committed version.

    Returns:
        True if docs are modified (out of date), False if up-to-date

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    result = subprocess.run(
        [
            "git",
            "diff",
            "--exit-code",
            "docs/reference/api/",
            "docs/reference/cli-generated.md",
        ],
        capture_output=True,
        check=False,
    )
    return result.returncode != 0


def get_modified_files() -> list[str]:
    """Get list of modified documentation files.

    Returns:
        List of modified file paths
    """
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "docs/reference/api/",
            "docs/reference/cli-generated.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def main() -> int:
    """Check generated documentation and return exit code.

    Returns:
        0 if docs are up-to-date or package not installed, 1 if out-of-date
    """
    print_colored("Checking generated documentation...", Colors.BLUE)

    # Check if package is importable
    if not check_package_importable():
        print_colored(
            "⚠️  Skipping documentation check: nhl_scrabble package not installed",
            Colors.YELLOW,
        )
        print_colored(
            "This is expected in pre-commit isolated environments.",
            Colors.YELLOW,
        )
        print_colored(
            "Documentation checks will run in CI via tox.",
            Colors.YELLOW,
        )
        return 0

    try:
        # Generate documentation
        generate_api_docs()
        generate_cli_docs()

        # Check if docs were modified
        if check_docs_modified():
            print_colored("✗ Generated docs are out of date!", Colors.RED)
            print_colored(
                "Run 'make docs-gen' to regenerate documentation",
                Colors.RED,
            )
            print()
            print("Modified files:")
            for file in get_modified_files():
                print(f"  {file}")
            return 1

        print_colored("✓ Generated docs are up-to-date", Colors.GREEN)
        return 0

    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Error generating documentation: {e}", Colors.RED)
        return 1


if __name__ == "__main__":
    sys.exit(main())
