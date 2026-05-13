"""CLI argument validation utilities."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import click

from nhl_scrabble.exceptions import ValidationError
from nhl_scrabble.i18n import _
from nhl_scrabble.validators import validate_file_path

logger = logging.getLogger(__name__)


def validate_output_path(output: str | None) -> None:
    """Validate that output path is writable before processing.

    Checks that the output path's parent directory exists and is writable,
    and that any existing file at the path is also writable. This validation
    happens before any API calls to provide immediate feedback on path issues.

    Args:
        output: Output file path, or None for stdout.

    Raises:
        click.ClickException: If output path is not writable, with helpful
            error message explaining the issue and how to fix it.

    Example:
        >>> validate_output_path("/tmp/output.txt")  # OK
        >>> validate_output_path(None)  # OK (stdout)
        >>> validate_output_path("/nonexistent/dir/file.txt")  # Raises
        ClickException: Output directory does not exist: /nonexistent/dir
        Create it first: mkdir -p /nonexistent/dir
    """
    if output is None:
        return  # stdout is always writable

    # Resolve to absolute path
    output_path = Path(output).resolve()
    output_dir = output_path.parent

    # Check if directory exists
    if not output_dir.exists():
        raise click.ClickException(
            _(
                "Output directory does not exist: {output_dir}\nCreate it first: mkdir -p {output_dir}",
            ).format(output_dir=output_dir),
        )

    # Check if directory is writable
    if not os.access(output_dir, os.W_OK):
        raise click.ClickException(
            _(
                "Output directory is not writable: {output_dir}\nCheck permissions with: ls -ld {output_dir}",
            ).format(output_dir=output_dir),
        )

    # Check if file exists and is writable
    if output_path.exists():
        if not os.access(output_path, os.W_OK):
            raise click.ClickException(
                _(
                    "Output file exists but is not writable: {output_path}\nCheck permissions with: ls -l {output_path}",
                ).format(output_path=output_path),
            )

        # Warn if file will be overwritten
        logger.warning(f"Output file exists and will be overwritten: {output_path}")


def validate_cli_arguments(output: str | None) -> Path | None:
    """Validate CLI output path before processing.

    Uses validators module to check output path for security issues.
    This validation happens before any API calls to provide immediate feedback.

    Note:
        Numeric validation (top_players, top_team_players, etc.) is now handled
        by Click's IntRange type directly in option definitions, eliminating
        redundant validation.

    Args:
        output: Output file path, or None for stdout

    Returns:
        Validated output path, or None for stdout

    Raises:
        click.ClickException: If output path is invalid with helpful error message

    Security:
        - Prevents path traversal attacks via output path
        - Provides early validation before expensive operations

    Examples:
        >>> validate_cli_arguments("output.txt")
        PosixPath('/current/dir/output.txt')
        >>> validate_cli_arguments(None)  # stdout
        None
    """
    validated_output: Path | None = None

    try:
        # Validate output path if provided
        if output:
            # Allow overwrite since we'll warn the user
            validated_output = validate_file_path(output, allow_overwrite=True)
            if validated_output.exists():
                logger.warning(f"Output file exists and will be overwritten: {validated_output}")

        return validated_output

    except ValidationError as e:
        raise click.ClickException(str(e)) from e
