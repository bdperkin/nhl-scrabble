"""YAML output formatter.

Converts NHL Scrabble analysis data to YAML format for human-readable structured data that's easy to
read and edit.
"""

from __future__ import annotations

from typing import Any


class YAMLFormatter:
    """Format analysis data as YAML.

    Produces human-readable YAML output with proper indentation and structure,
    suitable for configuration files or human review.

    Example:
        >>> formatter = YAMLFormatter()
        >>> output = formatter.format(data)
        >>> "teams:" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to YAML string.

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
            YAML formatted string with proper indentation

        Raises:
            ImportError: If PyYAML is not installed

        Example:
            >>> formatter = YAMLFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "TOR" in output
            True
        """
        try:
            import yaml
        except ImportError as e:
            raise ImportError(
                "PyYAML is required for YAML format. Install with: pip install pyyaml"
            ) from e

        # Use safe_dump with proper formatting options
        return yaml.dump(
            data,
            default_flow_style=False,  # Use block style (not inline)
            sort_keys=False,  # Preserve order
            allow_unicode=True,  # Support Unicode characters
        )
