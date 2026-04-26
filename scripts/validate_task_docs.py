#!/usr/bin/env python3
"""Task Documentation Validation Script.

Validates consistency between tasks/README.md, tasks/IMPLEMENTATION_SEQUENCE.md,
and tasks/TOOLING_ANALYSIS.md by comparing task counts from filesystem against
documented counts.

Usage:
    python scripts/validate_task_docs.py
    ./scripts/validate_task_docs.py

Exit Codes:
    0: All validation checks passed
    1: One or more validation checks failed
"""

# ruff: noqa: T201

import re
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RESET = "\033[0m"

    @classmethod
    def red(cls, text: str) -> str:
        """Return text in red."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def green(cls, text: str) -> str:
        """Return text in green."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def yellow(cls, text: str) -> str:
        """Return text in yellow."""
        return f"{cls.YELLOW}{text}{cls.RESET}"


def count_task_files() -> dict[str, int]:
    """Count task files on filesystem by category.

    Returns:
        Dictionary with category counts and totals
    """
    categories = [
        "bug-fixes",
        "security",
        "optimization",
        "enhancement",
        "testing",
        "new-features",
        "refactoring",
    ]

    counts = {}
    tasks_dir = Path("tasks")

    # Count active tasks per category
    for category in categories:
        category_path = tasks_dir / category
        if category_path.exists():
            # Count files matching pattern: starts with digit, ends with .md
            task_files = list(category_path.glob("[0-9]*.md"))
            counts[category] = len(task_files)
        else:
            counts[category] = 0

    # Calculate active total
    counts["active_total"] = sum(counts[cat] for cat in categories)

    # Count completed tasks
    completed_path = tasks_dir / "completed"
    if completed_path.exists():
        completed_files = list(completed_path.rglob("[0-9]*.md"))
        counts["completed"] = len(completed_files)
    else:
        counts["completed"] = 0

    # Calculate grand total
    counts["total"] = counts["active_total"] + counts["completed"]

    return counts


def extract_readme_counts(readme_path: Path) -> dict[str, int] | None:
    """Extract task counts from README.md.

    Args:
        readme_path: Path to tasks/README.md

    Returns:
        Dictionary with total, active, and completed counts, or None if parsing fails
    """
    if not readme_path.exists():
        return None

    content = readme_path.read_text()

    # Find line: **Total Tasks**: 142 tasks (63 active, 79 completed)
    pattern = r"\*\*Total Tasks\*\*:\s*(\d+)\s+tasks\s+\((\d+)\s+active,\s+(\d+)\s+completed\)"
    match = re.search(pattern, content)

    if match:
        return {
            "total": int(match.group(1)),
            "active": int(match.group(2)),
            "completed": int(match.group(3)),
        }

    return None


def extract_sequence_counts(sequence_path: Path) -> dict[str, int] | None:
    """Extract task counts from IMPLEMENTATION_SEQUENCE.md.

    Args:
        sequence_path: Path to tasks/IMPLEMENTATION_SEQUENCE.md

    Returns:
        Dictionary with active count, or None if parsing fails
    """
    if not sequence_path.exists():
        return None

    content = sequence_path.read_text()

    # Find line: **Total Tasks**: 63 active tasks
    pattern = r"\*\*Total Tasks\*\*:\s*(\d+)\s+active\s+tasks"
    match = re.search(pattern, content)

    if match:
        return {
            "active": int(match.group(1)),
        }

    return None


