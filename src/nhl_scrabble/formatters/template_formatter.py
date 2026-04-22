"""Template output formatter.

Converts NHL Scrabble analysis data using custom Jinja2 templates, allowing users to create fully
customized output formats.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TemplateFormatter:
    """Format analysis data using custom Jinja2 templates.

    Loads a user-provided Jinja2 template and renders it with analysis data,
    allowing complete customization of output format.

    Args:
        template_file: Path to Jinja2 template file

    Raises:
        ValueError: If template_file is not provided
        FileNotFoundError: If template file doesn't exist

    Example:
        >>> formatter = TemplateFormatter(template_file="custom.j2")
        >>> output = formatter.format(data)
    """

    def __init__(self, template_file: str | None = None) -> None:
        """Initialize template formatter.

        Args:
            template_file: Path to Jinja2 template file (required)

        Raises:
            ValueError: If template_file is None or empty
            FileNotFoundError: If template file doesn't exist
        """
        if not template_file:
            raise ValueError(
                "template_file is required for TemplateFormatter. "
                "Provide with: get_formatter('template', template_file='path/to/template.j2')"
            )

        self.template_path = Path(template_file)

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")

    def format(self, data: dict[str, Any]) -> str:
        """Format data using custom Jinja2 template.

        Args:
            data: Analysis data dictionary with structure:
                {
                    "teams": {...},
                    "divisions": {...},
                    "conferences": {...},
                    "playoffs": {...},
                    "summary": {...}
                }

        Returns:
            Rendered template string with data injected

        Raises:
            ImportError: If jinja2 is not installed
            jinja2.TemplateError: If template has syntax errors

        Example:
            >>> formatter = TemplateFormatter(template_file="custom.j2")
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
        """
        try:
            from jinja2 import Template  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(
                "Jinja2 is required for template format. Install with: pip install jinja2"
            ) from e

        # Read template file
        template_content = self.template_path.read_text()

        # Create template
        template = Template(template_content)

        # Add timestamp to data
        template_data = {
            **data,
            "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        # Render template
        return template.render(template_data)  # type: ignore[no-any-return]  # Jinja2 Template.render() returns str
