#!/usr/bin/env python3
"""Automated dependency update script.

This script:
1. Checks for outdated dependencies in pre-commit hooks
2. Checks for outdated Python packages in pyproject.toml files
3. Updates pyproject.toml version constraints
4. Syncs tox.ini dependencies with pyproject.toml
5. Updates uv.lock with latest compatible versions
6. Reports available updates
7. Optionally applies updates
8. Runs tests to verify compatibility
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore[assignment]

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]


class UpdateInfo(NamedTuple):
    """Information about an available update."""

    current: str
    latest: str


class DependencyUpdater:
    """Manage dependency updates across the project."""

    def __init__(self, project_root: Path, pyproject_files: list[Path] | None = None) -> None:
        """Initialize with project root directory.

        Args:
            project_root: Path to project root directory
            pyproject_files: List of pyproject.toml files to update (default: [pyproject.toml, qa/web/pyproject.toml])
        """
        self.project_root = project_root
        self.pre_commit_config = project_root / ".pre-commit-config.yaml"

        # Default pyproject.toml files to check
        if pyproject_files is None:
            self.pyproject_files = [
                project_root / "pyproject.toml",
                project_root / "qa" / "web" / "pyproject.toml",
            ]
        else:
            self.pyproject_files = pyproject_files

        # Filter to only existing files
        self.pyproject_files = [f for f in self.pyproject_files if f.exists()]

        self.tox_ini = project_root / "tox.ini"

    def check_pre_commit_updates(self) -> dict[str, UpdateInfo]:
        """Check for pre-commit hook updates.

        Returns:
            Dict mapping repo URL to UpdateInfo (current_version, latest_version)
        """
        print("🔍 Checking pre-commit hook updates...")

        # Run pre-commit autoupdate with --freeze to see what would update
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

    def get_pypi_latest_version(self, package_name: str) -> str | None:
        """Get latest version of a package from PyPI.

        Args:
            package_name: Name of package to check

        Returns:
            Latest version string or None if check failed
        """
        if requests is None:
            return None

        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except Exception:
            return None

    def parse_pyproject_dependencies(self, pyproject_file: Path) -> dict[str, str]:
        """Parse dependencies from a pyproject.toml file.

        Args:
            pyproject_file: Path to pyproject.toml file

        Returns:
            Dict mapping package name to version constraint
        """
        with open(pyproject_file, "rb") as f:
            data = tomllib.load(f)

        deps: dict[str, str] = {}

        # Parse project dependencies
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                # Parse: "package>=1.0.0" or "package==1.0.0"
                match = re.match(r"^([a-zA-Z0-9_-]+)([><=!~]+)(.+)$", dep.strip())
                if match:
                    name, operator, version = match.groups()
                    deps[name] = f"{operator}{version}"

        # Parse optional dependencies
        if "project" in data and "optional-dependencies" in data["project"]:
            for group, group_deps in data["project"]["optional-dependencies"].items():
                for dep in group_deps:
                    match = re.match(r"^([a-zA-Z0-9_-]+)([><=!~]+)(.+)$", dep.strip())
                    if match:
                        name, operator, version = match.groups()
                        if name not in deps:  # Don't override main deps
                            deps[name] = f"{operator}{version}"

        return deps

    def check_pyproject_updates(self, pyproject_file: Path) -> dict[str, UpdateInfo]:
        """Check for updates to packages in a pyproject.toml file.

        Args:
            pyproject_file: Path to pyproject.toml file

        Returns:
            Dict mapping package name to UpdateInfo
        """
        deps = self.parse_pyproject_dependencies(pyproject_file)
        updates: dict[str, UpdateInfo] = {}

        for package, constraint in deps.items():
            # Extract current version from constraint
            version_match = re.search(r"[\d.]+", constraint)
            if not version_match:
                continue

            current = version_match.group()
            latest = self.get_pypi_latest_version(package)

            if latest and latest != current:
                updates[package] = UpdateInfo(current=current, latest=latest)

        return updates

    def check_all_pyproject_updates(self) -> dict[Path, dict[str, UpdateInfo]]:
        """Check for updates across all pyproject.toml files.

        Returns:
            Dict mapping pyproject.toml path to its updates
        """
        print("🔍 Checking pyproject.toml dependency updates...")

        all_updates: dict[Path, dict[str, UpdateInfo]] = {}

        for pyproject_file in self.pyproject_files:
            print(f"   Checking {pyproject_file.relative_to(self.project_root)}...")
            updates = self.check_pyproject_updates(pyproject_file)
            if updates:
                all_updates[pyproject_file] = updates

        return all_updates

    def check_python_package_updates(self) -> dict[str, UpdateInfo]:
        """Check for Python package updates using pip.

        Returns:
            Dict mapping package name to UpdateInfo (current_version, latest_version)
        """
        print("🔍 Checking installed package updates...")

        # Use pip list --outdated
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return {}

        try:
            outdated = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}

        updates: dict[str, UpdateInfo] = {}
        for package in outdated:
            name = package["name"]
            current = package["version"]
            latest = package["latest_version"]
            updates[name] = UpdateInfo(current=current, latest=latest)

        return updates

    def update_pyproject_toml(self, pyproject_file: Path, updates: dict[str, UpdateInfo]) -> bool:
        """Update dependency versions in a pyproject.toml file.

        Args:
            pyproject_file: Path to pyproject.toml file
            updates: Dict of package updates to apply

        Returns:
            True if successful, False otherwise
        """
        if not tomli_w:
            print("⚠️  tomli_w not available, cannot update pyproject.toml")
            return False

        try:
            # Read current pyproject.toml
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)

            # Update project dependencies
            if "project" in data and "dependencies" in data["project"]:
                updated_deps = []
                for dep in data["project"]["dependencies"]:
                    match = re.match(r"^([a-zA-Z0-9_-]+)([><=!~]+)(.+)$", dep.strip())
                    if match:
                        name, operator, _version = match.groups()
                        if name in updates:
                            # Update to latest version
                            new_version = updates[name].latest
                            updated_deps.append(f"{name}{operator}{new_version}")
                            print(f"  Updated {name}: {updates[name].current} → {new_version}")
                        else:
                            updated_deps.append(dep)
                    else:
                        updated_deps.append(dep)

                data["project"]["dependencies"] = updated_deps

            # Update optional dependencies
            if "project" in data and "optional-dependencies" in data["project"]:
                for group in data["project"]["optional-dependencies"]:
                    updated_deps = []
                    for dep in data["project"]["optional-dependencies"][group]:
                        match = re.match(r"^([a-zA-Z0-9_-]+)([><=!~]+)(.+)$", dep.strip())
                        if match:
                            name, operator, _version = match.groups()
                            if name in updates:
                                new_version = updates[name].latest
                                updated_deps.append(f"{name}{operator}{new_version}")
                                print(
                                    f"  Updated {name} in [{group}]: "
                                    f"{updates[name].current} → {new_version}"
                                )
                            else:
                                updated_deps.append(dep)
                        else:
                            updated_deps.append(dep)

                    data["project"]["optional-dependencies"][group] = updated_deps

            # Write updated pyproject.toml
            with open(pyproject_file, "wb") as f:
                tomli_w.dump(data, f)

            return True

        except Exception as e:
            print(f"❌ Failed to update {pyproject_file}: {e}")
            return False

    def sync_tox_ini(self) -> bool:
        """Sync tox.ini dependencies with main pyproject.toml.

        Returns:
            True if successful, False otherwise
        """
        print("\n🔄 Syncing tox.ini with pyproject.toml...")

        try:
            # Read main pyproject.toml dependencies
            main_pyproject = self.project_root / "pyproject.toml"
            deps = self.parse_pyproject_dependencies(main_pyproject)

            # Read tox.ini
            config = configparser.ConfigParser()
            config.read(self.tox_ini)

            # Update deps in relevant testenv sections
            updated = False
            for section in config.sections():
                if section.startswith("testenv"):
                    if "deps" in config[section]:
                        # Parse current deps
                        current_deps = [
                            line.strip()
                            for line in config[section]["deps"].split("\n")
                            if line.strip()
                        ]

                        # Update versions based on pyproject.toml
                        new_deps = []
                        for dep in current_deps:
                            match = re.match(r"^([a-zA-Z0-9_-]+)([><=!~]+)(.+)$", dep)
                            if match:
                                name, operator, _version = match.groups()
                                if name in deps:
                                    # Use version from pyproject.toml
                                    new_deps.append(f"{name}{deps[name]}")
                                    updated = True
                                else:
                                    new_deps.append(dep)
                            else:
                                new_deps.append(dep)

                        if updated:
                            config[section]["deps"] = "\n" + "\n".join(new_deps)

            if updated:
                # Write updated tox.ini
                with open(self.tox_ini, "w") as f:
                    config.write(f)
                print("  ✅ tox.ini synced with pyproject.toml")
            else:
                print("  ℹ️  tox.ini already in sync")

            return True

        except Exception as e:
            print(f"❌ Failed to sync tox.ini: {e}")
            return False

    def report_updates(
        self,
        pre_commit_updates: dict[str, UpdateInfo],
        pyproject_updates: dict[Path, dict[str, UpdateInfo]],
        python_updates: dict[str, UpdateInfo],
    ) -> None:
        """Display available updates in formatted table.

        Args:
            pre_commit_updates: Pre-commit hook updates
            pyproject_updates: pyproject.toml dependency updates (per file)
            python_updates: Installed package updates
        """
        print("\n" + "=" * 80)
        print("📦 DEPENDENCY UPDATE REPORT")
        print("=" * 80)

        if pre_commit_updates:
            print("\n🔧 Pre-commit Hook Updates Available:")
            print("-" * 80)
            for repo, update in pre_commit_updates.items():
                repo_name = repo.split("/")[-1]
                print(f"  {repo_name:40s} {update.current:12s} → {update.latest:12s}")
        else:
            print("\n✅ All pre-commit hooks are up to date!")

        if pyproject_updates:
            for pyproject_file, updates in pyproject_updates.items():
                rel_path = pyproject_file.relative_to(self.project_root)
                print(f"\n📄 {rel_path} Dependency Updates Available:")
                print("-" * 80)
                for pkg, update in updates.items():
                    old_major = update.current.split(".")[0] if "." in update.current else "0"
                    new_major = update.latest.split(".")[0] if "." in update.latest else "0"
                    breaking = "⚠️  MAJOR" if old_major != new_major else ""

                    print(f"  {pkg:40s} {update.current:12s} → {update.latest:12s} {breaking}")
        else:
            print("\n✅ All pyproject.toml files are up to date!")

        if python_updates:
            # Collect all packages already shown in pyproject updates
            shown_packages = set()
            for updates in pyproject_updates.values():
                shown_packages.update(updates.keys())

            # Only show packages not in pyproject.toml files
            new_updates = {k: v for k, v in python_updates.items() if k not in shown_packages}

            if new_updates:
                print("\n🐍 Other Installed Package Updates Available:")
                print("-" * 80)
                for pkg, update in new_updates.items():
                    old_major = update.current.split(".")[0] if "." in update.current else "0"
                    new_major = update.latest.split(".")[0] if "." in update.latest else "0"
                    breaking = "⚠️  MAJOR" if old_major != new_major else ""

                    print(f"  {pkg:40s} {update.current:12s} → {update.latest:12s} {breaking}")

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
        """Apply Python package updates (uv lock --upgrade).

        Returns:
            True if successful, False otherwise
        """
        print("\n🔄 Updating uv.lock...")

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
    """Execute the dependency update process.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Check and update project dependencies across all config files",
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

