"""Tests for formatter factory."""

from __future__ import annotations

from pathlib import Path

import pytest

from nhl_scrabble.formatters import get_formatter
from nhl_scrabble.formatters.csv_formatter import CSVFormatter
from nhl_scrabble.formatters.html_formatter import HTMLFormatter
from nhl_scrabble.formatters.json_formatter import JSONFormatter
from nhl_scrabble.formatters.markdown_formatter import MarkdownFormatter
from nhl_scrabble.formatters.table_formatter import TableFormatter
from nhl_scrabble.formatters.template_formatter import TemplateFormatter
from nhl_scrabble.formatters.text_formatter import TextFormatter
from nhl_scrabble.formatters.xml_formatter import XMLFormatter
from nhl_scrabble.formatters.yaml_formatter import YAMLFormatter


def test_get_formatter_text() -> None:
    """Test factory returns TextFormatter."""
    formatter = get_formatter("text")
    assert isinstance(formatter, TextFormatter)


def test_get_formatter_json() -> None:
    """Test factory returns JSONFormatter."""
    formatter = get_formatter("json")
    assert isinstance(formatter, JSONFormatter)


def test_get_formatter_yaml() -> None:
    """Test factory returns YAMLFormatter."""
    formatter = get_formatter("yaml")
    assert isinstance(formatter, YAMLFormatter)


def test_get_formatter_xml() -> None:
    """Test factory returns XMLFormatter."""
    formatter = get_formatter("xml")
    assert isinstance(formatter, XMLFormatter)


def test_get_formatter_html() -> None:
    """Test factory returns HTMLFormatter."""
    formatter = get_formatter("html")
    assert isinstance(formatter, HTMLFormatter)


def test_get_formatter_table() -> None:
    """Test factory returns TableFormatter."""
    formatter = get_formatter("table")
    assert isinstance(formatter, TableFormatter)


def test_get_formatter_markdown() -> None:
    """Test factory returns MarkdownFormatter."""
    formatter = get_formatter("markdown")
    assert isinstance(formatter, MarkdownFormatter)


def test_get_formatter_csv() -> None:
    """Test factory returns CSVFormatter."""
    formatter = get_formatter("csv")
    assert isinstance(formatter, CSVFormatter)


def test_get_formatter_template(tmp_path: Path) -> None:
    """Test factory returns TemplateFormatter with template file."""
    template_file = tmp_path / "test.j2"
    template_file.write_text("test")

    formatter = get_formatter("template", template_file=str(template_file))
    assert isinstance(formatter, TemplateFormatter)


def test_get_formatter_unknown() -> None:
    """Test factory raises ValueError for unknown format."""
    with pytest.raises(ValueError, match="Unknown format"):
        get_formatter("unknown")


def test_get_formatter_with_kwargs(tmp_path: Path) -> None:
    """Test factory passes kwargs to formatter."""
    template_file = tmp_path / "test.j2"
    template_file.write_text("test")

    # Should not raise error when template_file is provided
    formatter = get_formatter("template", template_file=str(template_file))
    assert isinstance(formatter, TemplateFormatter)
