#!/usr/bin/env python3
"""Automated dependency update script.

This script:
1. Checks for outdated dependencies in pre-commit hooks
2. Checks for outdated Python packages
3. Reports available updates
4. Optionally applies updates
5. Runs tests to verify compatibility
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class UpdateInfo(NamedTuple):
    """Information about an available update."""

    current: str
    latest: str


class DependencyUpdater:
    """Manage dependency updates across the project."""

    def __init__(self, project_root: Path) -> None:
        """Initialize with project root directory.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.pre_commit_config = project_root / ".pre-commit-config.yaml"
        self.pyproject_toml = project_root / "pyproject.toml"
        self.tox_ini = project_root / "tox.ini"

    def check_pre_commit_updates(self) -> dict[str, UpdateInfo]:
        """Check for pre-commit hook updates.

        Returns:
            Dict mapping repo URL to UpdateInfo (current_version, latest_version)
        """
        print("🔍 Checking pre-commit hook updates...")

        # Run pre-commit autoupdate
        result = subprocess.run(
            ["pre-commit", "autoupdate"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        updates: dict[str, UpdateInfo] = {}
        for line in result.stdout.splitlines():
            # Parse: "updating https://... from v1.0.0 to v1.1.0"
            if "updating" in line and "from" in line and "to" in line:
                parts = line.split()
                repo_url = parts[1]
                old_ver = parts[3]
                new_ver = parts[5]
                updates[repo_url] = UpdateInfo(current=old_ver, latest=new_ver)

        return updates

    def check_python_package_updates(self) -> dict[str, UpdateInfo]:
        """Check for Python package updates.

        Returns:
            Dict mapping package name to UpdateInfo (current_version, latest_version)
        """
        print("🔍 Checking Python package updates...")

        # Use pip list --outdated
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"⚠️  Warning: pip list failed: {result.stderr}")
            return {}

        try:
            outdated = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("⚠️  Warning: Could not parse pip list output")
            return {}

        updates: dict[str, UpdateInfo] = {}
        for package in outdated:
            name = package["name"]
            current = package["version"]
            latest = package["latest_version"]
            updates[name] = UpdateInfo(current=current, latest=latest)

        return updates

    def check_uv_updates(self) -> dict[str, UpdateInfo]:
        """Check for UV package updates.

        Returns:
            Dict mapping package name to UpdateInfo (current_version, latest_version)
        """
        print("🔍 Checking UV package updates...")

        # Run uv lock --dry-run to see what would be updated
        # Unfortunately UV doesn't have a direct outdated check yet
        # So we'll use pip list for now
        return {}

    def report_updates(
        self,
        pre_commit_updates: dict[str, UpdateInfo],
        python_updates: dict[str, UpdateInfo],
    ) -> None:
        """Display available updates in formatted table.

        Args:
            pre_commit_updates: Pre-commit hook updates
            python_updates: Python package updates
        """
        print("\n" + "=" * 80)
        print("📦 DEPENDENCY UPDATE REPORT")
        print("=" * 80)

        if pre_commit_updates:
            print("\n🔧 Pre-commit Hook Updates Available:")
            print("-" * 80)
            for repo, update in pre_commit_updates.items():
                # Shorten repo URL for display
                repo_name = repo.split("/")[-1]
                print(f"  {repo_name:40s} {update.current:12s} → {update.latest:12s}")
        else:
            print("\n✅ All pre-commit hooks are up to date!")

        if python_updates:
            print("\n🐍 Python Package Updates Available:")
            print("-" * 80)
            for pkg, update in python_updates.items():
                # Check if major version change (basic check)
                old_major = update.current.split(".")[0] if "." in update.current else "0"
                new_major = update.latest.split(".")[0] if "." in update.latest else "0"
                breaking = "⚠️  MAJOR" if old_major != new_major else ""

                print(f"  {pkg:40s} {update.current:12s} → {update.latest:12s} {breaking}")
        else:
            print("\n✅ All Python packages are up to date!")

        print("\n" + "=" * 80)

    def apply_pre_commit_updates(self) -> bool:
        """Apply pre-commit hook updates.

        Returns:
            True if successful, False otherwise
        """
        print("\n🔄 Applying pre-commit updates...")

        result = subprocess.run(
            ["pre-commit", "autoupdate"],
            cwd=self.project_root,
            check=False,
        )

        return result.returncode == 0

    def apply_python_updates(self) -> bool:
        """Apply Python package updates.

        Returns:
            True if successful, False otherwise
        """
        print("\n🔄 Applying Python package updates...")

        # Use uv to upgrade packages
        result = subprocess.run(
            ["uv", "lock", "--upgrade"],
            cwd=self.project_root,
            check=False,
        )

        return result.returncode == 0

    def run_tests(self) -> bool:
        """Run test suite to verify updates don't break anything.

        Returns:
            True if tests pass, False otherwise
        """
        print("\n🧪 Running tests to verify updates...")

        # Run pytest
        result = subprocess.run(
            ["pytest", "-x"],  # Stop on first failure
            cwd=self.project_root,
            check=False,
        )

        return result.returncode == 0

    def run_tox(self) -> bool:
        """Run tox to verify updates across all environments.

        Returns:
            True if all environments pass, False otherwise
        """
        print("\n🧪 Running tox to verify updates...")

        result = subprocess.run(
            ["tox", "-p", "auto"],
            cwd=self.project_root,
            check=False,
        )

        return result.returncode == 0


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Check and update project dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for updates (dry run)
  python scripts/update_dependencies.py --check

  # Apply all updates
  python scripts/update_dependencies.py --apply

  # Apply updates and run tests
  python scripts/update_dependencies.py --apply --test

  # Apply updates, run tests, and full tox validation
  python scripts/update_dependencies.py --apply --test --tox
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for updates without applying (default)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply available updates",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests after applying updates",
    )
    parser.add_argument(
        "--tox",
        action="store_true",
        help="Run full tox validation after updates",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Default to check mode if no action specified
    if not args.check and not args.apply:
        args.check = True

    updater = DependencyUpdater(args.project_root)

    try:
        # Check for updates
        pre_commit_updates = updater.check_pre_commit_updates()
        python_updates = updater.check_python_package_updates()

        # Report findings
        updater.report_updates(pre_commit_updates, python_updates)

        # Apply updates if requested
        if args.apply:
            if pre_commit_updates or python_updates:
                print("\n⚠️  About to apply updates. Continue? [y/N] ", end="")
                response = input().strip().lower()

                if response != "y":
                    print("❌ Update cancelled by user")
                    return 1

                # Apply pre-commit updates
                if pre_commit_updates:
                    if not updater.apply_pre_commit_updates():
                        print("❌ Pre-commit update failed!")
                        return 1

                # Apply Python updates
                if python_updates:
                    if not updater.apply_python_updates():
                        print("❌ Python package update failed!")
                        return 1

                print("\n✅ Updates applied successfully!")

                # Run tests if requested
                if args.test:
                    if not updater.run_tests():
                        print("\n❌ Tests failed! Consider reverting updates.")
                        return 1
                    print("\n✅ Tests passed!")

                # Run tox if requested
                if args.tox:
                    if not updater.run_tox():
                        print("\n❌ Tox validation failed! Review failures.")
                        return 1
                    print("\n✅ Tox validation passed!")

                print("\n" + "=" * 80)
                print("✅ DEPENDENCY UPDATE COMPLETE")
                print("=" * 80)
                print("\nNext steps:")
                print("1. Review changes: git diff")
                print("2. Test manually: make test")
                print("3. Commit changes: git commit -m 'chore: Update dependencies'")
                print("4. Push: git push")
            else:
                print("\n✅ All dependencies are already up to date!")

        return 0

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