What gets updated:
  - .pre-commit-config.yaml: Hook versions
  - pyproject.toml: Dependency version constraints (main project)
  - qa/web/pyproject.toml: Dependency version constraints (QA tests)
  - tox.ini: Synced with main pyproject.toml
  - uv.lock: Regenerated with latest compatible versions
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
        help="Apply available updates to all files",
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

    # Check dependencies
    if not tomli_w:
        print("⚠️  Warning: tomli_w not installed. Install with: pip install tomli-w")
        print("    pyproject.toml updates will not be available.")

    if not requests:
        print("⚠️  Warning: requests not installed. Install with: pip install requests")
        print("    PyPI version checking will not be available.")

    updater = DependencyUpdater(args.project_root)

    try:
        # Check for updates
        pre_commit_updates = updater.check_pre_commit_updates()
        pyproject_updates = updater.check_all_pyproject_updates()
        python_updates = updater.check_python_package_updates()

        # Report findings
        updater.report_updates(pre_commit_updates, pyproject_updates, python_updates)

        # Apply updates if requested
        if args.apply:
            has_updates = pre_commit_updates or pyproject_updates or python_updates

            if has_updates:
                print("\n⚠️  About to apply updates to:")
                if pre_commit_updates:
                    print("   - .pre-commit-config.yaml")
                if pyproject_updates:
                    for pyproject_file in pyproject_updates.keys():
                        rel_path = pyproject_file.relative_to(args.project_root)
                        print(f"   - {rel_path}")
                    print("   - tox.ini (synced)")
                if python_updates or pyproject_updates:
                    print("   - uv.lock")
                print("\nContinue? [y/N] ", end="")
                response = input().strip().lower()

                if response != "y":
                    print("❌ Update cancelled by user")
                    return 1

                # Apply pre-commit updates
                if pre_commit_updates:
                    if not updater.apply_pre_commit_updates():
                        print("❌ Pre-commit update failed!")
                        return 1

                # Apply pyproject.toml updates
                if pyproject_updates:
                    for pyproject_file, updates in pyproject_updates.items():
                        rel_path = pyproject_file.relative_to(args.project_root)
                        print(f"\n🔄 Updating {rel_path}...")
                        if not updater.update_pyproject_toml(pyproject_file, updates):
                            print(f"❌ {rel_path} update failed!")
                            return 1

                    # Sync tox.ini (only with main pyproject.toml)
                    if not updater.sync_tox_ini():
                        print("⚠️  tox.ini sync failed (non-fatal)")

                # Apply Python package updates (uv lock)
                if pyproject_updates or python_updates:
                    if not updater.apply_python_updates():
                        print("❌ uv lock update failed!")
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
                print("\nFiles updated:")
                if pre_commit_updates:
                    print("  - .pre-commit-config.yaml")
                if pyproject_updates:
                    for pyproject_file in pyproject_updates.keys():
                        rel_path = pyproject_file.relative_to(args.project_root)
                        print(f"  - {rel_path}")
                    print("  - tox.ini")
                if python_updates or pyproject_updates:
                    print("  - uv.lock")
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
