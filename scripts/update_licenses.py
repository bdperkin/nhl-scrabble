#!/usr/bin/env python3
"""Automated license tracking and LICENSES.md update script.

This script:
1. Generates current dependency license list using pip-licenses
2. Deduplicates license entries (pip-licenses outputs duplicates)
3. Validates no prohibited licenses in runtime dependencies
4. Updates LICENSES.md with current license information
5. Checks if LICENSES.md is up-to-date with current dependencies
"""

# ruff: noqa: T201, RUF012, S607, PERF401, BLE001, PLC0415

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class LicenseEntry(NamedTuple):
    """A single license entry from pip-licenses."""

    name: str
    version: str
    license: str


class LicenseUpdater:
    """Manages license tracking and LICENSES.md updates."""

    # Header ends at line 49 (inclusive), table starts at line 50
    HEADER_END_LINE = 49
    LICENSES_FILE = Path("LICENSES.md")

    # Prohibited licenses for runtime dependencies
    PROHIBITED_LICENSES = {"GPL", "AGPL", "LGPL", "Proprietary"}

    # Allowed exceptions (dev-only dependencies)
    ALLOWED_EXCEPTIONS = {
        "blocklint",
        "CairoSVG",
        "pyenchant",
        "docutils",
        "LinkChecker",
        "Unidecode",
        "djlint",
        "docformatter",
        "refurb",
        "dicttoxml",
    }

    def __init__(self, verbose: bool = False) -> None:
        """Initialize the license updater.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

    def _log(self, message: str) -> None:
        """Log message if verbose mode enabled.

        Args:
            message: Message to log
        """
        if self.verbose:
            print(message, file=sys.stderr)

    def generate_license_list(self) -> list[LicenseEntry]:
        """Generate current license list using pip-licenses.

        Returns:
            List of LicenseEntry objects (deduplicated)

        Raises:
            RuntimeError: If pip-licenses command fails
        """
        self._log("Generating license list with pip-licenses...")

        try:
            result = subprocess.run(
                ["pip-licenses", "--format=markdown", "--order=name"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"pip-licenses failed: {e.stderr}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                "pip-licenses not found. Install with: pip install pip-licenses",
            ) from e

        # Parse markdown table and deduplicate
        lines = result.stdout.strip().split("\n")
        entries: list[LicenseEntry] = []
        seen: set[tuple[str, str, str]] = set()

        for line in lines[2:]:  # Skip header rows
            if not line.strip() or not line.startswith("|"):
                continue

            # Parse table row: | Name | Version | License |
            parts = [p.strip() for p in line.split("|")[1:-1]]  # Remove outer pipes
            if len(parts) != 3:
                continue

            name, version, license_text = parts

            # Skip continuation rows (empty name/version from multi-line license text)
            if not name or not version:
                continue

            entry_tuple = (name, version, license_text)

            # Deduplicate
            if entry_tuple not in seen:
                seen.add(entry_tuple)
                entries.append(LicenseEntry(name, version, license_text))

        self._log(f"Found {len(entries)} unique dependencies")
        return entries

    def validate_licenses(self, entries: list[LicenseEntry]) -> list[str]:
        """Validate no prohibited licenses in runtime dependencies.

        Args:
            entries: List of license entries to validate

        Returns:
            List of validation errors (empty if valid)
        """
        self._log("Validating licenses...")
        errors: list[str] = []

        for entry in entries:
            # Skip allowed exceptions (dev-only dependencies)
            if entry.name in self.ALLOWED_EXCEPTIONS:
                continue

            # Check for prohibited licenses
            for prohibited in self.PROHIBITED_LICENSES:
                if prohibited.upper() in entry.license.upper():
                    errors.append(
                        f"Prohibited license '{prohibited}' found in "
                        f"{entry.name} {entry.version}: {entry.license}",
                    )

        if errors:
            self._log(f"Found {len(errors)} license validation errors")
        else:
            self._log("All licenses valid ✓")

        return errors

    def format_license_table(self, entries: list[LicenseEntry]) -> str:
        """Format license entries as markdown table.

        Args:
            entries: List of license entries

        Returns:
            Markdown table string
        """
        # Calculate column widths
        max_name = max(len(e.name) for e in entries)
        max_version = max(len(e.version) for e in entries)
        max_license = max(len(e.license) for e in entries)

        # Ensure minimum widths match header
        max_name = max(max_name, len("Name"))
        max_version = max(max_version, len("Version"))
        max_license = max(max_license, len("License"))

        # Build table
        lines = [
            f"| {'Name':<{max_name}} | {'Version':<{max_version}} | {'License':<{max_license}} |",
            f"| {'-' * max_name} | {'-' * max_version} | {'-' * max_license} |",
        ]

        for entry in entries:
            lines.append(
                f"| {entry.name:<{max_name}} | {entry.version:<{max_version}} | {entry.license:<{max_license}} |",
            )

        return "\n".join(lines)

    def read_header(self) -> str:
        """Read the header section of LICENSES.md.

        Returns:
            Header content (lines 1-49)

        Raises:
            FileNotFoundError: If LICENSES.md doesn't exist
        """
        if not self.LICENSES_FILE.exists():
            raise FileNotFoundError(f"{self.LICENSES_FILE} not found")

        with self.LICENSES_FILE.open() as f:
            lines = f.readlines()

        if len(lines) < self.HEADER_END_LINE:
            raise RuntimeError(f"{self.LICENSES_FILE} has fewer than {self.HEADER_END_LINE} lines")

        return "".join(lines[: self.HEADER_END_LINE])

    def update_licenses_file(self, entries: list[LicenseEntry]) -> None:
        """Update LICENSES.md with current license information.

        Args:
            entries: List of license entries to write

        Raises:
            FileNotFoundError: If LICENSES.md doesn't exist
        """
        self._log(f"Updating {self.LICENSES_FILE}...")

        # Read header
        header = self.read_header()

        # Format table
        table = self.format_license_table(entries)

        # Write new file
        with self.LICENSES_FILE.open("w") as f:
            f.write(header)
            f.write(table)
            f.write("\n")

        self._log(f"Updated {self.LICENSES_FILE} ✓")

    def check_up_to_date(self, entries: list[LicenseEntry]) -> bool:
        """Check if LICENSES.md is up-to-date with current dependencies.

        Args:
            entries: Current license entries

        Returns:
            True if up-to-date, False otherwise
        """
        self._log("Checking if LICENSES.md is up-to-date...")

        # Read current table section
        if not self.LICENSES_FILE.exists():
            self._log(f"{self.LICENSES_FILE} doesn't exist")
            return False

        with self.LICENSES_FILE.open() as f:
            lines = f.readlines()

        if len(lines) <= self.HEADER_END_LINE:
            self._log(f"{self.LICENSES_FILE} has no table section")
            return False

        current_table = "".join(lines[self.HEADER_END_LINE :]).strip()
        expected_table = self.format_license_table(entries).strip()

        if current_table == expected_table:
            self._log("LICENSES.md is up-to-date ✓")
            return True
        self._log("LICENSES.md is OUT OF DATE")
        return False


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Update and validate LICENSES.md with current dependency licenses",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if LICENSES.md is up-to-date (exit 1 if not)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update LICENSES.md with current licenses",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate licenses only (no update)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Default: update if no action specified
    if not (args.check or args.update or args.validate):
        args.update = True

    return args


def _print_validation_errors(errors: list[str]) -> None:
    """Print validation errors to stderr.

    Args:
        errors: List of validation error messages
    """
    print("License validation FAILED:", file=sys.stderr)
    for error in errors:
        print(f"  ✗ {error}", file=sys.stderr)


def _handle_check_mode(updater: LicenseUpdater, entries: list[LicenseEntry]) -> int:
    """Handle --check mode.

    Args:
        updater: LicenseUpdater instance
        entries: License entries to check

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not updater.check_up_to_date(entries):
        print(
            f"ERROR: {updater.LICENSES_FILE} is out of date. "
            f"Run: python scripts/update_licenses.py --update",
            file=sys.stderr,
        )
        return 1
    print(f"{updater.LICENSES_FILE} is up-to-date ✓")
    return 0


def _handle_update_mode(updater: LicenseUpdater, entries: list[LicenseEntry]) -> int:
    """Handle --update mode.

    Args:
        updater: LicenseUpdater instance
        entries: License entries to write

    Returns:
        Exit code (0 for success)
    """
    updater.update_licenses_file(entries)
    print(f"Updated {updater.LICENSES_FILE} with {len(entries)} dependencies ✓")
    return 0


def _handle_validate_mode(entries: list[LicenseEntry]) -> int:
    """Handle --validate mode.

    Args:
        entries: License entries that were validated

    Returns:
        Exit code (0 for success)
    """
    print(f"All {len(entries)} dependency licenses are valid ✓")
    return 0


def main() -> int:
    """Run the license updater CLI.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = _parse_args()
    updater = LicenseUpdater(verbose=args.verbose)

    try:
        # Generate current license list
        entries = updater.generate_license_list()

        # Validate licenses
        errors = updater.validate_licenses(entries)
        if errors:
            _print_validation_errors(errors)
            return 1

        # Execute requested mode
        if args.check:
            return _handle_check_mode(updater, entries)
        if args.update:
            return _handle_update_mode(updater, entries)
        if args.validate:
            return _handle_validate_mode(entries)

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
