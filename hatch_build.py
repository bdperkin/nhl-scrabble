"""Hatch build hook to compile translation files during package build."""

# ruff: noqa: T201, S603, S607
# T201: print() is appropriate for build-time output
# S603/S607: subprocess call to pybabel is trusted build tool

import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CompileTranslationsBuildHook(BuildHookInterface):
    """Build hook to compile .po files to .mo files."""

    PLUGIN_NAME = "compile-translations"

    def initialize(self, _version: str, _build_data: dict) -> None:
        """Compile translation files before building the package.

        Args:
            _version: Package version (unused, required by interface)
            _build_data: Build metadata (unused, required by interface)
        """
        locales_dir = Path("src/nhl_scrabble/locales")

        if not locales_dir.exists():
            return

        # Find all .po files and compile them
        for po_file in locales_dir.rglob("*.po"):
            locale_name = po_file.parent.parent.name

            print(f"Compiling {locale_name} translations...")

            try:
                subprocess.run(
                    [
                        "pybabel",
                        "compile",
                        "-d",
                        str(locales_dir),
                        "-l",
                        locale_name,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"✓ Compiled {locale_name}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to compile {locale_name}: {e.stderr}")
            except FileNotFoundError:
                print("Warning: pybabel not found. Install babel to compile translations.")
                print("Skipping translation compilation...")
                break
