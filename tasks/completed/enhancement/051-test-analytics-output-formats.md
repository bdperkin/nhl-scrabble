# Extend test-analytics Output Formats

**GitHub Issue**: #601 - https://github.com/bdperkin/nhl-scrabble/issues/601

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

8-12 hours

## Description

Extend the `nhl-scrabble test-analytics` command to support additional output formats beyond the current text, json, and html options. Add support for yaml, xml, table, markdown, csv, excel, and template formats to provide users with more flexibility in how they consume and integrate test analytics data.

## Current State

The test-analytics command currently supports 3 output formats:

```python
# src/nhl_scrabble/cli.py
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "html"], case_sensitive=False),
    default="text",
    help=_("Output format (default: text)"),
)
def test_analytics(...):
    # Format output
    formatter: JSONFormatter | HTMLFormatter | TextFormatter
    if output_format == "json":
        formatter = JSONFormatter()
        output_text = formatter.format(report_data)
    elif output_format == "html":
        formatter = HTMLFormatter()
        output_text = formatter.format(report_data)
    else:
        formatter = TextFormatter()
        output_text = formatter.format(report_data)
```

**Existing Formatters** in `src/nhl_scrabble/analytics/formatters.py`:

1. **TextFormatter** - Rich terminal output with tables and panels
2. **JSONFormatter** - JSON serialization of analytics data
3. **HTMLFormatter** - Full HTML report with embedded CSS

Each formatter has a `format(data: dict[str, Any]) -> str` method that processes:
- `coverage_gaps` - List of CoverageGap instances
- `slow_tests` - List of TestPerformance instances
- `flaky_tests` - List of TestPerformance instances
- `coverage_trend` - Trend status string
- `coverage_history` - Historical coverage data

## Proposed Solution

Add 7 new formatter classes to `src/nhl_scrabble/analytics/formatters.py` and update the CLI to support them:

### 1. YAMLFormatter

Output analytics data in YAML format for configuration files and human-readable structured data:

```python
class YAMLFormatter:
    """Format analytics data as YAML.

    Example output:
        coverage_gaps:
          - module: src/nhl_scrabble/api/nhl_client.py
            current_coverage: 85.5
            target_coverage: 90.0
            lines_needed: 12
            priority: high
    """

    def format(self, data: dict[str, Any]) -> str:
        import yaml

        serializable_data = self._convert_to_dict(data)
        return yaml.dump(serializable_data, default_flow_style=False, sort_keys=False)
```

**Dependencies**: Add `PyYAML>=6.0.1` to `pyproject.toml`

### 2. XMLFormatter

Output analytics data in XML format for enterprise systems and legacy integrations:

```python
class XMLFormatter:
    """Format analytics data as XML.

    Example output:
        <?xml version="1.0" encoding="UTF-8"?>
        <test_analytics>
          <coverage_gaps>
            <gap>
              <module>src/nhl_scrabble/api/nhl_client.py</module>
              <current_coverage>85.5</current_coverage>
              <target_coverage>90.0</target_coverage>
              <lines_needed>12</lines_needed>
              <priority>high</priority>
            </gap>
          </coverage_gaps>
        </test_analytics>
    """

    def format(self, data: dict[str, Any]) -> str:
        import xml.etree.ElementTree as ET

        root = ET.Element("test_analytics")

        # Add coverage gaps
        if "coverage_gaps" in data:
            gaps_elem = ET.SubElement(root, "coverage_gaps")
            for gap in data["coverage_gaps"]:
                gap_elem = ET.SubElement(gaps_elem, "gap")
                ET.SubElement(gap_elem, "module").text = gap.module
                # ... add other fields

        return ET.tostring(root, encoding="unicode", method="xml")
```

**Dependencies**: Uses stdlib `xml.etree.ElementTree` (no new dependencies)

### 3. TableFormatter

Output analytics data in simple ASCII table format (simpler than Rich text output):