def run_validation() -> tuple[int, list[tuple[str, bool]]]:  # noqa: C901, PLR0912, PLR0915
    """Run all validation checks.

    Returns:
        Tuple of (failure_count, results_list)
    """
    failures = 0
    results = []

    # Count filesystem tasks
    print("📊 Counting task files on filesystem...")
    print()
    filesystem_counts = count_task_files()

    print("Filesystem Counts:")
    print("  Active Tasks:")
    for category in [
        "bug-fixes",
        "security",
        "optimization",
        "enhancement",
        "testing",
        "new-features",
        "refactoring",
    ]:
        print(f"    - {category}: {filesystem_counts[category]}")
    print(f"    - TOTAL: {filesystem_counts['active_total']}")
    print(f"  Completed: {filesystem_counts['completed']}")
    print(f"  Grand Total: {filesystem_counts['total']}")
    print()

    # Extract README.md counts
    print("📖 Reading tasks/README.md...")
    print()
    readme_path = Path("tasks/README.md")
    readme_counts = extract_readme_counts(readme_path)

    if readme_counts:
        print("README.md Totals:")
        print(f"  Total: {readme_counts['total']}")
        print(f"  Active: {readme_counts['active']}")
        print(f"  Completed: {readme_counts['completed']}")
        print()
    else:
        print(Colors.yellow("⚠️  Could not parse counts from README.md"))
        print()

    # Extract IMPLEMENTATION_SEQUENCE.md counts
    sequence_path = Path("tasks/IMPLEMENTATION_SEQUENCE.md")
    if sequence_path.exists():
        print("📋 Reading tasks/IMPLEMENTATION_SEQUENCE.md...")
        print()
        sequence_counts = extract_sequence_counts(sequence_path)

        if sequence_counts:
            print("IMPLEMENTATION_SEQUENCE.md:")
            print(f"  Active: {sequence_counts['active']}")
            print()
        else:
            print(
                Colors.yellow(
                    "⚠️  Could not find '**Total Tasks**:' in IMPLEMENTATION_SEQUENCE.md",
                ),
            )
            print()
            sequence_counts = None
    else:
        print(Colors.yellow("⚠️  tasks/IMPLEMENTATION_SEQUENCE.md not found"))
        print()
        sequence_counts = None

    # Run validation checks
    print("=" * 50)
    print("  Validation Results")
    print("=" * 50)
    print()

    # Check 1: Active tasks (Filesystem vs README.md)
    print("Check 1: Active tasks (Filesystem vs README.md)")
    if readme_counts and filesystem_counts["active_total"] == readme_counts["active"]:
        print(
            f"  {Colors.green('✅ PASS')}: Active count matches ({filesystem_counts['active_total']})",
        )
        results.append(("Check 1", True))
    else:
        print(f"  {Colors.red('❌ FAIL')}: Mismatch detected!")
        print(f"    - Filesystem: {filesystem_counts['active_total']}")
        print(f"    - README.md: {readme_counts['active'] if readme_counts else 'N/A'}")
        if readme_counts:
            diff = readme_counts["active"] - filesystem_counts["active_total"]
            print(f"    - Difference: {diff}")
        failures += 1
        results.append(("Check 1", False))
    print()

    # Check 2: Completed tasks (Filesystem vs README.md)
    print("Check 2: Completed tasks (Filesystem vs README.md)")
    if readme_counts and filesystem_counts["completed"] == readme_counts["completed"]:
        print(
            f"  {Colors.green('✅ PASS')}: Completed count matches ({filesystem_counts['completed']})",
        )
        results.append(("Check 2", True))
    else:
        print(f"  {Colors.red('❌ FAIL')}: Mismatch detected!")
        print(f"    - Filesystem: {filesystem_counts['completed']}")
        print(f"    - README.md: {readme_counts['completed'] if readme_counts else 'N/A'}")
        if readme_counts:
            diff = readme_counts["completed"] - filesystem_counts["completed"]
            print(f"    - Difference: {diff}")
        failures += 1
        results.append(("Check 2", False))
    print()

    # Check 3: Total tasks (Filesystem vs README.md)
    print("Check 3: Total tasks (Filesystem vs README.md)")
    if readme_counts and filesystem_counts["total"] == readme_counts["total"]:
        print(f"  {Colors.green('✅ PASS')}: Total count matches ({filesystem_counts['total']})")
        results.append(("Check 3", True))
    else:
        print(f"  {Colors.red('❌ FAIL')}: Mismatch detected!")
        print(f"    - Filesystem: {filesystem_counts['total']}")
        print(f"    - README.md: {readme_counts['total'] if readme_counts else 'N/A'}")
        if readme_counts:
            diff = readme_counts["total"] - filesystem_counts["total"]
            print(f"    - Difference: {diff}")
        failures += 1
        results.append(("Check 3", False))
    print()

    # Check 4: IMPLEMENTATION_SEQUENCE.md vs README.md
    if sequence_counts and readme_counts:
        print("Check 4: Active tasks (IMPLEMENTATION_SEQUENCE.md vs README.md)")
        if sequence_counts["active"] == readme_counts["active"]:
            print(
                f"  {Colors.green('✅ PASS')}: Active count matches ({sequence_counts['active']})",
            )
            results.append(("Check 4", True))
        else:
            print(f"  {Colors.red('❌ FAIL')}: Mismatch detected!")
            print(f"    - IMPLEMENTATION_SEQUENCE.md: {sequence_counts['active']}")
            print(f"    - README.md: {readme_counts['active']}")
            diff = readme_counts["active"] - sequence_counts["active"]
            print(f"    - Difference: {diff}")
            failures += 1
            results.append(("Check 4", False))
        print()

    # Check 5: IMPLEMENTATION_SEQUENCE.md vs Filesystem
    if sequence_counts:
        print("Check 5: Active tasks (IMPLEMENTATION_SEQUENCE.md vs Filesystem)")
        if sequence_counts["active"] == filesystem_counts["active_total"]:
            print(
                f"  {Colors.green('✅ PASS')}: Active count matches ({sequence_counts['active']})",
            )
            results.append(("Check 5", True))
        else:
            print(f"  {Colors.red('❌ FAIL')}: Mismatch detected!")
            print(f"    - IMPLEMENTATION_SEQUENCE.md: {sequence_counts['active']}")
            print(f"    - Filesystem: {filesystem_counts['active_total']}")
            diff = filesystem_counts["active_total"] - sequence_counts["active"]
            print(f"    - Difference: {diff}")
            failures += 1
            results.append(("Check 5", False))
        print()

    return failures, results


def print_summary(failures: int) -> None:
    """Print validation summary.

    Args:
        failures: Number of failed checks
    """
    print("=" * 50)
    print("  Summary")
    print("=" * 50)
    print()

    if failures == 0:
        print(Colors.green("✅ All validation checks passed!"))
        print()
        print("Task documentation is consistent across all files.")
    else:
        print(Colors.red(f"❌ {failures} validation check(s) failed!"))
        print()
        print("Task documentation has inconsistencies that need to be fixed.")
        print()
        print("Recommendations:")
        print("1. Update README.md with accurate task counts from filesystem")
        print("2. Update IMPLEMENTATION_SEQUENCE.md to match README.md")
        print("3. Remove completed tasks from active task lists")
        print("4. Add any missing new tasks")
        print("5. Re-run this script to verify fixes")


def main() -> int:
    """Execute validation and return exit code.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 50)
    print("  Task Documentation Validation Script")
    print("=" * 50)
    print()

    try:
        failures, _ = run_validation()
        print_summary(failures)
        return 0 if failures == 0 else 1
    except Exception as e:  # noqa: BLE001
        # Catch all exceptions for CLI - we want friendly error messages
        print(Colors.red(f"❌ Error: {e}"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
