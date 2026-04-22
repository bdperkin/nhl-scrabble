"""Formatter factory for creating formatter instances.

This module provides the central registry and factory function for all output formatters. It maps
format type strings to their corresponding formatter classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nhl_scrabble.formatters import OutputFormatter


def get_formatter(format_type: str, **kwargs: Any) -> OutputFormatter:
    """Get formatter instance for specified format.

    Args:
        format_type: Format type (text, json, yaml, xml, html, table, markdown, csv, template)
        **kwargs: Additional arguments passed to formatter constructor
            - template_file (str): Path to template file (required for 'template' format)

    Returns:
        Formatter instance implementing OutputFormatter protocol

    Raises:
        ValueError: If format_type is not recognized
        ValueError: If required kwargs are missing (e.g., template_file for template format)

    Example:
        >>> formatter = get_formatter('json')
        >>> output = formatter.format(data)

        >>> formatter = get_formatter('template', template_file='custom.j2')
        >>> output = formatter.format(data)
    """
    # Lazy imports to avoid circular dependencies and reduce startup time
    from nhl_scrabble.formatters.csv_formatter import CSVFormatter
    from nhl_scrabble.formatters.html_formatter import HTMLFormatter
    from nhl_scrabble.formatters.json_formatter import JSONFormatter
    from nhl_scrabble.formatters.markdown_formatter import MarkdownFormatter
    from nhl_scrabble.formatters.table_formatter import TableFormatter
    from nhl_scrabble.formatters.template_formatter import TemplateFormatter
    from nhl_scrabble.formatters.text_formatter import TextFormatter
    from nhl_scrabble.formatters.xml_formatter import XMLFormatter
    from nhl_scrabble.formatters.yaml_formatter import YAMLFormatter

    # Formatter registry mapping format type to formatter class
    FORMATTERS: dict[str, type[OutputFormatter]] = {
        "text": TextFormatter,
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "xml": XMLFormatter,
        "html": HTMLFormatter,
        "table": TableFormatter,
        "markdown": MarkdownFormatter,
        "csv": CSVFormatter,
        "template": TemplateFormatter,
    }

    # Validate format type
    formatter_class = FORMATTERS.get(format_type)
    if not formatter_class:
        valid_formats = ", ".join(sorted(FORMATTERS.keys()))
        raise ValueError(f"Unknown format: {format_type}. Valid formats: {valid_formats}")

    # Create and return formatter instance
    return formatter_class(**kwargs)