```python
class TableFormatter:
    """Format analytics data as simple ASCII tables.

    Example output:
        Coverage Gaps
        +-----------------+----------+----------+--------------+----------+
        | Module          | Current  | Target   | Lines Needed | Priority |
        +-----------------+----------+----------+--------------+----------+
        | api/nhl_client  | 85.5%    | 90.0%    | 12           | HIGH     |
        +-----------------+----------+----------+--------------+----------+
    """

    def format(self, data: dict[str, Any]) -> str:
        from tabulate import tabulate

        output = []

        # Coverage gaps table
        if "coverage_gaps" in data:
            headers = ["Module", "Current", "Target", "Lines Needed", "Priority"]
            rows = [[gap.module, f"{gap.current_coverage:.1f}%", ...]
                    for gap in data["coverage_gaps"][:20]]
            output.append("Coverage Gaps\n")
            output.append(tabulate(rows, headers=headers, tablefmt="grid"))

        return "\n\n".join(output)
```

**Dependencies**: Add `tabulate>=0.9.0` to `pyproject.toml`

### 4. MarkdownFormatter

Output analytics data in Markdown format for documentation and GitHub:

```python
class MarkdownFormatter:
    """Format analytics data as Markdown.

    Example output:
        # Test Analytics Report

        ## Coverage Gaps

        | Module | Current | Target | Lines Needed | Priority |
        |--------|---------|--------|--------------|----------|
        | api/nhl_client | 85.5% | 90.0% | 12 | HIGH |
    """

    def format(self, data: dict[str, Any]) -> str:
        output = ["# Test Analytics Report\n"]

        # Coverage gaps
        if "coverage_gaps" in data:
            output.append("## Coverage Gaps\n")
            output.append("| Module | Current | Target | Lines Needed | Priority |")
            output.append("|--------|---------|--------|--------------|----------|")
            for gap in data["coverage_gaps"][:20]:
                output.append(f"| {gap.module} | {gap.current_coverage:.1f}% | ...")

        return "\n".join(output)
```

**Dependencies**: None (pure Python string formatting)

### 5. CSVFormatter

Output analytics data in CSV format for spreadsheet import and data analysis:

```python
class CSVFormatter:
    """Format analytics data as CSV.

    Example output:
        section,test_name,module,current_coverage,target_coverage,lines_needed,priority,avg_duration,max_duration,failure_rate,flakiness_score
        coverage_gaps,,,85.5,90.0,12,high,,,
        slow_tests,test_api_fetch,,,,,,2.45,3.21,0.05,0.123
    """

    def format(self, data: dict[str, Any]) -> str:
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "section", "test_name", "module", "current_coverage",
            "target_coverage", "lines_needed", "priority",
            "avg_duration", "max_duration", "failure_rate", "flakiness_score"
        ])

        # Write coverage gaps
        if "coverage_gaps" in data:
            for gap in data["coverage_gaps"]:
                writer.writerow([
                    "coverage_gaps", "", gap.module, gap.current_coverage,
                    gap.target_coverage, gap.lines_needed, gap.priority,
                    "", "", "", ""
                ])

        # Write slow tests
        if "slow_tests" in data:
            for test in data["slow_tests"]:
                writer.writerow([
                    "slow_tests", test.test_name, "", "", "", "", "",
                    test.avg_duration, test.max_duration, test.failure_rate,
                    test.flakiness_score
                ])

        return output.getvalue()
```

**Dependencies**: Uses stdlib `csv` (no new dependencies)

### 6. ExcelFormatter

Output analytics data in Excel format for business reporting:

```python
class ExcelFormatter:
    """Format analytics data as Excel workbook.

    Creates a multi-sheet Excel workbook with:
    - Sheet 1: Coverage Gaps
    - Sheet 2: Slow Tests
    - Sheet 3: Flaky Tests
    - Sheet 4: Coverage Trends

    Note: Returns binary data, must be written in binary mode.
    """

    def format(self, data: dict[str, Any]) -> bytes:
        from io import BytesIO
        import openpyxl
        from openpyxl.styles import Font, PatternFill

        wb = openpyxl.Workbook()

        # Coverage Gaps sheet
        if "coverage_gaps" in data:
            ws = wb.active
            ws.title = "Coverage Gaps"
            ws.append(["Module", "Current", "Target", "Lines Needed", "Priority"])

            # Style header
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="4CAF50", fill_type="solid")

            # Add data
            for gap in data["coverage_gaps"]:
                ws.append([
                    gap.module,
                    gap.current_coverage,
                    gap.target_coverage,
                    gap.lines_needed,
                    gap.priority.upper()
                ])

        # Save to bytes
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
```

