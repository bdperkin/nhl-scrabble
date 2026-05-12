# Expand Test Coverage of Final Core Modules

**GitHub Issue**: [#589](https://github.com/bdperkin/nhl-scrabble/issues/589)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

18-24 hours

## Description

Critical application modules have **zero test coverage despite having test files**, leaving core functionality completely untested. Current coverage for these modules is **0.00%**, with **~713 untested statements** across 4 major subsystems:

- **config.py**: 0.00% (105 statements untested) - **Main application configuration**
- **analytics/**: 0.00% (284 statements untested across 4 files)
- **exporters/**: 0.00% (112 statements untested across 2 files)
- **formatters/**: 0.00% (212 statements untested across 11 files)

**Total missing coverage**: ~713 statements across 18 files

**Critical Finding**: Test files exist for most of these modules but have **0% coverage**, indicating tests are incomplete, not running, or not properly configured. This is a **unique situation** requiring investigation and comprehensive test implementation.

This represents critical gaps in quality assurance for:
- Application configuration and settings management
- Test analytics and code coverage analysis
- Data export functionality (Excel, CSV)
- Output formatting (10 different formats: CSV, HTML, JSON, Markdown, Table, Template, Text, XML, YAML, and analytics formatters)

## Current State

### Unusual Situation: Tests Exist But 0% Coverage

**config.py (105 statements, 0% coverage):**
- Test file exists: `tests/unit/test_config.py`
- But config.py has 0% coverage
- Suggests tests are incomplete or not running

**analytics/ (284 statements, 0% coverage):**
- Test files exist:
  - `tests/unit/test_analytics_formatters.py`
  - `tests/integration/test_test_analytics_command.py`
- All 4 files have 0% coverage
- Suggests significant test gaps

**exporters/ (112 statements, 0% coverage):**
- Test file exists: `tests/unit/test_excel_exporter.py`
- excel_exporter.py has 0% coverage (110 statements)
- Suggests tests are incomplete

**formatters/ (212 statements, 0% coverage):**
- **10 test files exist** - one for each formatter:
  - test_csv_formatter.py
  - test_html_formatter.py
  - test_json_formatter.py
  - test_markdown_formatter.py
  - test_table_formatter.py
  - test_template_formatter.py
  - test_text_formatter.py
  - test_xml_formatter.py
  - test_yaml_formatter.py
- All 10 formatters have 0% coverage
- factory.py has no dedicated test
- Suggests tests exist but are not comprehensive

### Coverage Breakdown by Module:

**config.py (105 statements, 0% coverage):**
```
Lines missing: 18-601
Features untested:
- Configuration loading from environment
- Configuration validation
- Default value handling
- Configuration merging
- Settings persistence
- Configuration schema
- Type conversion
- Configuration export
- Environment variable parsing
```

**analytics/analyzer.py (62 statements, 0% coverage):**
```
Lines missing: 3-202
Features untested:
- Test result analysis
- Coverage data processing
- Statistics calculation
- Trend analysis
- Failure pattern detection
- Performance metrics
- Report generation
```

**analytics/codecov_client.py (61 statements, 0% coverage):**
```
Lines missing: 3-201
Features untested:
- Codecov API integration
- Coverage data upload
- API authentication
- Error handling
- Retry logic
- Response parsing
```

**analytics/formatters.py (157 statements, 0% coverage):**
```
Lines missing: 3-442
Features untested:
- Analytics data formatting
- Coverage report formatting
- Test result formatting
- Statistical formatting
- Chart/graph data formatting
- Multiple output formats
```

**exporters/excel_exporter.py (110 statements, 0% coverage):**
```
Lines missing: 3-384
Features untested:
- Excel file generation
- Worksheet creation
- Cell formatting
- Data serialization
- Styling (colors, fonts, borders)
- Multiple sheets
- Formula handling
- Export validation
```

**formatters/ (212 statements, 0% coverage across 10 files):**
```
csv_formatter.py (18 statements):
- CSV generation
- Delimiter handling
- Escaping
- Header rows

html_formatter.py (28 statements):
- HTML table generation
- Styling
- Responsive design
- Accessibility

json_formatter.py (6 statements):
- JSON serialization
- Pretty printing
- Compact mode

markdown_formatter.py (31 statements):
- Markdown table generation
- Link formatting
- Code blocks

table_formatter.py (25 statements):
- ASCII table generation
- Column alignment
- Border styles

template_formatter.py (21 statements):
- Template rendering
- Variable substitution
- Template loading

text_formatter.py (35 statements):
- Plain text formatting
- Word wrapping
- Alignment
- Padding

xml_formatter.py (13 statements):
- XML generation
- Element creation
- Attribute handling

yaml_formatter.py (9 statements):
- YAML serialization
- Indentation
- Flow style

factory.py (18 statements):
- Formatter factory
- Format detection
- Formatter selection
```

## Proposed Solution

### 1. Test Coverage Expansion Strategy

#### Phase 0: Investigation (1-2 hours)
**Understand why existing tests have 0% coverage:**
1. Review existing test files
2. Identify incomplete tests
3. Check if tests are running in CI
4. Verify test configuration
5. Document findings

#### A. Configuration (Priority 1 - Foundation)

**config.py** (105 statements):
```python
# tests/unit/test_config.py (enhance existing)
class TestConfig:
    """Comprehensive configuration tests."""

    def test_config_initialization_default(self):
        """Test config initialization with defaults."""
        config = Config()
        assert config is not None
        # Verify default values

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "60")
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "5")
        config = Config.from_env()
        assert config.api_timeout == 60
        assert config.api_retries == 5

    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            Config(api_timeout=-1)  # Negative timeout
        with pytest.raises(ValidationError):
            Config(api_retries=101)  # Too many retries

    def test_config_default_values(self):
        """Test default value handling."""
        config = Config()
        assert config.api_timeout == 30  # Default
        assert config.cache_enabled is True  # Default

    def test_config_merging(self):
        """Test configuration merging."""
        config1 = Config(api_timeout=30)
        config2 = Config(api_retries=5)
        merged = config1.merge(config2)
        assert merged.api_timeout == 30
        assert merged.api_retries == 5

    def test_config_persistence(self, tmp_path):
        """Test configuration save/load."""
        config = Config(api_timeout=60)
        config_file = tmp_path / "config.json"
        config.save(config_file)
        loaded = Config.load(config_file)
        assert loaded.api_timeout == 60

    def test_config_schema(self):
        """Test configuration schema validation."""
        schema = Config.get_schema()
        assert "api_timeout" in schema
        assert schema["api_timeout"]["type"] == "integer"

    def test_config_type_conversion(self, monkeypatch):
        """Test automatic type conversion."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "60")  # String
        config = Config.from_env()
        assert isinstance(config.api_timeout, int)  # Converted to int

    def test_config_export(self):
        """Test configuration export to dict."""
        config = Config(api_timeout=60)
        exported = config.to_dict()
        assert exported["api_timeout"] == 60

    def test_environment_variable_parsing(self, monkeypatch):
        """Test environment variable name parsing."""
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "true")
        config = Config.from_env()
        assert config.verbose is True

    # Cover all 105 statements
```

#### B. Analytics (Priority 2 - Quality Assurance)

**analytics/analyzer.py** (62 statements):
```python
# tests/unit/test_analytics_analyzer.py (create new)
class TestAnalyzer:
    """Test result analyzer tests."""

    @pytest.fixture
    def sample_test_results(self):
        """Sample test results for analysis."""
        return {
            "total": 100,
            "passed": 90,
            "failed": 8,
            "skipped": 2,
            "duration": 123.45
        }

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = Analyzer()
        assert analyzer is not None

    def test_analyze_test_results(self, sample_test_results):
        """Test analysis of test results."""
        analyzer = Analyzer()
        analysis = analyzer.analyze(sample_test_results)
        assert analysis["success_rate"] == 0.90
        assert analysis["failure_rate"] == 0.08

    def test_calculate_statistics(self, sample_test_results):
        """Test statistics calculation."""
        analyzer = Analyzer()
        stats = analyzer.calculate_statistics(sample_test_results)
        assert "mean" in stats
        assert "median" in stats
        assert "std_dev" in stats

    def test_trend_analysis(self):
        """Test trend analysis over time."""
        analyzer = Analyzer()
        historical_results = [
            {"date": "2024-01-01", "passed": 80},
            {"date": "2024-01-02", "passed": 85"},
            {"date": "2024-01-03", "passed": 90"},
        ]
        trend = analyzer.analyze_trend(historical_results)
        assert trend["direction"] == "improving"

    def test_failure_pattern_detection(self):
        """Test detection of failure patterns."""
        analyzer = Analyzer()
        failures = [
            {"test": "test_a", "error": "AssertionError"},
            {"test": "test_b", "error": "AssertionError"},
            {"test": "test_c", "error": "TypeError"},
        ]
        patterns = analyzer.detect_patterns(failures)
        assert "AssertionError" in patterns
        assert patterns["AssertionError"]["count"] == 2

    def test_performance_metrics(self, sample_test_results):
        """Test performance metric calculation."""
        analyzer = Analyzer()
        metrics = analyzer.calculate_performance_metrics(sample_test_results)
        assert "avg_duration" in metrics
        assert "throughput" in metrics

    def test_report_generation(self, sample_test_results):
        """Test analysis report generation."""
        analyzer = Analyzer()
        report = analyzer.generate_report(sample_test_results)
        assert "summary" in report
        assert "details" in report

    # Cover all 62 statements
```

**analytics/codecov_client.py** (61 statements):
```python
# tests/unit/test_codecov_client.py (create new)
class TestCodecovClient:
    """Codecov API client tests."""

    @pytest.fixture
    def mock_requests(self, monkeypatch):
        """Mock requests library."""
        mock_post = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"uploaded": True}
        monkeypatch.setattr("requests.post", mock_post)
        return mock_post

    def test_client_initialization(self):
        """Test client initialization."""
        client = CodecovClient(token="test_token")
        assert client.token == "test_token"

    def test_upload_coverage(self, mock_requests):
        """Test coverage data upload."""
        client = CodecovClient(token="test_token")
        result = client.upload_coverage(coverage_data={"lines": 100})
        assert result["uploaded"] is True
        mock_requests.assert_called_once()

    def test_authentication(self, mock_requests):
        """Test API authentication."""
        client = CodecovClient(token="test_token")
        client.upload_coverage(coverage_data={})
        # Verify token is sent in request
        call_args = mock_requests.call_args
        assert "test_token" in str(call_args)

    def test_error_handling(self, monkeypatch):
        """Test error handling for failed uploads."""
        mock_post = Mock()
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Server error"
        monkeypatch.setattr("requests.post", mock_post)

        client = CodecovClient(token="test_token")
        with pytest.raises(CodecovError):
            client.upload_coverage(coverage_data={})

    def test_retry_logic(self, monkeypatch):
        """Test retry logic on transient failures."""
        attempts = []
        def mock_post_with_retry(*args, **kwargs):
            attempts.append(1)
            if len(attempts) < 3:
                response = Mock()
                response.status_code = 503
                return response
            response = Mock()
            response.status_code = 200
            response.json.return_value = {"uploaded": True}
            return response

        monkeypatch.setattr("requests.post", mock_post_with_retry)

        client = CodecovClient(token="test_token", max_retries=3)
        result = client.upload_coverage(coverage_data={})
        assert result["uploaded"] is True
        assert len(attempts) == 3

    def test_response_parsing(self, mock_requests):
        """Test response parsing."""
        mock_requests.return_value.json.return_value = {
            "uploaded": True,
            "url": "https://codecov.io/report"
        }

        client = CodecovClient(token="test_token")
        result = client.upload_coverage(coverage_data={})
        assert result["url"] == "https://codecov.io/report"

    # Cover all 61 statements
```

**analytics/formatters.py** (157 statements):
```python
# tests/unit/test_analytics_formatters.py (enhance existing)
class TestAnalyticsFormatters:
    """Analytics data formatter tests."""

    @pytest.fixture
    def sample_coverage_data(self):
        """Sample coverage data."""
        return {
            "total_statements": 1000,
            "covered_statements": 850,
            "coverage_percent": 85.0,
            "files": [...]
        }

    def test_format_coverage_report(self, sample_coverage_data):
        """Test coverage report formatting."""
        formatter = AnalyticsFormatter()
        report = formatter.format_coverage(sample_coverage_data)
        assert "85.0%" in report
        assert "Total: 1000" in report

    def test_format_test_results(self):
        """Test result formatting."""
        formatter = AnalyticsFormatter()
        results = {"passed": 90, "failed": 10, "total": 100}
        formatted = formatter.format_test_results(results)
        assert "90%" in formatted  # Success rate

    def test_format_statistics(self):
        """Test statistical formatting."""
        formatter = AnalyticsFormatter()
        stats = {"mean": 85.5, "median": 87.0, "std_dev": 5.2}
        formatted = formatter.format_statistics(stats)
        # Verify proper number formatting

    def test_format_chart_data(self):
        """Test chart/graph data formatting."""
        formatter = AnalyticsFormatter()
        data = [
            {"date": "2024-01-01", "coverage": 80},
            {"date": "2024-01-02", "coverage": 85},
        ]
        chart_data = formatter.format_for_chart(data)
        assert "labels" in chart_data
        assert "values" in chart_data

    def test_multiple_output_formats(self, sample_coverage_data):
        """Test multiple output format support."""
        formatter = AnalyticsFormatter()

        text = formatter.format_coverage(sample_coverage_data, format="text")
        json_data = formatter.format_coverage(sample_coverage_data, format="json")
        html = formatter.format_coverage(sample_coverage_data, format="html")

        assert isinstance(text, str)
        assert isinstance(json_data, dict)
        assert "<table>" in html

    # Cover all 157 statements
```

#### C. Exporters (Priority 2 - Data Export)

**exporters/excel_exporter.py** (110 statements):
```python
# tests/unit/test_excel_exporter.py (enhance existing)
class TestExcelExporter:
    """Excel export functionality tests."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for export."""
        return [
            {"name": "Player 1", "team": "WSH", "score": 42},
            {"name": "Player 2", "team": "PIT", "score": 38},
        ]

    def test_excel_file_generation(self, sample_data, tmp_path):
        """Test Excel file generation."""
        exporter = ExcelExporter()
        output_file = tmp_path / "output.xlsx"
        exporter.export(sample_data, output_file)
        assert output_file.exists()

    def test_worksheet_creation(self, sample_data, tmp_path):
        """Test multiple worksheet creation."""
        exporter = ExcelExporter()
        output_file = tmp_path / "output.xlsx"
        exporter.export({
            "Players": sample_data,
            "Teams": [...]
        }, output_file)
        # Verify multiple sheets created

    def test_cell_formatting(self, sample_data, tmp_path):
        """Test cell formatting (numbers, dates, text)."""
        exporter = ExcelExporter()
        output_file = tmp_path / "output.xlsx"
        exporter.export(sample_data, output_file)
        # Verify cell types are correct

    def test_data_serialization(self, tmp_path):
        """Test data type serialization."""
        exporter = ExcelExporter()
        data = [
            {"int": 42, "float": 3.14, "bool": True, "date": datetime.now()}
        ]
        output_file = tmp_path / "output.xlsx"
        exporter.export(data, output_file)
        # Verify types preserved

    def test_styling(self, sample_data, tmp_path):
        """Test styling (colors, fonts, borders)."""
        exporter = ExcelExporter()
        output_file = tmp_path / "output.xlsx"
        exporter.export(sample_data, output_file, style={
            "header": {"bold": True, "bg_color": "#4472C4"},
            "data": {"font_size": 11}
        })
        # Verify styles applied

    def test_multiple_sheets(self, tmp_path):
        """Test multiple sheet handling."""
        exporter = ExcelExporter()
        output_file = tmp_path / "output.xlsx"
        exporter.export({
            "Sheet1": [...],
            "Sheet2": [...],
            "Sheet3": [...]
        }, output_file)
        # Verify all sheets created

    def test_formula_handling(self, sample_data, tmp_path):
        """Test formula insertion."""
        exporter = ExcelExporter()
        data = [
            {"value1": 10, "value2": 20, "sum": "=A2+B2"}
        ]
        output_file = tmp_path / "output.xlsx"
        exporter.export(data, output_file)
        # Verify formulas work

    def test_export_validation(self, sample_data, tmp_path):
        """Test export data validation."""
        exporter = ExcelExporter()
        with pytest.raises(ValueError):
            exporter.export(None, tmp_path / "output.xlsx")  # None data
        with pytest.raises(ValueError):
            exporter.export([], tmp_path / "output.xlsx")  # Empty data

    # Cover all 110 statements
```

#### D. Formatters (Priority 3 - Output Formats)

**All 10 formatters** (212 statements total):
```python
# Enhance all 10 existing test files

# tests/unit/formatters/test_csv_formatter.py
class TestCSVFormatter:
    def test_csv_generation(self, sample_data):
        """Test CSV string generation."""
        formatter = CSVFormatter()
        csv = formatter.format(sample_data)
        assert "name,team,score" in csv  # Header

    def test_delimiter_handling(self, sample_data):
        """Test custom delimiter."""
        formatter = CSVFormatter(delimiter=";")
        csv = formatter.format(sample_data)
        assert ";" in csv

    def test_escaping(self):
        """Test special character escaping."""
        formatter = CSVFormatter()
        data = [{"field": 'value with "quotes"'}]
        csv = formatter.format(data)
        assert '""' in csv  # Escaped quotes

    # Cover all 18 statements

# tests/unit/formatters/test_html_formatter.py
class TestHTMLFormatter:
    def test_html_table_generation(self, sample_data):
        """Test HTML table generation."""
        formatter = HTMLFormatter()
        html = formatter.format(sample_data)
        assert "<table>" in html
        assert "<th>name</th>" in html

    def test_styling(self, sample_data):
        """Test CSS styling."""
        formatter = HTMLFormatter(style="bootstrap")
        html = formatter.format(sample_data)
        assert "class=" in html

    def test_responsive_design(self, sample_data):
        """Test responsive table."""
        formatter = HTMLFormatter(responsive=True)
        html = formatter.format(sample_data)
        assert "responsive" in html

    def test_accessibility(self, sample_data):
        """Test ARIA attributes."""
        formatter = HTMLFormatter()
        html = formatter.format(sample_data)
        assert "role=" in html or "aria-" in html

    # Cover all 28 statements

# tests/unit/formatters/test_json_formatter.py
class TestJSONFormatter:
    def test_json_serialization(self, sample_data):
        """Test JSON serialization."""
        formatter = JSONFormatter()
        json_str = formatter.format(sample_data)
        data = json.loads(json_str)
        assert len(data) == len(sample_data)

    def test_pretty_printing(self, sample_data):
        """Test pretty printed JSON."""
        formatter = JSONFormatter(indent=2)
        json_str = formatter.format(sample_data)
        assert "  " in json_str  # Indentation

    def test_compact_mode(self, sample_data):
        """Test compact JSON (no whitespace)."""
        formatter = JSONFormatter(compact=True)
        json_str = formatter.format(sample_data)
        assert "\n" not in json_str

    # Cover all 6 statements

# Similar patterns for other 7 formatters:
# - test_markdown_formatter.py (31 statements)
# - test_table_formatter.py (25 statements)
# - test_template_formatter.py (21 statements)
# - test_text_formatter.py (35 statements)
# - test_xml_formatter.py (13 statements)
# - test_yaml_formatter.py (9 statements)

# tests/unit/formatters/test_factory.py (create new)
class TestFormatterFactory:
    """Test formatter factory."""

    def test_create_formatter_by_name(self):
        """Test creating formatter by name."""
        formatter = FormatterFactory.create("csv")
        assert isinstance(formatter, CSVFormatter)

    def test_format_detection(self):
        """Test automatic format detection."""
        formatter = FormatterFactory.detect_format("output.json")
        assert isinstance(formatter, JSONFormatter)

    def test_formatter_selection(self, sample_data):
        """Test formatter selection logic."""
        formatter = FormatterFactory.select(sample_data, output_type="html")
        assert isinstance(formatter, HTMLFormatter)

    # Cover all 18 statements
```

### 2. Test Organization

```
tests/
├── unit/
│   ├── test_config.py                         ✓ enhance (105 statements)
│   ├── test_analytics_analyzer.py             + create (62 statements)
│   ├── test_codecov_client.py                 + create (61 statements)
│   ├── test_analytics_formatters.py           ✓ enhance (157 statements)
│   ├── test_excel_exporter.py                 ✓ enhance (110 statements)
│   └── formatters/
│       ├── test_csv_formatter.py              ✓ enhance (18 statements)
│       ├── test_html_formatter.py             ✓ enhance (28 statements)
│       ├── test_json_formatter.py             ✓ enhance (6 statements)
│       ├── test_markdown_formatter.py         ✓ enhance (31 statements)
│       ├── test_table_formatter.py            ✓ enhance (25 statements)
│       ├── test_template_formatter.py         ✓ enhance (21 statements)
│       ├── test_text_formatter.py             ✓ enhance (35 statements)
│       ├── test_xml_formatter.py              ✓ enhance (13 statements)
│       ├── test_yaml_formatter.py             ✓ enhance (9 statements)
│       └── test_factory.py                    + create (18 statements)
└── integration/
    ├── test_config_integration.py             + create
    ├── test_analytics_workflow.py             + create
    └── test_export_workflow.py                + create
```

## Implementation Steps

1. **Phase 0: Investigation** (1-2 hours)
   - Review all existing test files
   - Understand why coverage is 0%
   - Document findings
   - Create investigation report

2. **Phase 1: Configuration** (4-6 hours)
   - Enhance tests/unit/test_config.py (105 statements)
   - Foundation module - critical

3. **Phase 2: Analytics** (6-8 hours)
   - Create tests/unit/test_analytics_analyzer.py (62 statements)
   - Create tests/unit/test_codecov_client.py (61 statements)
   - Enhance tests/unit/test_analytics_formatters.py (157 statements)
   - Quality assurance modules

4. **Phase 3: Exporters** (3-4 hours)
   - Enhance tests/unit/test_excel_exporter.py (110 statements)
   - Data export functionality

5. **Phase 4: Formatters** (4-6 hours)
   - Enhance all 10 formatter test files (212 statements total)
   - Create tests/unit/formatters/test_factory.py (18 statements)
   - Output formatting

6. **Phase 5: Integration Testing** (2-3 hours)
   - Create integration test suites
   - Test workflows

7. **Phase 6: Documentation** (2 hours)
   - Update test documentation
   - CI configuration

## Testing Strategy

### Investigation Phase
- **Review existing tests** to understand 0% coverage
- Check test execution
- Verify test configuration
- Document incomplete tests

### Unit Tests
- Test each module in isolation
- Mock external dependencies
- Test all code paths
- Use parametrize for multiple formats

### Integration Tests
- Test configuration loading workflow
- Test analytics end-to-end
- Test export workflows
- Verify formatter integration

## Acceptance Criteria

- [ ] Investigation complete - understand why tests had 0% coverage
- [ ] **config.py** coverage: 0% → 95%+
- [ ] **analytics/analyzer.py** coverage: 0% → 95%+
- [ ] **analytics/codecov_client.py** coverage: 0% → 95%+
- [ ] **analytics/formatters.py** coverage: 0% → 95%+
- [ ] **exporters/excel_exporter.py** coverage: 0% → 95%+
- [ ] **All 10 formatters** coverage: 0% → 95%+
- [ ] **formatters/factory.py** coverage: 0% → 95%+
- [ ] All new/enhanced tests pass in CI (all platforms)
- [ ] All tests pass with Python 3.12-3.15-dev
- [ ] No test flakiness
- [ ] Overall project coverage increases
- [ ] diff-cover shows 100% coverage
- [ ] All tests have comprehensive docstrings
- [ ] Documentation updated

## Related Files

### Source Files:
- `src/nhl_scrabble/config.py` - Application configuration (105 statements)
- `src/nhl_scrabble/analytics/analyzer.py` - Test analysis (62 statements)
- `src/nhl_scrabble/analytics/codecov_client.py` - Codecov integration (61 statements)
- `src/nhl_scrabble/analytics/formatters.py` - Analytics formatting (157 statements)
- `src/nhl_scrabble/exporters/excel_exporter.py` - Excel export (110 statements)
- `src/nhl_scrabble/formatters/` - 10 formatters + factory (212 statements)

### Test Files:
- All test files exist but need enhancement/completion

## Dependencies

- **Complements Tasks 033, 034, 035**: This is the final test coverage task
- Should be completed after or alongside other test coverage tasks
- No blocking dependencies

## Additional Notes

### Unique Situation

This task is unique because **test files already exist** for most modules but have **0% coverage**. This suggests:
1. Tests are incomplete or stubs
2. Tests aren't running properly
3. Tests aren't configured correctly
4. Investigation phase is critical

### Why This Matters

1. **Configuration Critical**: Main config.py is foundation of application
2. **Quality Assurance**: Analytics modules ensure test quality
3. **Data Export**: Excel export is key functionality
4. **Output Formats**: 10 formatters support multiple output types

### Combined Impact (All 4 Tasks)

**Task 033** (#586):
- Infrastructure: ~445 statements
- 16-24 hours

**Task 034** (#587):
- Application: ~642 statements
- 24-32 hours

**Task 035** (#588):
- Business Logic: ~576 statements
- 20-28 hours
- **HIGH priority**

**Task 036** (this):
- Final Modules: ~713 statements
- 18-24 hours

**Total**:
- **~2,376 untested statements**
- **78-108 hours** total effort
- **Coverage target: 90.21% → 97%+** (estimated)
- **Complete test coverage** of entire application

## Implementation Notes

*To be filled during implementation:*
- Investigation findings (why 0% coverage despite tests existing)
- Test completion requirements
- Configuration issues discovered
- Actual effort vs estimated
- Coverage improvements achieved
