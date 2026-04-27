"""Output formatters for NHL Scrabble analysis.

This module provides a collection of output formatters for converting NHL Scrabble
analysis data into various formats (JSON, YAML, XML, HTML, CSV, Markdown, etc.).
All formatters implement the OutputFormatter protocol defined below.

Example:
    >>> from nhl_scrabble.formatters import get_formatter
    >>> formatter = get_formatter('json')
    >>> output = formatter.format(data)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Any


class OutputFormatter(Protocol):
    """Protocol for output formatters.

    All formatters must implement this protocol's format() method to convert
    analysis data dictionaries into formatted string output.

    Example:
        >>> class MyFormatter:
        ...     def format(self, data: dict[str, Any]) -> str:
        ...         return str(data)
        >>> formatter = MyFormatter()
        >>> result = formatter.format({"teams": []})
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to string output.

        Args:
            data: Analysis data dictionary containing teams, players, standings, etc.

        Returns:
            Formatted string output in the formatter's target format.

        Raises:
            ValueError: If data is invalid or missing required fields.
        """

__all__ = [
    "OutputFormatter",
    "get_formatter",
]


def get_formatter(format_type: str, **kwargs: Any) -> OutputFormatter:
    """Get formatter instance for specified format.

    This is a convenience function that imports and returns the appropriate
    formatter class from the factory module.

    Args:
        format_type: Format type (text, json, yaml, xml, html, table, markdown, csv, template)
        **kwargs: Additional arguments passed to formatter constructor

    Returns:
        Formatter instance implementing OutputFormatter protocol

    Raises:
        ValueError: If format_type is not recognized

    Example:
        >>> formatter = get_formatter('json')
        >>> output = formatter.format(data)
    """
    # Lazy import to avoid circular dependencies at module level
    from nhl_scrabble.formatters.factory import (  # noqa: PLC0415
        get_formatter as factory_get_formatter,
    )

    return factory_get_formatter(format_type, **kwargs)