**Dependencies**: Add `openpyxl>=3.1.0` to `pyproject.toml`

**Note**: Excel format returns `bytes` instead of `str`, requires special handling in CLI

### 7. TemplateFormatter

Output analytics data using Jinja2 templates for custom formats:

```python
class TemplateFormatter:
    """Format analytics data using custom Jinja2 template.

    Users can provide a template file path via environment variable
    NHL_SCRABBLE_ANALYTICS_TEMPLATE or --template option.

    Example template:
        # Test Analytics - {{ timestamp }}

        {% if coverage_gaps %}
        ## Coverage Gaps ({{ coverage_gaps|length }} modules)
        {% for gap in coverage_gaps[:10] %}
        - {{ gap.module }}: {{ gap.current_coverage }}% → {{ gap.target_coverage }}%
        {% endfor %}
        {% endif %}
    """

    def __init__(self, template_path: str | None = None) -> None:
        self.template_path = template_path or os.getenv(
            "NHL_SCRABBLE_ANALYTICS_TEMPLATE"
        )

    def format(self, data: dict[str, Any]) -> str:
        from jinja2 import Environment, FileSystemLoader, Template
        from datetime import datetime

        if not self.template_path:
            raise ValueError(
                "Template path required. Set NHL_SCRABBLE_ANALYTICS_TEMPLATE "
                "or use --template option."
            )

        template_path = Path(self.template_path)
        env = Environment(loader=FileSystemLoader(template_path.parent))
        template = env.get_template(template_path.name)

        # Add timestamp to data
        render_data = {**data, "timestamp": datetime.now().isoformat()}

        return template.render(**render_data)
```

**Dependencies**: Add `Jinja2>=3.1.0` to `pyproject.toml`

**CLI Enhancement**: Add `--template` option for template format

### CLI Updates

Update `src/nhl_scrabble/cli.py`:

```python
@click.option(
    "--format",
    "output_format",
    type=click.Choice(
        ["text", "json", "yaml", "xml", "html", "table", "markdown", "csv", "excel", "template"],
        case_sensitive=False,
    ),
    default="text",
    help=_("Output format (default: text)"),
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=_("Template file path (required for --format template)"),
)
def test_analytics(
    ctx: click.Context,
    output_format: str,
    template: str | None,
    output: str | None,
    ...
) -> None:
    # Import all formatters
    from nhl_scrabble.analytics.formatters import (
        CSVFormatter,
        ExcelFormatter,
        HTMLFormatter,
        JSONFormatter,
        MarkdownFormatter,
        TableFormatter,
        TemplateFormatter,
        TextFormatter,
        XMLFormatter,
        YAMLFormatter,
    )

    # ... fetch analytics data ...

    # Format output
    formatter_map = {
        "json": JSONFormatter(),
        "yaml": YAMLFormatter(),
        "xml": XMLFormatter(),
        "html": HTMLFormatter(),
        "table": TableFormatter(),
        "markdown": MarkdownFormatter(),
        "csv": CSVFormatter(),
        "excel": ExcelFormatter(),
        "template": TemplateFormatter(template),
        "text": TextFormatter(),
    }

    formatter = formatter_map.get(output_format, TextFormatter())
    output_data = formatter.format(report_data)

    # Write output
    if output:
        output_path = Path(output)
        if output_format == "excel":
            # Excel returns bytes, write in binary mode
            output_path.write_bytes(output_data)
        else:
            # Other formats return str, write in text mode
            output_path.write_text(output_data, encoding="utf-8")
        console.print(f"[green]✓ Report saved to {output}[/green]")
    else:
        # Display to console (skip for excel)
        if output_format == "excel":
            console.print(
                "[red]Error: Excel format requires --output option[/red]",
                style="bold",
            )
            ctx.exit(1)
        else:
            console.print(output_data)
```

## Implementation Steps

1. **Update dependencies in pyproject.toml**
   ```toml
   dependencies = [
       # ... existing dependencies ...
       "PyYAML>=6.0.1",
       "tabulate>=0.9.0",
       "openpyxl>=3.1.0",
       "Jinja2>=3.1.0",
   ]
   ```

2. **Create new formatter classes**
   - Add `YAMLFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `XMLFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `TableFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `MarkdownFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `CSVFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `ExcelFormatter` to `src/nhl_scrabble/analytics/formatters.py`
   - Add `TemplateFormatter` to `src/nhl_scrabble/analytics/formatters.py`

3. **Update CLI command**
   - Update `@click.option("--format")` choices list
   - Add `@click.option("--template")` for template format
   - Update formatter selection logic to use formatter_map
   - Add binary write handling for Excel format
   - Add validation that Excel format requires --output

4. **Add helper method for dataclass serialization**
   ```python
   def _convert_to_dict(data: dict[str, Any]) -> dict[str, Any]:
       """Convert dataclasses to dicts for serialization."""
       # Reuse logic from JSONFormatter
   ```

5. **Update type hints**
   - Update formatter union type in CLI
   - Add proper return type annotations (str vs bytes)

6. **Update i18n translations**
   - Extract new help strings
   - Update all locale .po files

7. **Update documentation**
   - Update CLI docstring examples
   - Update `docs/reference/cli.md`
   - Update `README.md` examples

## Testing Strategy

### Unit Tests

Create `tests/unit/test_analytics_formatters.py` additions:

```python
@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing."""
    return {
        "coverage_gaps": [
            CoverageGap(
                module="src/api/client.py",
                current_coverage=85.5,
                target_coverage=90.0,
                lines_needed=12,
                priority="high",
            ),
        ],
        "slow_tests": [
            TestPerformance(
                test_name="test_api_fetch",
                avg_duration=2.45,
                max_duration=3.21,
                min_duration=1.89,
                failure_rate=0.05,
                flakiness_score=0.123,
            ),
        ],
        "flaky_tests": [],
        "coverage_trend": "improving",
        "coverage_history": [
            {"timestamp": "2026-05-01", "coverage": 89.5},
            {"timestamp": "2026-04-01", "coverage": 87.2},
        ],
    }


class TestYAMLFormatter:
    """Test YAML formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test YAML formatting of coverage gaps."""
        formatter = YAMLFormatter()
        output = formatter.format(sample_analytics_data)

        # Parse YAML and verify structure
        import yaml
        data = yaml.safe_load(output)

        assert "coverage_gaps" in data
        assert len(data["coverage_gaps"]) == 1
        assert data["coverage_gaps"][0]["module"] == "src/api/client.py"
        assert data["coverage_gaps"][0]["priority"] == "high"

    def test_format_empty_data(self):
        """Test YAML formatting with empty data."""
        formatter = YAMLFormatter()
        output = formatter.format({})
        assert output == "{}\n"


class TestXMLFormatter:
    """Test XML formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test XML formatting of coverage gaps."""
        formatter = XMLFormatter()
        output = formatter.format(sample_analytics_data)

        # Parse XML and verify structure
        import xml.etree.ElementTree as ET
        root = ET.fromstring(output)

        assert root.tag == "test_analytics"
        gaps = root.find("coverage_gaps")
        assert gaps is not None
        assert len(gaps.findall("gap")) == 1


class TestTableFormatter:
    """Test table formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test table formatting of coverage gaps."""
        formatter = TableFormatter()
        output = formatter.format(sample_analytics_data)

        assert "Coverage Gaps" in output
        assert "src/api/client.py" in output
        assert "85.5%" in output
        assert "HIGH" in output


class TestMarkdownFormatter:
    """Test markdown formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test markdown formatting of coverage gaps."""
        formatter = MarkdownFormatter()
        output = formatter.format(sample_analytics_data)

        assert "# Test Analytics Report" in output
        assert "## Coverage Gaps" in output
        assert "| Module |" in output
        assert "src/api/client.py" in output


class TestCSVFormatter:
    """Test CSV formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test CSV formatting of coverage gaps."""
        formatter = CSVFormatter()
        output = formatter.format(sample_analytics_data)

        lines = output.strip().split("\n")

        # Check header
        assert "section" in lines[0]
        assert "module" in lines[0]

        # Check data
        assert "coverage_gaps" in lines[1]
        assert "src/api/client.py" in lines[1]


class TestExcelFormatter:
    """Test Excel formatter."""

    def test_format_coverage_gaps(self, sample_analytics_data):
        """Test Excel formatting of coverage gaps."""
        formatter = ExcelFormatter()
        output = formatter.format(sample_analytics_data)

        # Verify binary output
        assert isinstance(output, bytes)
        assert len(output) > 0

        # Parse Excel and verify structure
        from io import BytesIO
        import openpyxl

        wb = openpyxl.load_workbook(BytesIO(output))
        assert "Coverage Gaps" in wb.sheetnames

        ws = wb["Coverage Gaps"]
        assert ws["A1"].value == "Module"
        assert ws["A2"].value == "src/api/client.py"


class TestTemplateFormatter:
    """Test template formatter."""

    def test_format_with_template(self, sample_analytics_data, tmp_path):
        """Test template formatting with custom template."""
        template_file = tmp_path / "template.j2"
        template_file.write_text(
            "Gaps: {{ coverage_gaps|length }}\n"
            "Trend: {{ coverage_trend }}"
        )

        formatter = TemplateFormatter(str(template_file))
        output = formatter.format(sample_analytics_data)

        assert "Gaps: 1" in output
        assert "Trend: improving" in output

    def test_format_without_template(self, sample_analytics_data):
        """Test template formatter requires template path."""
        formatter = TemplateFormatter()

        with pytest.raises(ValueError, match="Template path required"):
            formatter.format(sample_analytics_data)
```

### Integration Tests

Add to `tests/integration/test_test_analytics_command.py`:

```python
class TestOutputFormats:
    """Test different output formats."""

    def test_yaml_format(self, runner, mock_codecov_api, tmp_path):
        """Test YAML output format."""
        output_file = tmp_path / "analytics.yaml"
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "yaml", "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        import yaml
        data = yaml.safe_load(output_file.read_text())
        assert "coverage_gaps" in data or "slow_tests" in data

    def test_xml_format(self, runner, mock_codecov_api, tmp_path):
        """Test XML output format."""
        output_file = tmp_path / "analytics.xml"
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "xml", "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "<?xml" in output_file.read_text()

    def test_markdown_format(self, runner, mock_codecov_api, tmp_path):
        """Test Markdown output format."""
        output_file = tmp_path / "analytics.md"
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "markdown", "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "# Test Analytics Report" in content
        assert "|" in content  # Markdown table

    def test_csv_format(self, runner, mock_codecov_api, tmp_path):
        """Test CSV output format."""
        output_file = tmp_path / "analytics.csv"
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "csv", "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        import csv
        with output_file.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert "section" in rows[0]

    def test_excel_format(self, runner, mock_codecov_api, tmp_path):
        """Test Excel output format."""
        output_file = tmp_path / "analytics.xlsx"
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "excel", "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        import openpyxl
        wb = openpyxl.load_workbook(output_file)
        assert len(wb.sheetnames) > 0

    def test_excel_requires_output(self, runner, mock_codecov_api):
        """Test Excel format requires --output option."""
        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "excel"],
        )

        assert result.exit_code == 1
        assert "requires --output" in result.output.lower()

    def test_template_format(self, runner, mock_codecov_api, tmp_path):
        """Test template output format."""
        template_file = tmp_path / "template.j2"
        template_file.write_text("Coverage Trend: {{ coverage_trend }}")

        output_file = tmp_path / "analytics.txt"
        result = runner.invoke(
            cli,
            [
                "test-analytics",
                "--format", "template",
                "--template", str(template_file),
                "-o", str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Coverage Trend:" in output_file.read_text()
```

### Manual Testing

```bash
# Test each format
nhl-scrabble test-analytics --format text
nhl-scrabble test-analytics --format json -o analytics.json
nhl-scrabble test-analytics --format yaml -o analytics.yaml
nhl-scrabble test-analytics --format xml -o analytics.xml
nhl-scrabble test-analytics --format html -o analytics.html
nhl-scrabble test-analytics --format table -o analytics.txt
nhl-scrabble test-analytics --format markdown -o analytics.md
nhl-scrabble test-analytics --format csv -o analytics.csv
nhl-scrabble test-analytics --format excel -o analytics.xlsx
nhl-scrabble test-analytics --format template --template template.j2 -o analytics.txt

# Test Excel error handling
nhl-scrabble test-analytics --format excel  # Should error

# Test template error handling
nhl-scrabble test-analytics --format template  # Should error

# Verify output files
cat analytics.json | jq
cat analytics.yaml
cat analytics.xml
cat analytics.md
cat analytics.csv
libreoffice analytics.xlsx
```

## Acceptance Criteria

- [x] YAMLFormatter class implemented and tested
- [x] XMLFormatter class implemented and tested
- [x] TableFormatter class implemented and tested
- [x] MarkdownFormatter class implemented and tested
- [x] CSVFormatter class implemented and tested
- [x] ExcelFormatter class implemented and tested
- [x] TemplateFormatter class implemented and tested
- [x] CLI --format option updated with all 10 formats
- [x] CLI --template option added
- [x] Excel format requires --output validation implemented
- [x] Template format requires --template validation implemented
- [x] Binary write handling for Excel format
- [x] UTF-8 encoding for all text formats
- [x] Unit tests for all 7 new formatters (35+ new tests)
- [x] Integration tests for all formats (8+ scenarios)
- [x] All existing tests still pass
- [x] Type hints updated and mypy passes
- [x] Documentation updated (CLI docstring, docs/reference/cli.md, README.md)
- [x] i18n strings extracted and translated
- [x] All pre-commit hooks pass
- [x] Coverage maintained above 90%

## Related Files

- `src/nhl_scrabble/cli.py` - CLI command with --format and --template options
- `src/nhl_scrabble/analytics/formatters.py` - Formatter classes (add 7 new classes)
- `pyproject.toml` - Add dependencies: PyYAML, tabulate, openpyxl, Jinja2
- `tests/unit/test_analytics_formatters.py` - Add formatter unit tests
- `tests/integration/test_test_analytics_command.py` - Add integration tests
- `docs/reference/cli.md` - CLI documentation
- `README.md` - Usage examples
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - i18n translations

## Dependencies

**New Package Dependencies** (add to pyproject.toml):
```toml
"PyYAML>=6.0.1",      # YAML formatter
"tabulate>=0.9.0",    # Table formatter
"openpyxl>=3.1.0",    # Excel formatter
"Jinja2>=3.1.0",      # Template formatter
```

**Standard Library** (no new dependencies):
- `xml.etree.ElementTree` - XML formatter
- `csv` - CSV formatter

**Task Dependencies**:
- None - this is a standalone enhancement

## Additional Notes

### Performance Implications

- **YAML/JSON/XML**: Minimal overhead, similar performance
- **HTML**: Slightly more overhead due to HTML generation
- **Table**: Similar to text format, uses tabulate library
- **Markdown**: Very lightweight, pure string formatting
- **CSV**: Very fast, stdlib implementation
- **Excel**: Most overhead due to workbook creation, but acceptable for typical analytics data
- **Template**: Performance depends on template complexity

### Security Considerations

- **Template Format**: Template path must be validated to prevent path traversal
  - Use `click.Path(exists=True, dir_okay=False)` validation
  - Consider adding template directory restriction
- **XML Format**: Use stdlib ElementTree (not vulnerable to XXE by default)
- **Excel Format**: openpyxl is safe for writing, no macro execution
- **All Formatters**: Ensure proper escaping of user-controlled data

### Breaking Changes

**None** - This is a backward-compatible enhancement:
- Default format remains "text"
- Existing formats (text, json, html) unchanged
- All existing commands and options work as before

### Migration Requirements

**None** - Users can adopt new formats at their convenience

### Example Output Files

**YAML** (`analytics.yaml`):
```yaml
coverage_gaps:
  - module: src/nhl_scrabble/api/nhl_client.py
    current_coverage: 85.5
    target_coverage: 90.0
    lines_needed: 12
    priority: high
slow_tests:
  - test_name: test_api_fetch
    avg_duration: 2.45
    max_duration: 3.21
    failure_rate: 0.05
```

**Markdown** (`analytics.md`):
```markdown
# Test Analytics Report

## Coverage Gaps

| Module | Current | Target | Lines Needed | Priority |
|--------|---------|--------|--------------|----------|
| src/nhl_scrabble/api/nhl_client.py | 85.5% | 90.0% | 12 | HIGH |

## Slowest Tests

| Test | Avg Duration | Max Duration | Failure Rate |
|------|--------------|--------------|--------------|
| test_api_fetch | 2.45s | 3.21s | 5.0% |
```

**CSV** (`analytics.csv`):
```csv
section,test_name,module,current_coverage,target_coverage,lines_needed,priority,avg_duration,max_duration,failure_rate,flakiness_score
coverage_gaps,,src/nhl_scrabble/api/nhl_client.py,85.5,90.0,12,high,,,
slow_tests,test_api_fetch,,,,,,2.45,3.21,0.05,0.123
```

### Future Enhancements

This implementation provides a foundation for:
- **PDF Output**: Add PDF formatter using ReportLab
- **Custom Templates**: Template gallery or built-in templates
- **Interactive Charts**: Add chart generation to HTML/Excel formats
- **Email Integration**: Send reports via email with preferred format
- **Dashboard Integration**: Push analytics to external dashboards

## Implementation Notes

**Implemented**: 2026-05-13
**Branch**: enhancement/051-test-analytics-output-formats
**PR**: #608 - https://github.com/bdperkin/nhl-scrabble/pull/608
**Commits**: 3 commits (c8d6f3a, 2f2e5f1, 8a4b9c3)

### Actual Implementation

Followed the proposed solution closely with one significant architectural change:

#### File Size Refactoring

The initial implementation created a single 38KB `formatters.py` file containing all 10 formatter classes, which exceeded the project's 20KB file size limit enforced by the `check_file_size.sh` pre-commit hook.

**Refactored to modular structure**:
- Split `src/nhl_scrabble/analytics/formatters.py` (38KB) into 11 separate modules:
  - `formatters/__init__.py` (1.2KB) - Re-exports for backward compatibility
  - `formatters/csv_formatter.py` (2.7KB)
  - `formatters/excel_formatter.py` (4.7KB)
  - `formatters/html_formatter.py` (6.4KB)
  - `formatters/json_formatter.py` (2.3KB)
  - `formatters/markdown_formatter.py` (3.5KB)
  - `formatters/table_formatter.py` (2.9KB)
  - `formatters/template_formatter.py` (4.1KB)
  - `formatters/text_formatter.py` (6.3KB)
  - `formatters/xml_formatter.py` (2.6KB)
  - `formatters/yaml_formatter.py` (2.9KB)

- Split `tests/unit/test_analytics_formatters.py` (38KB) into 10 separate test files:
  - `test_csv_formatter.py` (2.0KB)
  - `test_excel_formatter.py` (2.7KB)
  - `test_html_formatter.py` (2.5KB)
  - `test_json_formatter.py` (2.1KB)
  - `test_markdown_formatter.py` (2.4KB)
  - `test_table_formatter.py` (2.0KB)
  - `test_template_formatter.py` (2.7KB)
  - `test_text_formatter.py` (5.7KB)
  - `test_xml_formatter.py` (2.4KB)
  - `test_yaml_formatter.py` (2.2KB)

**Benefits of refactored structure**:
- Better code organization and maintainability
- Easier to locate and modify specific formatters
- Faster IDE navigation and search
- Cleaner git history for formatter-specific changes
- All files now well under 20KB limit (largest is 6.4KB)

#### Dependencies

Added 4 new dependencies to `pyproject.toml` `export` optional dependency group:
- `PyYAML>=6.0.2` - YAML formatter
- `tabulate>=0.9.0` - Table formatter
- `openpyxl>=3.1.5` - Excel formatter
- `Jinja2>=3.1.4` - Template formatter

Used lazy imports (`import` inside methods) for all optional dependencies to avoid hard requirements.

#### Type Safety

Added type hints throughout and resolved mypy errors:
- ExcelFormatter returns `bytes` instead of `str` for binary Excel workbook
- Added `# type: ignore[attr-defined]` for formatter protocol usage in CLI
- All formatters properly typed with return type annotations

#### Security

Implemented security best practices:
- Jinja2 templates use `autoescape=select_autoescape()` to prevent XSS
- XML parsing uses stdlib ElementTree (no XXE vulnerability)
- Template path validation via Click's `Path(exists=True, dir_okay=False)`
- All user data properly escaped in formatters

### Challenges Encountered

1. **File Size Enforcement**
   - Initial commit exceeded 20KB limit for formatters.py and test file
   - Required complete refactoring into modular structure
   - Learned to check file sizes proactively during implementation

2. **Pre-commit Hook Iterations**
   - Multiple rounds of linting fixes (PLC0415, PERF401, C901, etc.)
   - Added noqa comments with justifications for unavoidable complexity
   - Bash script linting required modernizing test syntax and quoting

3. **Git Workflow**
   - Remote contained work not in local branch
   - Required `git pull --rebase` to resolve
   - Learned to check remote state before pushing

4. **Type Checking**
   - Formatter protocol inference issues in mypy
   - Resolved with targeted `# type: ignore[attr-defined]` comments
   - Maintained strict type checking elsewhere

### Deviations from Plan

**Minor deviations**:

1. **Module Structure**: Refactored from single file to multi-module package
   - **Why**: File size enforcement requirement
   - **Impact**: Better than original plan, improved maintainability

2. **Dependencies in Optional Group**: Placed new dependencies in `export` optional group instead of main dependencies
   - **Why**: Avoids forcing all users to install formatting libraries they may not use
   - **Impact**: Users must `pip install nhl-scrabble[export]` to use new formats

3. **Enhanced Error Messages**: Added detailed error messages for missing dependencies
   - **Why**: Better user experience when optional deps not installed
   - **Impact**: Clearer guidance for users

### Actual vs Estimated Effort

- **Estimated**: 8-12 hours
- **Actual**: ~10 hours (within estimate)
- **Breakdown**:
  - Initial implementation: 4 hours
  - File size refactoring: 2 hours
  - Pre-commit hook fixes: 2 hours
  - Git workflow resolution: 1 hour
  - Type checking fixes: 1 hour

### Related PRs

- #608 - Main implementation

### Testing

**Unit Tests**: 54 total tests across 10 test files
- All formatters have comprehensive test coverage
- Tests for success cases, empty data, edge cases
- Excel and template format error handling tested

**Integration Tests**: 8 new integration tests
- All 10 formats tested end-to-end
- File output validation for each format
- Error cases (Excel without --output, template without --template)

**Coverage**: Maintained >90% coverage (currently 90.21%)

### Pre-Flight Validation

**Pre-commit Hooks**: All 87 hooks passing ✅
- File quality, Python quality, type checking, formatters, linters
- Bash script quality (12 hooks)
- Documentation validation

**Mypy**: All type checks passing ✅

**Pytest**: All 1,722 tests passing ✅
- Including 54 new formatter tests

**Tox**: Validation completed with disk space issues resolved

### Lessons Learned

1. **Proactive File Size Monitoring**: Check file sizes during implementation, not at commit time
2. **Modular Architecture**: Breaking large files into focused modules improves maintainability
3. **Optional Dependencies**: Use lazy imports and optional dependency groups for format-specific libraries
4. **Pre-commit Hooks**: Understand hook requirements before writing code (Bash modernization, noqa placement)
5. **Git Workflow**: Always check remote state before pushing, especially with team collaboration
